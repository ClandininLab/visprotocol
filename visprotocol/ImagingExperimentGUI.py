#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 10:51:42 2018

@author: mhturner
"""
import sys
from PyQt5.QtWidgets import (QPushButton, QWidget, QLabel, QTextEdit, QGridLayout, QApplication,
                             QComboBox, QLineEdit, QFormLayout, QDialog, QFileDialog, QInputDialog,
                             QMessageBox, QCheckBox, QSpinBox, QTabWidget, QVBoxLayout, QFrame)
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
from datetime import datetime
import os

from visprotocol import client
from visprotocol import protocol
from visprotocol import data
from visprotocol import control

# TODO: handle params that are meant to be strings
# TODO: save/load parameter sets

class ImagingExperimentGUI(QWidget):
    
    def __init__(self):
        super().__init__()
        self.noteText = ''
        self.run_parameter_input = {}
        self.protocol_parameter_input = {}
        self.ignoreWarnings = False

        user_names = ['mht']
        user_name, ok = QInputDialog.getItem(self, "select user", 
                                             "Available users", user_names, 0, False)

        # get a client
        self.client = getattr(client, user_name + '_client').Client()
        # get a data object
        self.data = getattr(data, user_name + '_data').Data()
        # get a protocol, just start with the base class until user selects one
        self.protocol_object = getattr(protocol, user_name + '_protocol').BaseProtocol()
        # get available protocol classes
        self.available_protocols = getattr(protocol, user_name + '_protocol').BaseProtocol.__subclasses__()
        # get an epoch run control object
        self.epoch_run = control.EpochRun()

        self.initUI()

    def initUI(self):  
        self.layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        
        self.tab1 = QWidget()
        self.grid1 = QGridLayout()
        self.grid1.setSpacing(10)
        
        self.tab2 = QWidget()
        self.grid2 = QFormLayout()
        self.grid2.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.grid2.setLabelAlignment(QtCore.Qt.AlignCenter)

        self.tabs.addTab(self.tab1,"Main")
        self.tabs.addTab(self.tab2,"Expt. Data")
        
        self.tabs.resize(450, 500) 
        
        # # # TAB 1: Main controls, for selecting / playing stimuli
        # Protocol ID drop-down:
        comboBox = QComboBox(self)
        comboBox.addItem("(select a protocol to run)")
        for sub_class in self.available_protocols:
            comboBox.addItem(sub_class.__name__)
        protocol_label = QLabel('Protocol:')
        comboBox.activated[str].connect(self.onSelectedProtocolID)
        self.grid1.addWidget(protocol_label, 1, 0)
        self.grid1.addWidget(comboBox, 1, 1, 1, 1)
        
        # Run paramters input:
        self.updateRunParamtersInput()

        # View button:
        viewButton = QPushButton("View", self)
        viewButton.clicked.connect(self.onPressedButton) 
        self.grid1.addWidget(viewButton, self.run_params_ct+3, 0)
        
        # Record button:
        recordButton = QPushButton("Record", self)
        recordButton.clicked.connect(self.onPressedButton) 
        self.grid1.addWidget(recordButton, self.run_params_ct+3, 1)
        
        # Stop button:
        stopButton = QPushButton("Stop", self)
        stopButton.clicked.connect(self.onPressedButton) 
        self.grid1.addWidget(stopButton, self.run_params_ct+3, 2)
        
        # Enter note button:
        noteButton = QPushButton("Enter note", self)
        noteButton.clicked.connect(self.onPressedButton) 
        self.grid1.addWidget(noteButton, self.run_params_ct+4, 0)

        # Notes field:
        self.notesEdit = QTextEdit()
        self.grid1.addWidget(self.notesEdit, self.run_params_ct+4, 1, 1, 2)
        
        
        # Status window:
        newLabel = QLabel('Status:')
        self.grid1.addWidget(newLabel, 2, 2)
        self.status_label = QLabel()
        self.status_label.setFrameShadow(QFrame.Shadow(1))
        self.grid1.addWidget(self.status_label, 3, 2)
        self.status_label.setText('')

        # Current imaging series counter
        newLabel = QLabel('series counter:')
        self.grid1.addWidget(newLabel, self.run_params_ct , 2)
        self.series_counter_input = QSpinBox()
        self.series_counter_input.setMinimum(1)
        self.series_counter_input.setMaximum(1000)
        self.series_counter_input.setValue(1)
        self.series_counter_input.valueChanged.connect(self.onEnteredSeriesCount)
        self.grid1.addWidget(self.series_counter_input, self.run_params_ct+1, 2)
        
        
        # # # TAB 2: Data file and fly metadata information
        # Data file info
        # Initialize new experiment button
        initializeButton = QPushButton("Initialize experiment", self)
        initializeButton.clicked.connect(self.onPressedButton) 
        newLabel = QLabel('Current data file:')
        self.grid2.addRow(initializeButton, newLabel)
        # Load existing experiment button
        loadButton = QPushButton("Load experiment", self)
        loadButton.clicked.connect(self.onPressedButton) 
        # Label with current expt file
        self.currentExperimentLabel = QLabel('')
        self.grid2.addRow(loadButton, self.currentExperimentLabel)
        
        new_separator_line = QFrame()
        new_separator_line.setFrameShape(new_separator_line.HLine)
        self.grid2.addRow(new_separator_line)

        # # Fly info:
        newLabel = QLabel('Current fly info:')
        newLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.grid2.addRow(newLabel)
        
        # Fly ID:
        newLabel = QLabel('Fly ID:')
        self.fly_id_input = QLineEdit()
        self.grid2.addRow(newLabel, self.fly_id_input)
        # Sex:
        newLabel = QLabel('Sex:')
        self.fly_sex_input = QComboBox()
        self.fly_sex_input.addItems(['Female','Male'])
        self.grid2.addRow(newLabel, self.fly_sex_input)
        # Age:
        newLabel = QLabel('Age:')
        self.fly_age_input = QSpinBox()
        self.fly_age_input.setMinimum(0)
        self.fly_age_input.setValue(1)
        self.grid2.addRow(newLabel, self.fly_age_input)
        # Prep ID:
        newLabel = QLabel('Prep:')
        self.fly_prep_input = QComboBox()
        self.fly_prep_input.addItem("")
        for prepID in self.data.prepChoices:
            self.fly_prep_input.addItem(prepID)
        self.grid2.addRow(newLabel, self.fly_prep_input)
        # Driver1:
        newLabel = QLabel('Driver_1:')
        self.fly_driver_1 = QComboBox()
        self.fly_driver_1.addItem("")
        for prepID in self.data.driverChoices:
            self.fly_driver_1.addItem(prepID)
        self.grid2.addRow(newLabel, self.fly_driver_1)
        # Indicator1:
        newLabel = QLabel('Indicator_1:')
        self.fly_indicator_1 = QComboBox()
        self.fly_indicator_1.addItem("")
        for prepID in self.data.indicatorChoices:
            self.fly_indicator_1.addItem(prepID)
        self.grid2.addRow(newLabel, self.fly_indicator_1)
        # Driver2:
        newLabel = QLabel('Driver_2:')
        self.fly_driver_2 = QComboBox()
        self.fly_driver_2.addItem("")
        for prepID in self.data.driverChoices:
            self.fly_driver_2.addItem(prepID)
        self.grid2.addRow(newLabel, self.fly_driver_2)
        # Indicator2:
        newLabel = QLabel('Indicator_2:')
        self.fly_indicator_2 = QComboBox()
        self.fly_indicator_2.addItem("")
        for prepID in self.data.indicatorChoices:
            self.fly_indicator_2.addItem(prepID)
        self.grid2.addRow(newLabel, self.fly_indicator_2)
        # Fly genotype:
        newLabel = QLabel('Genotype:')
        self.fly_genotype_input = QLineEdit()
        self.grid2.addRow(newLabel, self.fly_genotype_input)

        self.layout.addWidget(self.tabs)
        self.tab1.setLayout(self.grid1)
        self.tab2.setLayout(self.grid2)
        self.setWindowTitle('FlyStim GUI')    
        self.show()
        

    def onSelectedProtocolID(self, text):
        if text == "(select a protocol to run)":
            return
        # Clear old params list from grid
        self.resetLayout()
        
        # initialize the selected protocol object
        prot_names = [x.__name__ for x in self.available_protocols]
        self.protocol_object = self.available_protocols[prot_names.index(text)]()

        #update display lists of run & protocol parameters
        self.updateProtocolParametersInput()
        self.updateRunParamtersInput()
        self.show()
       
    def onPressedButton(self):
        sender = self.sender()
        if sender.text() == 'Record':
            if self.data.experiment_file is None:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("You have not initialized a data file yet")
                msg.setInformativeText("You can show stimuli by clicking the View button, but no metadata will be saved")
                msg.setWindowTitle("No experiment file")
                msg.setDetailedText("Initialize or load an experiment file if you'd like to save your metadata")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            else:
                self.status_label.setText('Recording ...')
                QApplication.processEvents()
                self.sendRun(save_metadata_flag = True)         
        elif sender.text() == 'View':
            self.status_label.setText('Viewing ...')
            QApplication.processEvents()
            self.sendRun(save_metadata_flag = False)         

        elif sender.text() == 'Stop':
            self.epoch_run.stopRun()
            
        elif sender.text() == 'Enter note':
            self.noteText = self.notesEdit.toPlainText()
            if self.data.experiment_file is None:
                self.notesEdit.setTextColor(QtGui.QColor("Red"))
            else: 
                self.data.addNoteToExperimentFile(self.noteText) # save note to expt file
                self.notesEdit.clear() # clear notes box
            
        elif sender.text() == 'Initialize experiment':
            dialog = QDialog()
            
            dialog.ui = InitializeExperimentGUI(parent = dialog)
            dialog.ui.setupUI(self, dialog)
            dialog.setFixedSize(300,200)
            dialog.exec_()
            
            self.data.experiment_file_name = dialog.ui.le_FileName.text()
            self.data.data_directory = dialog.ui.le_DataDirectory.text()
            self.data.experimenter = dialog.ui.le_Experimenter.text()
            self.data.rig = dialog.ui.le_Rig.text()
            
        elif sender.text() == 'Load experiment':
            filePath, _ = QFileDialog.getOpenFileName(self, "Open file")
            self.data.experiment_file_name = os.path.split(filePath)[1].split('.')[0]
            self.data.data_directory = os.path.split(filePath)[0]
            
            if self.data.experiment_file_name is not '':
                self.data.reOpenExperimentFile()
                self.currentExperimentLabel.setText(self.data.experiment_file_name)
                # update series count to reflect already-collected series
                largest_prior_value = max(list(map(int,list(self.data.experiment_file['/epoch_runs'].keys()))), default = 0)
                self.data.experiment_file.close()
                self.series_counter_input.setValue(largest_prior_value + 1)

    def resetLayout(self):
        for ii in range(len(self.protocol_object.protocol_parameters.items())):
            item = self.grid1.itemAtPosition(self.run_params_ct+5+ii,0)
            if item != None:
                item.widget().deleteLater()
            item = self.grid1.itemAtPosition(self.run_params_ct+5+ii,1)
            if item != None:
                item.widget().deleteLater()
        self.show()

    def updateProtocolParametersInput(self):
        # update display window to show parameters for this protocol
        self.protocol_parameter_input = {}; # clear old input params dict
        ct = 0
        for key, value in self.protocol_object.protocol_parameters.items():
            ct += 1
            newLabel = QLabel(key + ':')
            self.grid1.addWidget(newLabel, self.run_params_ct + 4 + ct , 0)
            
            if isinstance(value, bool):
                self.protocol_parameter_input[key] = QCheckBox()
                self.protocol_parameter_input[key].setChecked(value)
            else:
                self.protocol_parameter_input[key] = QLineEdit()
                if isinstance(value, int):
                    self.protocol_parameter_input[key].setValidator(QtGui.QIntValidator())
                elif isinstance(value, float):
                    self.protocol_parameter_input[key].setValidator(QtGui.QDoubleValidator())
                    
                self.protocol_parameter_input[key].setText(str(value)) #set to default value
            self.grid1.addWidget(self.protocol_parameter_input[key], self.run_params_ct + 4 + ct, 1, 1, 2)
        
    def updateRunParamtersInput(self):
        self.run_params_ct = 0
        # Run parameters list
        for key, value in self.protocol_object.run_parameters.items():
            if key not in ['protocol_ID', 'run_start_time']:
                self.run_params_ct += 1
                newLabel = QLabel(key + ':')
                self.grid1.addWidget(newLabel, 1 + self.run_params_ct , 0)
                
                self.run_parameter_input[key] = QLineEdit()
                if isinstance(value, int):
                    validator = QtGui.QIntValidator()
                    validator.setBottom(0)
                elif isinstance(value, float):
                    validator = QtGui.QDoubleValidator()
                    validator.setBottom(0)
                self.run_parameter_input[key].setValidator(validator)
                self.run_parameter_input[key].setText(str(value))
                self.grid1.addWidget(self.run_parameter_input[key], 1 + self.run_params_ct, 1, 1, 1)

    def onEnteredSeriesCount(self):
        self.data.series_count = self.series_counter_input.value()
        if self.data.experiment_file is not None:
            self.data.reOpenExperimentFile()
            existing_groups = list(self.data.experiment_file['/epoch_runs'].keys())
            self.data.experiment_file.close()
            if any(str(self.data.series_count) in x for x in existing_groups):
                self.series_counter_input.setStyleSheet("background-color: rgb(0, 255, 255);")
            else:
                self.series_counter_input.setStyleSheet("background-color: rgb(255, 255, 255);")
            
    def sendRun(self, save_metadata_flag = True):
        #check to make sure a protocol has been selected
        if self.protocol_object.run_parameters['protocol_ID'] == '':
                self.status_label.setText('Select a protocol')
                return #no protocol exists, don't send anything
            
        #check to make sure the series count does not already exist
        if save_metadata_flag:
            self.data.series_count = self.series_counter_input.value()
            self.data.reOpenExperimentFile()
            existing_groups = list(self.data.experiment_file['/epoch_runs'].keys())
            self.data.experiment_file.close()
            if any(str(self.data.series_count) in x for x in existing_groups):
                self.series_counter_input.setStyleSheet("background-color: rgb(0, 255, 255);")
                return #group already exists, don't send anything
            else:
                self.series_counter_input.setStyleSheet("background-color: rgb(255, 255, 255);")
            
        
        # Populate parameters from filled fields
        for key, value in self.run_parameter_input.items():
            self.protocol_object.run_parameters[key] = float(self.run_parameter_input[key].text())
            
        for key, value in self.protocol_parameter_input.items():
            if isinstance(self.protocol_parameter_input[key],QCheckBox): #QCheckBox
                self.protocol_object.protocol_parameters[key] = self.protocol_parameter_input[key].isChecked()
            elif isinstance(self.protocol_object.protocol_parameters[key],str):
                self.protocol_object.protocol_parameters[key] = self.protocol_parameter_input[key].text() # Pass the string
            else: #QLineEdit
                new_param_entry = self.protocol_parameter_input[key].text()
                
                if new_param_entry[0] == '[': #User trying to enter a list of values
                    to_a_list = []
                    for x in new_param_entry[1:-1].split(','): to_a_list.append(float(x))
                    self.protocol_object.protocol_parameters[key] = to_a_list
                else: 
                    self.protocol_object.protocol_parameters[key] = float(new_param_entry)
        
        # Populate fly metadata from fly data fields
        self.data.fly_metadata = {'fly:fly_id':self.fly_id_input.text(),
                                  'fly:sex':self.fly_sex_input.currentText(),
                                  'fly:age':self.fly_age_input.value(), 
                                  'fly:prep':self.fly_prep_input.currentText(),
                                  'fly:driver_1':self.fly_driver_1.currentText(),
                                  'fly:indicator_1':self.fly_indicator_1.currentText(), 
                                  'fly:driver_2':self.fly_driver_2.currentText(),
                                  'fly:indicator_2':self.fly_indicator_2.currentText(),
                                  'fly:genotype':self.fly_genotype_input.text()}
        
        
        self.epoch_run.startRun(self.protocol_object, self.data, self.client, save_metadata_flag = save_metadata_flag)       

        self.status_label.setText('Ready')
        
        if save_metadata_flag:
            # Advance the series_count:
            self.data.advanceSeriesCount()
            self.series_counter_input.setValue(self.data.series_count)
            
        QApplication.processEvents()
        
class InitializeExperimentGUI(QWidget):
   def setupUI(self, experimentGuiObject, parent = None):
      super(InitializeExperimentGUI, self).__init__(parent)
      self.parent = parent
      self.experimentGuiObject = experimentGuiObject
      layout = QFormLayout()
      
      label_FileName = QLabel('File Name:')
      init_now = datetime.now()
      defaultName = init_now.isoformat()[:-16]
      self.le_FileName = QLineEdit(defaultName)
      layout.addRow(label_FileName, self.le_FileName)
      
      button_SelectDirectory = QPushButton("Select Directory...", self)
      button_SelectDirectory.clicked.connect(self.onPressedDirectoryButton) 
      self.le_DataDirectory = QLineEdit(self.experimentGuiObject.data.data_directory)
      layout.addRow(button_SelectDirectory, self.le_DataDirectory)
      
      label_Experimenter = QLabel('Experimenter:')
      self.le_Experimenter = QLineEdit(self.experimentGuiObject.data.experimenter)
      layout.addRow(label_Experimenter, self.le_Experimenter)
      
      label_Rig = QLabel('Rig:')
      self.le_Rig = QLineEdit(self.experimentGuiObject.data.rig)
      layout.addRow(label_Rig,self.le_Rig)
      
      self.label_status = QLabel('Enter experiment info')
      layout.addRow(self.label_status)
      
      enterButton = QPushButton("Enter", self)
      enterButton.clicked.connect(self.onPressedEnterButton) 
      layout.addRow(enterButton)

      self.setLayout(layout)

   def onPressedEnterButton(self):
       self.experimentGuiObject.data.experiment_file_name = self.le_FileName.text()
       self.experimentGuiObject.data.data_directory = self.le_DataDirectory.text()
       self.experimentGuiObject.data.experimenter = self.le_Experimenter.text()
       self.experimentGuiObject.data.rig = self.le_Rig.text()

       if os.path.isfile(os.path.join(self.experimentGuiObject.data.data_directory,
                                      self.experimentGuiObject.data.experiment_file_name) + '.hdf5'):
           self.label_status.setText('Experiment file already exists!')
       elif not os.path.isdir(self.experimentGuiObject.data.data_directory):
           self.label_status.setText('Data directory does not exist!')
       else: 
           self.label_status.setText('Data entered')
           self.experimentGuiObject.currentExperimentLabel.setText(self.experimentGuiObject.data.experiment_file_name)
           self.experimentGuiObject.data.initializeExperimentFile()
           self.experimentGuiObject.series_counter_input.setValue(1)
           self.close()
           self.parent.close()
           
   def onPressedDirectoryButton(self):
       filePath = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
       self.le_DataDirectory.setText(filePath)
          

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImagingExperimentGUI()
    sys.exit(app.exec_())