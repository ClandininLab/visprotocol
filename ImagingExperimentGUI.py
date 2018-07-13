#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 10:51:42 2018

@author: mhturner
"""

import MhtProtocol
import sys
from PyQt5.QtWidgets import (QPushButton, QWidget, QLabel, QTextEdit, QGridLayout, QApplication, QComboBox, QLineEdit, QFormLayout, QDialog, QFileDialog)
import PyQt5.QtGui as Gui
from datetime import datetime
import squirrel
import os

# TODO: merge init experiment into this as a window ('Initialize experiment' or 'load experiment' button)
# TODO: merge data manager / source manager GUI into this as a window ("start new fly" button)

class ImagingExperimentGUI(QWidget):
    
    def __init__(self):
        super().__init__()
        self.noteText = ''
        self.run_parameter_input = {}
        self.protocol_parameter_input = {}
        
        # Link to a protocol object
        self.protocolObject = MhtProtocol.MhtProtocol();

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
        
        ct = 0
        # Run parameters list
        for key, value in self.protocolObject.run_parameters.items():
            ct += 1
            if key not in ['protocol_ID', 'run_start_time']:
                newLabel = QLabel(key + ':')
                self.grid.addWidget(newLabel, 1 + ct , 0)
                
                self.run_parameter_input[key] = QLineEdit()
                if isinstance(value, int):
                    self.run_parameter_input[key].setValidator(Gui.QIntValidator())
                elif isinstance(value, float):
                    self.run_parameter_input[key].setValidator(Gui.QDoubleValidator())
                self.run_parameter_input[key].setText(str(value))
                self.grid.addWidget(self.run_parameter_input[key], 1 + ct, 1, 1, 1)
        
        
        # Start button:
        startButton = QPushButton("Start", self)
        startButton.clicked.connect(self.onPressedButton) 
        self.grid.addWidget(startButton, 7, 0)
        
        # Stop button:
        stopButton = QPushButton("Stop", self)
        stopButton.clicked.connect(self.onPressedButton) 
        self.grid.addWidget(stopButton, 7, 1)
        
        # Enter note button:
        noteButton = QPushButton("Enter note", self)
        noteButton.clicked.connect(self.onPressedButton) 
        self.grid.addWidget(noteButton, 8, 0)

        # Notes field:
        self.notesEdit = QTextEdit()
        self.grid.addWidget(self.notesEdit, 8, 1, 1, 1)
        
        self.setLayout(self.grid) 
        self.setGeometry(300, 300, 350, 500)
        self.setWindowTitle('FlyStim')    
        self.show()
        
        # Initialize new experiment button
        # TODO connect
        initializeButton = QPushButton("Initialize experiment", self)
        initializeButton.clicked.connect(self.onPressedButton) 
        self.grid.addWidget(initializeButton, 1, 2)
        
        # TODO Status bar with current expt file
        self.currentExperimentLabel = QLabel('')
        self.grid.addWidget(self.currentExperimentLabel, 2, 2)
        
        # Load existing experiment button
        # TODO connect
        loadButton = QPushButton("Load experiment", self)
        loadButton.clicked.connect(self.onPressedButton) 
        self.grid.addWidget(loadButton, 3, 2)
        
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
        # TODO: handle lists of parameters somehow
        self.protocol_parameter_input = {}; # clear old input params dict
        ct = 0
        for key, value in self.protocolObject.protocol_parameters.items():
            ct += 1
            newLabel = QLabel(key + ':')
            self.grid.addWidget(newLabel, 8 + ct , 0)
            self.protocol_parameter_input[key] = QLineEdit()
            if isinstance(value, int):
                self.protocol_parameter_input[key].setValidator(Gui.QIntValidator())
            elif isinstance(value, float):
                self.protocol_parameter_input[key].setValidator(Gui.QDoubleValidator())
#            elif isinstance(value, list):
                
            self.protocol_parameter_input[key].setText(str(value))
            self.grid.addWidget(self.protocol_parameter_input[key], 8 + ct, 1, 1, 1)
        self.show()
       
    def onPressedButton(self):
        sender = self.sender()
        if sender.text() == 'Start':
            if self.protocolObject.run_parameters['protocol_ID'] == '':
                print('select a protocol to run, first')
                return
            # Populate parameters from filled fields
            for key, value in self.run_parameter_input.items():
                self.protocolObject.run_parameters[key] = float(self.run_parameter_input[key].text())
                
            for key, value in self.protocol_parameter_input.items():
                self.protocolObject.protocol_parameters[key] = float(self.protocol_parameter_input[key].text())
            
            # Send run and protocol parameters to protocol control
            self.protocolObject.start(self.protocolObject.run_parameters, self.protocolObject.protocol_parameters)
            
        elif sender.text() == 'Stop':
            self.protocolObject.stop = True
            
        elif sender.text() == 'Enter note':
            self.noteText = self.notesEdit.toPlainText()
            self.protocolObject.addNoteToExperimentFile(self.noteText) # save note to expt file
            self.notesEdit.clear() # clear notes box
            
        elif sender.text() == 'Initialize experiment':
            dialog = QDialog()
            
            dialog.ui = InitializeExperimentGUI(parent = dialog)
            dialog.ui.setupUI(dialog)
            dialog.setFixedSize(300,200)
            dialog.exec_()
            self.ExperimentFileData = {'FileName':dialog.ui.le_FileName.text(),
                                       'DataDirectory':dialog.ui.le_DataDirectory.text(),
                                       'Experimenter':dialog.ui.le_Experimenter.text(),
                                       'Rig':dialog.ui.le_Rig.text()}
            self.protocolObject.initializeExperimentFile(**self.ExperimentFileData)
            self.protocolObject.experiment_file = squirrel.get(self.ExperimentFileData['FileName'], self.ExperimentFileData['DataDirectory'])
            self.currentExperimentLabel.setText(self.ExperimentFileData['FileName'])


    def resetLayout(self):
        # TODO fix these deletions
        for ii in range(len(self.protocolObject.protocol_parameters.items())):
            item = self.grid.itemAtPosition(9+ii,0)
            if item != None:
                item.widget().deleteLater()
            item = self.grid.itemAtPosition(9+ii,1)
            if item != None:
                item.widget().deleteLater()

        self.show()
        
class InitializeExperimentGUI(QWidget):
   def setupUI(self, parent = None):
      super(InitializeExperimentGUI, self).__init__(parent)
      self.parent = parent
      layout = QFormLayout()
      
      label_FileName = QLabel('File Name:')
      init_now = datetime.now()
      defaultName = init_now.isoformat()[:-16]
      self.le_FileName = QLineEdit(defaultName)
      layout.addRow(label_FileName, self.le_FileName)
      
      
      label_DataDirectory = QLabel('Data Directory:')
      self.le_DataDirectory = QLineEdit('/Users/mhturner/documents/stashedObjects/')
      layout.addRow(label_DataDirectory, self.le_DataDirectory)
      
      label_Experimenter = QLabel('Experimenter:')
      self.le_Experimenter = QLineEdit()
      layout.addRow(label_Experimenter, self.le_Experimenter)
      
      label_Rig = QLabel('Rig:')
      self.le_Rig = QLineEdit()
      layout.addRow(label_Rig,self.le_Rig)
      
      self.label_status = QLabel('Enter experiment info')
      layout.addRow(self.label_status)
      
      enterButton = QPushButton("Enter", self)
      enterButton.clicked.connect(self.onPressedEnterButton) 
      layout.addRow(enterButton)

      self.setLayout(layout)

   def onPressedEnterButton(self):
       if os.path.isfile(self.le_DataDirectory.text() + self.le_FileName.text() + '.pkl'):
           self.label_status.setText('Experiment file already exists!')
       else: 
           self.label_status.setText('Data entered')
           self.close()
           self.parent.close()
          

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ProtocolGUI()
    sys.exit(app.exec_())