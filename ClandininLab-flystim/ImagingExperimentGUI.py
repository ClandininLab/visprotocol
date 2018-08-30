#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 10:51:42 2018

@author: mhturner
"""
import sys
from PyQt5.QtWidgets import (QPushButton, QWidget, QLabel, QTextEdit, QGridLayout, QApplication,
                             QComboBox, QLineEdit, QFormLayout, QDialog, QFileDialog, QInputDialog,
                             QMessageBox, QCheckBox, QSpinBox)
import PyQt5.QtGui as QtGui
from datetime import datetime
import os

# TODO: merge data manager / source manager GUI into this as a window ("start new fly" button)
# TODO: handle params that are meant to be strings

class ImagingExperimentGUI(QWidget):
    
    def __init__(self):
        super().__init__()
        self.noteText = ''
        self.run_parameter_input = {}
        self.protocol_parameter_input = {}
        self.ignoreWarnings = False
        
        # Link to a protocol object
        items = ('MhtProtocol','ExampleProtocol', '')
        item, ok = QInputDialog.getItem(self, "select user protocol", 
         "Available protocols", items, 0, False)
        
        if item == 'MhtProtocol':
            import MhtProtocol
            self.protocolObject = MhtProtocol.MhtProtocol();
        elif item == 'ExampleProtocol':
            import ExampleProtocol
            self.protocolObject = ExampleProtocol.ExampleProtocol();
        elif item == '':
            import ExampleProtocol
            self.protocolObject = ExampleProtocol.ExampleProtocol();
            
        self.initUI()

    def initUI(self):  
        self.grid = QGridLayout()
        self.grid.setSpacing(10)
        
        # Protocol ID drop-down:
        comboBox = QComboBox(self)
        comboBox.addItem("(select a protocol to run)")
        for protID in self.protocolObject.protocolIDList:
            comboBox.addItem(protID)
        protocol_label = QLabel('Protocol:')
        comboBox.activated[str].connect(self.onSelectedProtocolID)

        self.grid.addWidget(protocol_label, 1, 0)
        self.grid.addWidget(comboBox, 1, 1, 1, 1)
        
        # status label showing init expt, selected source, protocol chosen etc
        self.statusLabel = QLabel()
        self.grid.addWidget(self.statusLabel, 2 , 0, 1, 2)
        self.updateStatusLabel()
        
        self.run_params_ct = 0
        # Run parameters list
        for key, value in self.protocolObject.run_parameters.items():
            if key not in ['protocol_ID', 'run_start_time']:
                self.run_params_ct += 1
                newLabel = QLabel(key + ':')
                self.grid.addWidget(newLabel, 2 + self.run_params_ct , 0)
                
                self.run_parameter_input[key] = QLineEdit()
                if isinstance(value, int):
                    validator = QtGui.QIntValidator()
                    validator.setBottom(0)
                elif isinstance(value, float):
                    validator = QtGui.QDoubleValidator()
                    validator.setBottom(0)
                self.run_parameter_input[key].setValidator(validator)
                self.run_parameter_input[key].setText(str(value))
                self.grid.addWidget(self.run_parameter_input[key], 2 + self.run_params_ct, 1, 1, 1)
         
        # Start button:
        startButton = QPushButton("Start", self)
        startButton.clicked.connect(self.onPressedButton) 
        self.grid.addWidget(startButton, self.run_params_ct+3, 0)
        
        # Stop button:
        stopButton = QPushButton("Stop", self)
        stopButton.clicked.connect(self.onPressedButton) 
        self.grid.addWidget(stopButton, self.run_params_ct+3, 1)
        
        # Enter note button:
        noteButton = QPushButton("Enter note", self)
        noteButton.clicked.connect(self.onPressedButton) 
        self.grid.addWidget(noteButton, self.run_params_ct+4, 0)

        # Notes field:
        self.notesEdit = QTextEdit()
        self.grid.addWidget(self.notesEdit, self.run_params_ct+4, 1, 1, 1)
        
        self.setLayout(self.grid) 
        self.setGeometry(300, 300, 450, 500)
        self.setWindowTitle('FlyStim')    
        self.show()
        
        # Initialize new experiment button
        initializeButton = QPushButton("Initialize experiment", self)
        initializeButton.clicked.connect(self.onPressedButton) 
        self.grid.addWidget(initializeButton, 1, 2)
        
        # Label with current expt file
        self.currentExperimentLabel = QLabel('')
        self.grid.addWidget(self.currentExperimentLabel, 2, 2)
        
        # Load existing experiment button
        loadButton = QPushButton("Load experiment", self)
        loadButton.clicked.connect(self.onPressedButton) 
        self.grid.addWidget(loadButton, 3, 2)
        
        # Current imaging series counter
        newLabel = QLabel('series counter:')
        self.grid.addWidget(newLabel, 7 , 2)
        self.series_counter_input = QSpinBox()
        self.series_counter_input.setMinimum(1)
        self.series_counter_input.setMaximum(1000)
        self.series_counter_input.setValue(1)
        self.series_counter_input.valueChanged.connect(self.onEnteredSeriesCount)
        self.grid.addWidget(self.series_counter_input, 8, 2)

    def onSelectedProtocolID(self, text):
        if text == "(select a protocol to run)":
            return
        else:
            self.protocolObject.run_parameters['protocol_ID'] = text
            
        # Clear old params list from grid
        self.resetLayout()
        
        # Get default protocol parameters for this protocol ID
        self.protocolObject.protocol_parameters = self.protocolObject.getParameterDefaults(self.protocolObject.run_parameters['protocol_ID'])
        
        # update display window to show parameters for this protocol
        self.protocol_parameter_input = {}; # clear old input params dict
        ct = 0
        for key, value in self.protocolObject.protocol_parameters.items():
            ct += 1
            newLabel = QLabel(key + ':')
            self.grid.addWidget(newLabel, self.run_params_ct + 4 + ct , 0)
            
            if isinstance(value, bool):
                self.protocol_parameter_input[key] = QCheckBox()
                self.protocol_parameter_input[key].setChecked(value)
                self.grid.addWidget(self.protocol_parameter_input[key], self.run_params_ct + 4 + ct, 1, 1, 1)
            else:
                self.protocol_parameter_input[key] = QLineEdit()
                if isinstance(value, int):
                    self.protocol_parameter_input[key].setValidator(QtGui.QIntValidator())
                elif isinstance(value, float):
                    self.protocol_parameter_input[key].setValidator(QtGui.QDoubleValidator())
                    
                self.protocol_parameter_input[key].setText(str(value)) #set to default value
                self.grid.addWidget(self.protocol_parameter_input[key], self.run_params_ct + 4 + ct, 1, 1, 1)
            
        self.updateStatusLabel()
        self.show()
       
    def onPressedButton(self):
        sender = self.sender()
        if sender.text() == 'Start':
            if self.protocolObject.run_parameters['protocol_ID'] == '':
                print('Select a protocol to run, first')
                return
            
            if self.protocolObject.experiment_file is None and not self.ignoreWarnings:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("You are not saving your metadata")
                msg.setInformativeText("Would you like to present stimuli anyway?")
                msg.setWindowTitle("MessageBox demo")
                msg.setDetailedText("Initialize or load an experiment file if you'd like to save your metadata")
                msg.setStandardButtons(QMessageBox.Ignore | QMessageBox.No | QMessageBox.Yes )
                msg.buttonClicked.connect(self.onClickedWarningMessageButton)
                msg.exec_()
            else:
                self.sendRun()

        elif sender.text() == 'Stop':
            self.protocolObject.stop = True
            
        elif sender.text() == 'Enter note':
            self.noteText = self.notesEdit.toPlainText()
            if self.protocolObject.experiment_file is None:
                self.notesEdit.setTextColor(QtGui.QColor("Red"))
            else: 
                self.protocolObject.addNoteToExperimentFile(self.noteText) # save note to expt file
                self.notesEdit.clear() # clear notes box
            
        elif sender.text() == 'Initialize experiment':
            dialog = QDialog()
            
            dialog.ui = InitializeExperimentGUI(parent = dialog)
            dialog.ui.setupUI(self, dialog)
            dialog.setFixedSize(300,200)
            dialog.exec_()
            
            self.protocolObject.experiment_file_name = dialog.ui.le_FileName.text()
            self.protocolObject.data_directory = dialog.ui.le_DataDirectory.text()
            self.protocolObject.experimenter = dialog.ui.le_Experimenter.text()
            self.protocolObject.rig = dialog.ui.le_Rig.text()
            
        elif sender.text() == 'Load experiment':
            filePath, _ = QFileDialog.getOpenFileName(self, "Open file")
            self.protocolObject.experiment_file_name = os.path.split(filePath)[1].split('.')[0]
            self.protocolObject.data_directory = os.path.split(filePath)[0]
            
            if self.protocolObject.experiment_file_name is not '':
                self.protocolObject.reOpenExperimentFile()
                self.currentExperimentLabel.setText(self.protocolObject.experiment_file_name)
                # update series count to reflect already-collected series
                largest_prior_value = max(list(map(int,list(self.protocolObject.experiment_file['/epoch_runs'].keys()))), default = 0)
                self.protocolObject.experiment_file.close()
                self.series_counter_input.setValue(largest_prior_value + 1)

            self.updateStatusLabel()

    def resetLayout(self):
        for ii in range(len(self.protocolObject.protocol_parameters.items())):
            item = self.grid.itemAtPosition(self.run_params_ct+5+ii,0)
            if item != None:
                item.widget().deleteLater()
            item = self.grid.itemAtPosition(self.run_params_ct+5+ii,1)
            if item != None:
                item.widget().deleteLater()
        self.show()
        
    def updateStatusLabel(self):
        if self.protocolObject.run_parameters['protocol_ID'] == '':
            self.statusLabel.setText('Select a protocol to run')
        elif self.protocolObject.experiment_file is None:
            self.statusLabel.setText('Initialize an experiment file to save data')
        elif self.protocolObject.currentFly is None:
            self.statusLabel.setText('Warning: No fly defined!')
            
    def onClickedWarningMessageButton(self, input):
        if input.text() == '&Yes':
            self.sendRun()
        elif input.text() == 'Ignore':
            self.ignoreWarnings = True
            self.sendRun()
            
    def onEnteredSeriesCount(self):
        self.protocolObject.series_count = self.series_counter_input.value()
        if self.protocolObject.experiment_file is not None:
            self.protocolObject.reOpenExperimentFile()
            existing_groups = list(self.protocolObject.experiment_file['/epoch_runs'].keys())
            self.protocolObject.experiment_file.close()
            if any(str(self.protocolObject.series_count) in x for x in existing_groups):
                self.series_counter_input.setStyleSheet("background-color: rgb(0, 255, 255);")
            else:
                self.series_counter_input.setStyleSheet("background-color: rgb(255, 255, 255);")
            
    def sendRun(self):
        if self.protocolObject.experiment_file is not None:
            self.protocolObject.series_count = self.series_counter_input.value()
            self.protocolObject.reOpenExperimentFile()
            existing_groups = list(self.protocolObject.experiment_file['/epoch_runs'].keys())
            self.protocolObject.experiment_file.close()
            if any(str(self.protocolObject.series_count) in x for x in existing_groups):
                self.series_counter_input.setStyleSheet("background-color: rgb(0, 255, 255);")
                return #group already exists
            else:
                self.series_counter_input.setStyleSheet("background-color: rgb(255, 255, 255);")
        
        # Populate parameters from filled fields
        for key, value in self.run_parameter_input.items():
            self.protocolObject.run_parameters[key] = float(self.run_parameter_input[key].text())
            
        for key, value in self.protocol_parameter_input.items():
            if isinstance(self.protocol_parameter_input[key],QCheckBox): #QCheckBox
                self.protocolObject.protocol_parameters[key] = self.protocol_parameter_input[key].isChecked()
            else: #QLineEdit
                new_param_entry = self.protocol_parameter_input[key].text()
                
                if new_param_entry[0] == '[': #User trying to enter a list of values
                    to_a_list = []
                    for x in new_param_entry[1:-1].split(','): to_a_list.append(float(x))
                    self.protocolObject.protocol_parameters[key] = to_a_list
                else: 
                    self.protocolObject.protocol_parameters[key] = float(new_param_entry)

        # Send run and protocol parameters to protocol object
        self.protocolObject.start(self.protocolObject.run_parameters, self.protocolObject.protocol_parameters)
        
        if self.protocolObject.experiment_file is not None:
            # Advance the series_count:
            self.series_counter_input.setValue(self.protocolObject.series_count + 1)
            self.protocolObject.series_count = self.series_counter_input.value()
        
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
      self.le_DataDirectory = QLineEdit(self.experimentGuiObject.protocolObject.data_directory)
      layout.addRow(button_SelectDirectory, self.le_DataDirectory)
      
      label_Experimenter = QLabel('Experimenter:')
      self.le_Experimenter = QLineEdit(self.experimentGuiObject.protocolObject.experimenter)
      layout.addRow(label_Experimenter, self.le_Experimenter)
      
      label_Rig = QLabel('Rig:')
      self.le_Rig = QLineEdit(self.experimentGuiObject.protocolObject.rig)
      layout.addRow(label_Rig,self.le_Rig)
      
      self.label_status = QLabel('Enter experiment info')
      layout.addRow(self.label_status)
      
      enterButton = QPushButton("Enter", self)
      enterButton.clicked.connect(self.onPressedEnterButton) 
      layout.addRow(enterButton)

      self.setLayout(layout)

   def onPressedEnterButton(self):
       self.experimentGuiObject.protocolObject.experiment_file_name = self.le_FileName.text()
       self.experimentGuiObject.protocolObject.data_directory = self.le_DataDirectory.text()
       self.experimentGuiObject.protocolObject.experimenter = self.le_Experimenter.text()
       self.experimentGuiObject.protocolObject.rig = self.le_Rig.text()

       if os.path.isfile(os.path.join(self.experimentGuiObject.protocolObject.data_directory,
                                      self.experimentGuiObject.protocolObject.experiment_file_name) + '.hdf5'):
           self.label_status.setText('Experiment file already exists!')
       elif not os.path.isdir(self.experimentGuiObject.protocolObject.data_directory):
           self.label_status.setText('Data directory does not exist!')
       else: 
           self.label_status.setText('Data entered')
           self.experimentGuiObject.currentExperimentLabel.setText(self.experimentGuiObject.protocolObject.experiment_file_name)
           self.experimentGuiObject.protocolObject.initializeExperimentFile()
           self.experimentGuiObject.updateStatusLabel()
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