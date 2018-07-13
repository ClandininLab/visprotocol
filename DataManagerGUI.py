#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 19:16:02 2018

@author: mhturner
"""


import squirrel
from datetime import datetime
import os
from sys import platform

import MhtProtocol
import sys
from PyQt5.QtWidgets import (QPushButton, QWidget, QLabel, QTextEdit, QGridLayout, QApplication, QComboBox, QLineEdit)
import PyQt5.QtGui as Gui

class DataManagerGUI(QWidget):
    
    def __init__(self):
        super().__init__()
        self.fly_data_input = {}
        
        self.default_fly_data = {'FlyID':'Fly1',
                               'Age':0,
                               'Driver(s)': '',
                               'Indicator(s)': '',
                               'Prep':''}
        self.fly_list = []
        self.fly_data = []
        self.current_fly_ID = None
        self.current_fly_data = {}
        
        self.initUI()
        
    def initUI(self):  
        self.grid = QGridLayout()
        self.grid.setSpacing(10)
        
        # Fly ID drop-down:
        fly_label = QLabel('Fly:')
        self.grid.addWidget(fly_label, 1, 0)
        self.comboBox = QComboBox(self)
        self.grid.addWidget(self.comboBox, 1, 1, 1, 1)
        
        self.populateFlyInfo(self.current_fly_ID)
        
  
        # Enter new fly button:
        startButton = QPushButton("Enter new fly", self)
        startButton.clicked.connect(self.onPressedButton) 
        self.grid.addWidget(startButton, 7, 0, 1, 2)
        
        # Delete fly button:
        deleteButton = QPushButton("Delete fly", self)
        deleteButton.clicked.connect(self.onPressedButton) 
        self.grid.addWidget(deleteButton, 7, 2)

        self.setLayout(self.grid) 
        self.setGeometry(300, 300, 350, 500)
        self.setWindowTitle('Data Manager')    
        self.show()
        
    def updateFlyList(self, newflyID):
        self.comboBox.addItem(newflyID)
        self.comboBox.activated[str].connect(self.onSelectedFly)
        self.show()
        
    def populateFlyInfo(self,flyID):
        self.resetFlyInfo()
        if flyID is None:
            useDict = self.default_fly_data
        else:
            ind = self.fly_list.index(flyID)
            useDict = self.fly_data[ind]
            
        ct = 0
        for key, value in useDict.items():
            ct += 1
            newLabel = QLabel(key + ':')
            self.grid.addWidget(newLabel, 1 + ct , 0)
            self.fly_data_input[key] = QLineEdit()
            if isinstance(value, int):
                self.fly_data_input[key].setValidator(Gui.QIntValidator())
            self.fly_data_input[key].setText(str(value))
            self.grid.addWidget(self.fly_data_input[key], 1 + ct, 1, 1, 1)
        
        
        
    def onSelectedFly(self, text):
        self.current_fly_ID = text
        # Populate grid with selected fly info
        self.populateFlyInfo(self.current_fly_ID)
        self.show()
       
    def onPressedButton(self):
        sender = self.sender()
        if sender.text() == 'Enter new fly':
            # Populate parameters from filled fields
            newFlyData = {}
            for key, value in self.fly_data_input.items():
                newFlyData[key] = self.fly_data_input[key].text()
            self.fly_data.append(newFlyData)
            
            self.fly_list.append(newFlyData['FlyID'])
            self.updateFlyList(newFlyData['FlyID'])
            self.comboBox.setCurrentText(newFlyData['FlyID'])
        elif sender.text() == 'Delete fly':
            ind = self.fly_list.index(self.current_fly_ID)
            self.fly_data.pop(ind);
            self.fly_list.pop(ind);
            self.comboBox.removeItem(ind)
            self.comboBox.setCurrentText(self.fly_list[-1])
            self.populateFlyInfo(self.fly_list[-1])
        
    def resetFlyInfo(self):
        for c in reversed(range(self.grid.count())):
            if c > 13:
                item = self.grid.takeAt(c)
                if item != None:
                    item.widget().deleteLater()
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DataManagerGUI()
    sys.exit(app.exec_())
