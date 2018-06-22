#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 10:51:42 2018

@author: mhturner
"""

import MhtProtocol
import sys
from PyQt5.QtWidgets import (QPushButton, QWidget, QLabel, QTextEdit, QGridLayout, QApplication, QComboBox, QLineEdit)
import PyQt5.QtGui as Gui

class ProtocolGUI(QWidget):
    
    def __init__(self):
        super().__init__()
        self.protocolID = ''
        self.protocol_parameters = {}
        self.run_parameters = {'protocol_ID':self.protocolID,
              'num_epochs':5,
              'pre_time':0.5,
              'stim_time':5,
              'tail_time':0.5}
        self.noteText = ''
        
        self.run_parameter_input = {}
        self.protocol_parameter_input = {}
        self.initUI()
        
        
        
    def initUI(self):  
        self.grid = QGridLayout()
        self.grid.setSpacing(10)
        
        # Protocol ID drop-down:
        comboBox = QComboBox(self)
        comboBox.addItem("(select a protocol to run)")
        comboBox.addItem("CheckerboardWhiteNoise")
        comboBox.addItem("RotatingSquareGrating")
        protocol_label = QLabel('Protocol:')
        comboBox.activated[str].connect(self.onSelectedProtocolID)

        self.grid.addWidget(protocol_label, 1, 0)
        self.grid.addWidget(comboBox, 1, 1, 1, 1)
        
        ct = 0
        # Run parameters list
        for key, value in self.run_parameters.items():
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
        
        # Enter note button:
        noteButton = QPushButton("Enter note", self)
        noteButton.clicked.connect(self.onPressedButton) 
        self.grid.addWidget(noteButton, 7, 1)

        # Notes field:
        notes_label = QLabel('Notes:')
        self.notesEdit = QTextEdit()
        self.grid.addWidget(notes_label, 8, 0)
        self.grid.addWidget(self.notesEdit, 8, 1, 1, 1)
        
        
        self.setLayout(self.grid) 
        self.setGeometry(300, 300, 350, 500)
        self.setWindowTitle('FlyStim')    
        self.show()
        
    def onSelectedProtocolID(self, text):
        if text == "(select a protocol to run)":
            return
        else:
            self.run_parameters['protocol_ID'] = text
            
        # Clear old params list from grid
        self.resetLayout()
        
        # Get default protocol parameters for this protocol ID
        self.protocol_parameters = MhtProtocol.getParameterDefaults(self.run_parameters['protocol_ID'])
        
        # update display window to show parameters for this protocol
        # TODO: handle lists of parameters somehow
        self.protocol_parameter_input = {}; # clear old input params dict
        ct = 0
        for key, value in self.protocol_parameters.items():
            ct += 1
            newLabel = QLabel(key + ':')
            self.grid.addWidget(newLabel, 8 + ct , 0)
            self.protocol_parameter_input[key] = QLineEdit()
            if isinstance(value, int):
                self.protocol_parameter_input[key].setValidator(Gui.QIntValidator())
            elif isinstance(value, float):
                self.protocol_parameter_input[key].setValidator(Gui.QDoubleValidator())
            self.protocol_parameter_input[key].setText(str(value))
            self.grid.addWidget(self.protocol_parameter_input[key], 8 + ct, 1, 1, 1)
        self.show()
       
    def onPressedButton(self):
        sender = self.sender()
        if sender.text() == 'Start':
            if self.run_parameters['protocol_ID'] == '':
                print('select a protocol to run, first')
                return
            # Populate parameters from filled fields
            for key, value in self.run_parameter_input.items():
                self.run_parameters[key] = float(self.run_parameter_input[key].text())
                
            for key, value in self.protocol_parameter_input.items():
                self.protocol_parameters[key] = float(self.protocol_parameter_input[key].text())
            
            # Send run and protocol parameters to protocol control
            MhtProtocol.start(self.run_parameters, self.protocol_parameters)
        elif sender.text() == 'Enter note':
            self.noteText = self.notesEdit.toPlainText()
            print(self.noteText) # TODO: save note text to experiment file
        
        
    def resetLayout(self):
        for c in reversed(range(self.grid.count())):
            if c > 13:
                item = self.grid.takeAt(c)
                if item != None:
                    item.widget().deleteLater()
        self.show()
                
        

if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = ProtocolGUI()
    sys.exit(app.exec_())