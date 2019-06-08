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
import glob

from visprotocol.clandinin_client import Client
from visprotocol.clandinin_data import Data
from visprotocol.control import EpochRun
from visprotocol import protocol

# TODO: handle params that are meant to be strings

class ImagingExperimentGUI(QWidget):
    
    def __init__(self):
        super().__init__()
        self.noteText = ''
        self.run_parameter_input = {}
        self.protocol_parameter_input = {}
        self.ignoreWarnings = False
        
        #looks for user names based on .yaml config files in visprotocol/config directory
        # Filenames should be: USER_config.yaml
        config_dir = os.path.join(os.path.abspath(os.path.join(os.path.split(__file__)[0], os.pardir)), 'config')
        user_config_files = [os.path.split(f)[1] for f in glob.glob(os.path.join(config_dir,'*.yaml'))]

        user_names = [f.split('_config')[0] for f in user_config_files]
        user_name, ok = QInputDialog.getItem(self, "select user", 
                                             "Available users", user_names, 0, False)

        # start a client
        self.client = Client()
        # start a data object
        self.data = Data(user_name)
        # get a protocol, just start with the base class until user selects one
        self.protocol_object = getattr(protocol, user_name + '_protocol').BaseProtocol()
        # get available protocol classes
        self.available_protocols = getattr(protocol, user_name + '_protocol').BaseProtocol.__subclasses__()
        # get an epoch run control object
        self.epoch_run = EpochRun()

        self.initUI()

    def initUI(self):  
        self.layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        
        self.protocol_tab = QWidget()
        self.protocol_grid = QGridLayout()
        self.protocol_grid.setSpacing(10)
        
        self.data_tab = QWidget()
        self.data_grid = QFormLayout()
        self.data_grid.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.data_grid.setLabelAlignment(QtCore.Qt.AlignCenter)
        
        self.poi_tab = QWidget()
        self.poi_grid = QFormLayout()
        self.poi_grid.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.poi_grid.setLabelAlignment(QtCore.Qt.AlignCenter)
        
        self.file_tab = QWidget()
        self.file_grid = QFormLayout()
        self.file_grid.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.file_grid.setLabelAlignment(QtCore.Qt.AlignCenter)

        self.tabs.addTab(self.protocol_tab,"Main")
        self.tabs.addTab(self.data_tab,"Fly")
        self.tabs.addTab(self.poi_tab,"POI")
        self.tabs.addTab(self.file_tab, "File")
        
        self.tabs.resize(450, 500) 
        
        # # # TAB 1: MAIN controls, for selecting / playing stimuli
        # Protocol ID drop-down:
        comboBox = QComboBox(self)
        comboBox.addItem("(select a protocol to run)")
        for sub_class in self.available_protocols:
            comboBox.addItem(sub_class.__name__)
        protocol_label = QLabel('Protocol:')
        comboBox.activated[str].connect(self.onSelectedProtocolID)
        self.protocol_grid.addWidget(protocol_label, 1, 0)
        self.protocol_grid.addWidget(comboBox, 1, 1, 1, 1)
        
        # Parameter preset drop-down:
        parameter_preset_label = QLabel('Parameter_preset:')
        self.protocol_grid.addWidget(parameter_preset_label, 2, 0)
        self.updateParameterPresetSelector()
        
        # Save parameter preset button:
        savePresetButton = QPushButton("Save preset", self)
        savePresetButton.clicked.connect(self.onPressedButton) 
        self.protocol_grid.addWidget(savePresetButton, 2, 2)

        # Run paramters input:
        self.updateRunParamtersInput()

        # View button:
        viewButton = QPushButton("View", self)
        viewButton.clicked.connect(self.onPressedButton) 
        self.protocol_grid.addWidget(viewButton, self.run_params_ct+4, 0)
        
        # Record button:
        recordButton = QPushButton("Record", self)
        recordButton.clicked.connect(self.onPressedButton) 
        self.protocol_grid.addWidget(recordButton, self.run_params_ct+4, 1)
        
        # Stop button:
        stopButton = QPushButton("Stop", self)
        stopButton.clicked.connect(self.onPressedButton) 
        self.protocol_grid.addWidget(stopButton, self.run_params_ct+4, 2)
        
        # Enter note button:
        noteButton = QPushButton("Enter note", self)
        noteButton.clicked.connect(self.onPressedButton) 
        self.protocol_grid.addWidget(noteButton, self.run_params_ct+5, 0)

        # Notes field:
        self.notesEdit = QTextEdit()
        self.protocol_grid.addWidget(self.notesEdit, self.run_params_ct+5, 1, 1, 2)

        # Status window:
        newLabel = QLabel('Status:')
        self.protocol_grid.addWidget(newLabel, 4, 2)
        self.status_label = QLabel()
        self.status_label.setFrameShadow(QFrame.Shadow(1))
        self.protocol_grid.addWidget(self.status_label, 5, 2)
        self.status_label.setText('')

        # Current imaging series counter
        newLabel = QLabel('Series counter:')
        self.protocol_grid.addWidget(newLabel, self.run_params_ct+1 , 2)
        self.series_counter_input = QSpinBox()
        self.series_counter_input.setMinimum(1)
        self.series_counter_input.setMaximum(1000)
        self.series_counter_input.setValue(1)
        self.series_counter_input.valueChanged.connect(self.onEnteredSeriesCount)
        self.protocol_grid.addWidget(self.series_counter_input, self.run_params_ct+2, 2)

        # # # TAB 2: Current FLY metadata information
        # # Fly info:
        # Load any existing fly metadata in this file
        newLabel = QLabel('Load existing fly')
        self.existing_fly_input = QComboBox()
        self.existing_fly_input.activated[int].connect(self.onSelectedExistingFly)
        self.data_grid.addRow(newLabel, self.existing_fly_input)
        self.updateExistingFlyInput()
        

        newLabel = QLabel('Current fly info:')
        newLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.data_grid.addRow(newLabel)
        
        # Fly ID:
        newLabel = QLabel('Fly ID:')
        self.fly_id_input = QLineEdit()
        self.data_grid.addRow(newLabel, self.fly_id_input)
        # Sex:
        newLabel = QLabel('Sex:')
        self.fly_sex_input = QComboBox()
        self.fly_sex_input.addItems(['Female','Male'])
        self.data_grid.addRow(newLabel, self.fly_sex_input)
        # Age:
        newLabel = QLabel('Age:')
        self.fly_age_input = QSpinBox()
        self.fly_age_input.setMinimum(0)
        self.fly_age_input.setValue(1)
        self.data_grid.addRow(newLabel, self.fly_age_input)
        # Prep ID:
        newLabel = QLabel('Prep:')
        self.fly_prep_input = QComboBox()
        self.fly_prep_input.addItem("")
        for prepID in self.data.prepChoices:
            self.fly_prep_input.addItem(prepID)
        self.data_grid.addRow(newLabel, self.fly_prep_input)
        # Driver1:
        newLabel = QLabel('Driver_1:')
        self.fly_driver_1 = QComboBox()
        self.fly_driver_1.addItem("")
        for prepID in self.data.driverChoices:
            self.fly_driver_1.addItem(prepID)
        self.data_grid.addRow(newLabel, self.fly_driver_1)
        # Indicator1:
        newLabel = QLabel('Indicator_1:')
        self.fly_indicator_1 = QComboBox()
        self.fly_indicator_1.addItem("")
        for prepID in self.data.indicatorChoices:
            self.fly_indicator_1.addItem(prepID)
        self.data_grid.addRow(newLabel, self.fly_indicator_1)
        # Driver2:
        newLabel = QLabel('Driver_2:')
        self.fly_driver_2 = QComboBox()
        self.fly_driver_2.addItem("")
        for prepID in self.data.driverChoices:
            self.fly_driver_2.addItem(prepID)
        self.data_grid.addRow(newLabel, self.fly_driver_2)
        # Indicator2:
        newLabel = QLabel('Indicator_2:')
        self.fly_indicator_2 = QComboBox()
        self.fly_indicator_2.addItem("")
        for prepID in self.data.indicatorChoices:
            self.fly_indicator_2.addItem(prepID)
        self.data_grid.addRow(newLabel, self.fly_indicator_2)
        # Fly genotype:
        newLabel = QLabel('Genotype:')
        self.fly_genotype_input = QLineEdit()
        self.data_grid.addRow(newLabel, self.fly_genotype_input)
        
        # # # TAB 3: POI info and attachment to file
        self.poi_tag_label = QLabel('POI tag')
        self.poi_range_label = QLabel('POI number(s) [e.g. "1-4" or "2,6,8"]')
        self.poi_grid.addRow(self.poi_tag_label, self.poi_range_label)
        
        self.poi_tag_entries = []
        self.poi_range_entries = []
        
        for rows in range(8):
            new_tag = QComboBox()
            new_tag.setEditable(True)
            new_tag.addItem('')
            for poi_name in self.data.poiNames:
                new_tag.addItem(poi_name)
            new_range = QLineEdit()

            self.poi_tag_entries.append(new_tag)
            self.poi_range_entries.append(new_range)
            self.poi_grid.addRow(new_tag, new_range)

        new_separator_line = QFrame()
        new_separator_line.setFrameShape(new_separator_line.HLine)
        self.poi_grid.addRow(new_separator_line)
        
        attachPoiDataButton = QPushButton("Attach poi data", self)
        attachPoiDataButton.clicked.connect(self.onPressedButton)
        self.poi_grid.addRow(attachPoiDataButton)
        
        # # # TAB 4: FILE tab - init, load, close etc. h5 file
        # Data file info
        # Initialize new experiment button
        initializeButton = QPushButton("Initialize experiment", self)
        initializeButton.clicked.connect(self.onPressedButton) 
        newLabel = QLabel('Current data file:')
        self.file_grid.addRow(initializeButton, newLabel)
        # Load existing experiment button
        loadButton = QPushButton("Load experiment", self)
        loadButton.clicked.connect(self.onPressedButton) 
        # Label with current expt file
        self.currentExperimentLabel = QLabel('')
        self.file_grid.addRow(loadButton, self.currentExperimentLabel)
        

        self.layout.addWidget(self.tabs)
        self.protocol_tab.setLayout(self.protocol_grid)
        self.data_tab.setLayout(self.data_grid)
        self.poi_tab.setLayout(self.poi_grid)
        self.file_tab.setLayout(self.file_grid)
        self.setWindowTitle('Visprotocol GUI')    
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
        self.protocol_object.loadParameterPresets()
        self.updateParameterPresetSelector()
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
                
        elif sender.text() == 'Save preset':
            self.updateParametersFromFillableFields() #get the state of the param input from GUI
            start_name = self.parameter_preset_comboBox.currentText()
            if start_name == 'Default':
                start_name = ''
            
            text, _ = QInputDialog.getText(self, "Save preset","Preset Name:", QLineEdit.Normal, start_name)
            
            self.protocol_object.updateParameterPresets(text)
            
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
            
            self.updateExistingFlyInput()
            
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
                self.updateExistingFlyInput()
                
        elif sender.text() == 'Attach poi data':
            poi_directory = str(QFileDialog.getExistingDirectory(self, "Select experiment date's data directory"))
            self.data.attachPoiData(poi_directory)

    def resetLayout(self):
        for ii in range(len(self.protocol_object.protocol_parameters.items())):
            item = self.protocol_grid.itemAtPosition(self.run_params_ct+6+ii,0)
            if item != None:
                item.widget().deleteLater()
            item = self.protocol_grid.itemAtPosition(self.run_params_ct+6+ii,1)
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
            self.protocol_grid.addWidget(newLabel, self.run_params_ct + 5 + ct , 0)
            
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
            self.protocol_grid.addWidget(self.protocol_parameter_input[key], self.run_params_ct + 5 + ct, 1, 1, 2)
        
    def updateParameterPresetSelector(self):
        self.parameter_preset_comboBox = QComboBox(self)
        self.parameter_preset_comboBox.addItem("Default")
        for name in self.protocol_object.parameter_presets.keys():
            self.parameter_preset_comboBox.addItem(name)
        self.parameter_preset_comboBox.activated[str].connect(self.onSelectedParameterPreset)
        self.protocol_grid.addWidget(self.parameter_preset_comboBox, 2, 1, 1, 1)
        
    def onSelectedParameterPreset(self, text):
        self.protocol_object.selectProtocolPreset(text)
        self.resetLayout()
        self.updateProtocolParametersInput()
        self.updateRunParamtersInput()
        self.show()
        
    def onSelectedExistingFly(self, index):
        fly_data = self.data.getExistingFlyData()
        self.populateFlyMetadataFields(fly_data[index])
        
    def updateExistingFlyInput(self):
        self.existing_fly_input.clear()
        for fly_data in self.data.getExistingFlyData():
            self.existing_fly_input.addItem(fly_data['fly:fly_id'])
        
    def populateFlyMetadataFields(self, fly_data_dict):
        self.fly_id_input.setText(fly_data_dict['fly:fly_id'])
        self.fly_sex_input.setCurrentText(fly_data_dict['fly:sex'])
        self.fly_age_input.setValue(fly_data_dict['fly:age'])
        self.fly_driver_1.setCurrentText(fly_data_dict['fly:driver_1'])
        self.fly_indicator_1.setCurrentText(fly_data_dict['fly:indicator_1'])
        self.fly_driver_2.setCurrentText(fly_data_dict['fly:driver_2'])
        self.fly_indicator_2.setCurrentText(fly_data_dict['fly:indicator_2'])
        self.fly_genotype_input.setText(fly_data_dict['fly:genotype'])
        
    def updateRunParamtersInput(self):
        self.run_params_ct = 0
        # Run parameters list
        for key, value in self.protocol_object.run_parameters.items():
            if key not in ['protocol_ID', 'run_start_time']:
                self.run_params_ct += 1
                # delete existing labels:
                item = self.protocol_grid.itemAtPosition(2 + self.run_params_ct,0)
                if item != None:
                    item.widget().deleteLater()
                
                #write new labels:
                newLabel = QLabel(key + ':')
                self.protocol_grid.addWidget(newLabel, 2 + self.run_params_ct , 0)
                
                self.run_parameter_input[key] = QLineEdit()
                if isinstance(value, int):
                    validator = QtGui.QIntValidator()
                    validator.setBottom(0)
                elif isinstance(value, float):
                    validator = QtGui.QDoubleValidator()
                    validator.setBottom(0)
                self.run_parameter_input[key].setValidator(validator)
                self.run_parameter_input[key].setText(str(value))
                self.protocol_grid.addWidget(self.run_parameter_input[key], 2 + self.run_params_ct, 1, 1, 1)

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
        self.updateParametersFromFillableFields()

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
        
        # Populate poi information
        self.data.poi_metadata = {}
        for ind in range(len(self.poi_tag_entries)):
            current_tag = self.poi_tag_entries[ind].currentText()
            current_range = self.poi_range_entries[ind].text()
            if (current_tag != '') & (current_range != ''): #both fields are filled in by user
                ranges = (x.split("-") for x in current_range.split(","))
                interpreted_range = [i for r in ranges for i in range(int(r[0]), int(r[-1]) + 1)]
                self.data.poi_metadata[current_tag] = interpreted_range
        
        
        self.epoch_run.startRun(self.protocol_object, self.data, self.client, save_metadata_flag = save_metadata_flag)       

        if save_metadata_flag:
            self.updateExistingFlyInput()
            
        self.status_label.setText('Ready')
        
        if save_metadata_flag:
            # Advance the series_count:
            self.data.advanceSeriesCount()
            self.series_counter_input.setValue(self.data.series_count)
            
        QApplication.processEvents()

    def updateParametersFromFillableFields(self):
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
