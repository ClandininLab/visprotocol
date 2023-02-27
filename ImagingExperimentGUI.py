#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 10:51:42 2018

@author: mhturner
"""
from datetime import datetime
import importlib
from importlib.machinery import SourceFileLoader
import os
import sys
from PyQt5.QtWidgets import (QPushButton, QWidget, QLabel, QTextEdit, QGridLayout, QApplication,
                             QComboBox, QLineEdit, QFormLayout, QDialog, QFileDialog, QInputDialog,
                             QMessageBox, QCheckBox, QSpinBox, QTabWidget, QVBoxLayout, QFrame,
                             QTableWidget, QTableWidgetItem, QTreeWidget, QTreeWidgetItem)
import PyQt5.QtCore as QtCore
from PyQt5.QtCore import QThread
import PyQt5.QtGui as QtGui

from visprotocol.util import config_tools, h5io
from visprotocol.control import EpochRun


class ImagingExperimentGUI(QWidget):

    def __init__(self):
        super().__init__()
        self.noteText = ''
        self.run_parameter_input = {}
        self.protocol_parameter_input = {}
        self.ignoreWarnings = False

        # user input for user name and rig config
        dialog = QDialog()
        dialog.ui = InitializeRigGUI(parent=dialog)
        dialog.ui.setupUI(self, dialog)
        dialog.setFixedSize(200, 200)
        dialog.exec()

        # load user and rig configurations
        self.user_configuration = config_tools.getUserConfiguration(self.user_name)
        self.cfg = self.user_configuration.copy()
        self.cfg['user_name'] = self.user_name
        self.cfg['rig_name'] = self.rig_name
        self.cfg['draw_screens'] = self.draw_screens

        rig_config = self.cfg['rig_config'][self.rig_name]
        self.cfg['server_data_directory'] = rig_config['server_data_directory'] if 'server_data_directory' in rig_config else None
        self.cfg['loco_avail'] = 'locomotion' in rig_config and rig_config['locomotion']

        # Use user config file to import protocol, client and data modules
        full_module_paths = config_tools.getFullPathsToModules(self.cfg)
        protocol_module = SourceFileLoader(full_module_paths['protocol_module_name'],
                                           full_module_paths['protocol_module_path']).load_module()
        client_module = SourceFileLoader(full_module_paths['client_module_name'],
                                           full_module_paths['client_module_path']).load_module()
        data_module = SourceFileLoader(full_module_paths['data_module_name'],
                                           full_module_paths['data_module_path']).load_module()

        # get a protocol, just start with the base class until user selects one
        self.protocol_object = protocol_module.BaseProtocol(self.cfg) 
        # get available protocol classes
        self.available_protocols = protocol_module.BaseProtocol.__subclasses__()

        # start a client
        self.client = client_module.Client(self.cfg)

        # start a data object
        self.data = data_module.Data(self.cfg)

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
        self.data_grid = QGridLayout()
        self.data_grid.setSpacing(10)
        # self.data_grid.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        # self.data_grid.setLabelAlignment(QtCore.Qt.AlignCenter)

        self.file_tab = QWidget()
        self.file_grid = QFormLayout()
        self.file_grid.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.file_grid.setLabelAlignment(QtCore.Qt.AlignCenter)

        self.tabs.addTab(self.protocol_tab, "Main")
        self.tabs.addTab(self.data_tab, "Animal")
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

        # loco checkbox:
        if self.cfg['loco_avail']:
            loco_label = QLabel('Locomotion:')
            self.protocol_grid.addWidget(loco_label, 1, 2)
            self.loco_checkbox = QCheckBox()
            self.loco_checkbox.setChecked(False)
            self.protocol_grid.addWidget(self.loco_checkbox, 1, 3)
        
        # Parameter preset drop-down:
        parameter_preset_label = QLabel('Parameter_preset:')
        self.protocol_grid.addWidget(parameter_preset_label, 2, 0)
        self.updateParameterPresetSelector()

        # Save parameter preset button:
        savePresetButton = QPushButton("Save preset", self)
        savePresetButton.clicked.connect(self.onPressedButton)
        self.protocol_grid.addWidget(savePresetButton, 2, 2)

        # Run paramters input:
        self.updaterunParametersInput()

        # View button:
        self.viewButton = QPushButton("View", self)
        self.viewButton.clicked.connect(self.onPressedButton)
        self.protocol_grid.addWidget(self.viewButton, self.run_params_ct+4, 0)

        # Record button:
        self.recordButton = QPushButton("Record", self)
        self.recordButton.clicked.connect(self.onPressedButton)
        self.protocol_grid.addWidget(self.recordButton, self.run_params_ct+4, 1)

        # Pause/resume button:
        self.pauseButton = QPushButton("Pause", self)
        self.pauseButton.clicked.connect(self.onPressedButton)
        self.protocol_grid.addWidget(self.pauseButton, self.run_params_ct+4, 2)

        # Stop button:
        stopButton = QPushButton("Stop", self)
        stopButton.clicked.connect(self.onPressedButton)
        self.protocol_grid.addWidget(stopButton, self.run_params_ct+4, 3)

        # Enter note button:
        noteButton = QPushButton("Enter note", self)
        noteButton.clicked.connect(self.onPressedButton)
        self.protocol_grid.addWidget(noteButton, self.run_params_ct+5, 0)

        # Notes field:
        self.notesEdit = QTextEdit()
        self.protocol_grid.addWidget(self.notesEdit, self.run_params_ct+5, 1, 1, 2)

        # Status window:
        newLabel = QLabel('Status:')
        self.protocol_grid.addWidget(newLabel, 3, 2)
        self.status_label = QLabel()
        self.status_label.setFrameShadow(QFrame.Shadow(1))
        self.protocol_grid.addWidget(self.status_label, 3, 3)
        self.status_label.setText('')

        # Epoch count refresh button:
        checkEpochCntButton = QPushButton("Check epochs:", self)
        checkEpochCntButton.clicked.connect(self.onPressedButton)
        self.protocol_grid.addWidget(checkEpochCntButton, 4, 2)

        # Epoch count window:
        self.epoch_count = QLabel()
        self.epoch_count.setFrameShadow(QFrame.Shadow(1))
        self.protocol_grid.addWidget(self.epoch_count, 4, 3)
        self.epoch_count.setText('')

        # Imaging type dropdown (if AODscope):
        if self.data.rig == 'AODscope':
            self.imagingTypeComboBox = QComboBox(self)
            self.imagingTypeComboBox.addItem("POI")
            self.imagingTypeComboBox.addItem("xyt series")
            self.imagingTypeComboBox.activated[str].connect(self.onChangedDataType)
            self.protocol_grid.addWidget(self.imagingTypeComboBox, 5, 2)

        # Current imaging series counter
        newLabel = QLabel('Series counter:')
        self.protocol_grid.addWidget(newLabel, self.run_params_ct+2, 2)
        self.series_counter_input = QSpinBox()
        self.series_counter_input.setMinimum(1)
        self.series_counter_input.setMaximum(1000)
        self.series_counter_input.setValue(1)
        self.series_counter_input.valueChanged.connect(self.onEnteredSeriesCount)
        self.protocol_grid.addWidget(self.series_counter_input, self.run_params_ct+2, 3)

        # # # TAB 2: Current animal metadata information
        # # Animal info:
        # Load any existing animal metadata in this file
        newLabel = QLabel('Load existing animal')
        self.existing_animal_input = QComboBox()
        self.existing_animal_input.activated[int].connect(self.onSelectedExistingAnimal)
        self.data_grid.addWidget(newLabel, 1, 0)
        self.data_grid.addWidget(self.existing_animal_input, 1, 1, 1, 2)
        self.updateExistingAnimalInput()

        # Animal ID:
        newLabel = QLabel('Animal ID:')
        self.animal_id_input = QLineEdit()
        self.data_grid.addWidget(newLabel, 2, 0)
        self.data_grid.addWidget(self.animal_id_input, 2, 1, 1, 2)

        # Age: 
        newLabel = QLabel('Age:')
        self.animal_age_input = QSpinBox()
        self.animal_age_input.setMinimum(0)
        self.animal_age_input.setValue(1)
        self.data_grid.addWidget(newLabel, 3, 0)
        self.data_grid.addWidget(self.animal_age_input, 3, 1, 1, 2)

        # Notes: 
        newLabel = QLabel('Notes:')
        self.animal_notes_input = QTextEdit()
        self.data_grid.addWidget(newLabel, 4, 0)
        self.data_grid.addWidget(self.animal_notes_input, 4, 1, 1, 2)

        # Use user cfg to populate other metadata options
        self.animal_metadata_inputs = {}
        ct = 0
        for key in self.cfg['animal_metadata']:
            if key == 'transgenes':
                pass
            else:
                ct += 1
                newLabel = QLabel(key)
                new_input = QComboBox()
                new_input.addItem("")
                for choiceID in self.cfg['animal_metadata'][key]:
                    new_input.addItem(choiceID)
                self.data_grid.addWidget(newLabel, 4+ct, 0)
                self.data_grid.addWidget(new_input, 4+ct, 1, 1, 2)

                self.animal_metadata_inputs[key] = new_input
            
        newLabel = QLabel('Transgenes')
        self.data_grid.addWidget(newLabel, 5+ct, 2, 1, 2)
        # handle transgenes metadata
        self.transgenes_input = []
        for driver_ind in range(self.cfg['animal_metadata']['transgenes'].get('max_drivers', 1)):
            newLabel = QLabel('driver / effector')
            driver_input = QComboBox()
            driver_input.addItem("")
            for choiceID in self.cfg['animal_metadata']['transgenes']['driver']:
                    driver_input.addItem(choiceID)
            self.data_grid.addWidget(driver_input, 6+ct+driver_ind, 0)

            effector_inputs = []
            for effector_ind in range(self.cfg['animal_metadata']['transgenes'].get('max_effectors', 1)):
                effector_input = QComboBox()
                effector_input.addItem("")
                for choiceID in self.cfg['animal_metadata']['transgenes']['effector']:
                    effector_input.addItem(choiceID)
                    effector_inputs.append(effector_input)
                self.data_grid.addWidget(effector_input, 6+ct+driver_ind, effector_ind+1)

            self.transgenes_input.append({'driver': driver_input, 'effectors': effector_inputs})

        # Create animal button
        new_separator_line = QFrame()
        new_separator_line.setFrameShape(new_separator_line.HLine)
        self.data_grid.addWidget(new_separator_line, 7+ct+driver_ind, 0, 1, 3)

        createAnimalButton = QPushButton("Create animal", self)
        createAnimalButton.clicked.connect(self.onCreatedAnimal)
        self.data_grid.addWidget(createAnimalButton, 8+ct+driver_ind, 0, 1, 3)

        # # # TAB 3: FILE tab - init, load, close etc. h5 file
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

        # # # # Data browser: # # # # # # # #
        self.groupTree = QTreeWidget(self)
        self.groupTree.setHeaderHidden(True)
        self.groupTree.itemClicked.connect(self.onTreeItemClicked)
        self.file_grid.addRow(self.groupTree)

        # Attribute table
        self.tableAttributes = QTableWidget()
        self.tableAttributes.setStyleSheet("")
        self.tableAttributes.setColumnCount(2)
        self.tableAttributes.setObjectName("tableAttributes")
        self.tableAttributes.setRowCount(0)
        item = QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(10)
        item.setFont(font)
        item.setBackground(QtGui.QColor(121, 121, 121))
        brush = QtGui.QBrush(QtGui.QColor(91, 91, 91))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setForeground(brush)
        self.tableAttributes.setHorizontalHeaderItem(0, item)
        item = QTableWidgetItem()
        item.setBackground(QtGui.QColor(123, 123, 123))
        brush = QtGui.QBrush(QtGui.QColor(91, 91, 91))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setForeground(brush)
        self.tableAttributes.setHorizontalHeaderItem(1, item)
        self.tableAttributes.horizontalHeader().setCascadingSectionResizes(True)
        self.tableAttributes.horizontalHeader().setDefaultSectionSize(200)
        self.tableAttributes.horizontalHeader().setHighlightSections(False)
        self.tableAttributes.horizontalHeader().setSortIndicatorShown(True)
        self.tableAttributes.horizontalHeader().setStretchLastSection(True)
        self.tableAttributes.verticalHeader().setVisible(False)
        self.tableAttributes.verticalHeader().setHighlightSections(False)
        self.tableAttributes.setMinimumSize(QtCore.QSize(200, 400))
        item = self.tableAttributes.horizontalHeaderItem(0)
        item.setText("Attribute")
        item = self.tableAttributes.horizontalHeaderItem(1)
        item.setText("Value")

        self.tableAttributes.itemChanged.connect(self.update_attrs_to_file)

        self.file_grid.addRow(self.tableAttributes)

        # Add all layouts to window and show
        self.layout.addWidget(self.tabs)
        self.protocol_tab.setLayout(self.protocol_grid)
        self.data_tab.setLayout(self.data_grid)
        self.file_tab.setLayout(self.file_grid)
        self.setWindowTitle('Visprotocol')
        self.show()

    def onChangedDataType(self, text):
        if text == 'POI':
            self.data.poi_scan = True
        elif text == 'xyt series':
            self.data.poi_scan = False
        else:
            self.data.poi_scan = False

        self.series_counter_input.setValue(self.data.getSeriesCount())

    def onSelectedProtocolID(self, text):
        if text == "(select a protocol to run)":
            return
        # Clear old params list from grid
        self.resetLayout()

        # initialize the selected protocol object
        prot_names = [x.__name__ for x in self.available_protocols]
        self.protocol_object = self.available_protocols[prot_names.index(text)](self.cfg)

        # update display lists of run & protocol parameters
        self.protocol_object.loadParameterPresets()
        self.updateParameterPresetSelector()
        self.updateProtocolParametersInput()
        self.updaterunParametersInput()
        self.show()

    def onPressedButton(self):
        sender = self.sender()
        if sender.text() == 'Record':
            if (self.data.experimentFileExists() and self.data.currentAnimalExists()):
                self.sendRun(save_metadata_flag=True)
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("You have not initialized a data file and/or animal yet")
                msg.setInformativeText("You can show stimuli by clicking the View button, but no metadata will be saved")
                msg.setWindowTitle("No experiment file and/or animal")
                msg.setDetailedText("Initialize or load both an experiment file and a animal if you'd like to save your metadata")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()

        elif sender.text() == 'View':
            self.sendRun(save_metadata_flag=False)
            self.pauseButton.setText('Pause')

        elif sender.text() == 'Pause':
            self.epoch_run.pauseRun()
            self.pauseButton.setText('Resume')
            self.status_label.setText('Paused...')
            self.show()

        elif sender.text() == 'Resume':
            self.epoch_run.resumeRun()
            self.pauseButton.setText('Pause')
            self.status_label.setText('Viewing...')
            self.show()

        elif sender.text() == 'Stop':
            self.epoch_run.stopRun()
            self.pauseButton.setText('Pause')

        elif sender.text() == 'Enter note':
            self.noteText = self.notesEdit.toPlainText()
            if self.data.experimentFileExists():
                self.data.createNote(self.noteText)  # save note to expt file
                self.notesEdit.clear()  # clear notes box
            else:
                self.notesEdit.setTextColor(QtGui.QColor("Red"))

        elif sender.text() == 'Save preset':
            self.updateParametersFromFillableFields()  # get the state of the param input from GUI
            start_name = self.parameter_preset_comboBox.currentText()
            if start_name == 'Default':
                start_name = ''

            text, _ = QInputDialog.getText(self, "Save preset", "Preset Name:", QLineEdit.Normal, start_name)

            self.protocol_object.updateParameterPresets(text)

        elif sender.text() == 'Initialize experiment':
            dialog = QDialog()

            dialog.ui = InitializeExperimentGUI(parent=dialog)
            dialog.ui.setupUI(self, dialog)
            dialog.setFixedSize(300, 200)
            dialog.exec_()

            self.data.experiment_file_name = dialog.ui.le_FileName.text()
            self.data.data_directory = dialog.ui.le_DataDirectory.text()
            self.data.experimenter = dialog.ui.le_Experimenter.text()

            self.updateExistingAnimalInput()
            self.populateGroups()

        elif sender.text() == 'Load experiment':
            if os.path.isdir(self.data.data_directory):
                filePath, _ = QFileDialog.getOpenFileName(self, "Open file", self.data.data_directory)
            else:
                filePath, _ = QFileDialog.getOpenFileName(self, "Open file")
            self.data.experiment_file_name = os.path.split(filePath)[1].split('.')[0]
            self.data.data_directory = os.path.split(filePath)[0]

            if self.data.experiment_file_name != '':
                self.currentExperimentLabel.setText(self.data.experiment_file_name)
                # update series count to reflect already-collected series
                self.data.reloadSeriesCount()
                self.series_counter_input.setValue(self.data.getHighestSeriesCount() + 1)
                self.updateExistingAnimalInput()
                self.populateGroups()

        elif sender.text() == 'Check epochs:':
            self.epoch_count.setText(str(self.protocol_object.num_epochs_completed))

    def onCreatedAnimal(self):
        # Populate animal metadata from animal data fields
        animal_metadata = {}
        animal_metadata['animal_id'] = self.animal_id_input.text()
        animal_metadata['age'] = self.animal_age_input.value()
        animal_metadata['notes'] = self.animal_notes_input.text()
        for key in self.animal_metadata_inputs:
            animal_metadata[key] = self.animal_metadata_inputs[key].currentText()

        for driver_ind, tg in enumerate(self.transgenes_input):
            expression_string = tg['driver'].currentText() + '->'
            for effector_ind, ef in enumerate(tg['effectors']):
                expression_string += ef.currentText{}

            expression_string = '{}->{}'.format(tg['driver'].currentText(), )
            animal_metadata['driver_{}'.format(driver_ind+1)] = tg['driver'].currentText()
            for effector_ind, tg in enumerate(tg['effectors']):
                animal_metadata['driver_{}_effector_{}'.format(driver_ind+1)] = tg['driver'].currentText()

        self.data.createAnimal(animal_metadata)  # creates new animal and selects it as the current animal
        self.updateExistingAnimalInput()

    def resetLayout(self):
        for ii in range(len(self.protocol_object.protocol_parameters.items())):
            item = self.protocol_grid.itemAtPosition(self.run_params_ct+6+ii, 0)
            if item is not None:
                item.widget().deleteLater()
            item = self.protocol_grid.itemAtPosition(self.run_params_ct+6+ii, 1)
            if item is not None:
                item.widget().deleteLater()
        self.show()

    def updateProtocolParametersInput(self):
        # update display window to show parameters for this protocol
        self.protocol_parameter_input = {}  # clear old input params dict
        ct = 0
        for key, value in self.protocol_object.protocol_parameters.items():
            ct += 1
            newLabel = QLabel(key + ':')
            self.protocol_grid.addWidget(newLabel, self.run_params_ct + 5 + ct, 0)

            if isinstance(value, bool):
                self.protocol_parameter_input[key] = QCheckBox()
                self.protocol_parameter_input[key].setChecked(value)
            else:
                self.protocol_parameter_input[key] = QLineEdit()
                if isinstance(value, int):
                    self.protocol_parameter_input[key].setValidator(QtGui.QIntValidator())
                elif isinstance(value, float):
                    self.protocol_parameter_input[key].setValidator(QtGui.QDoubleValidator())

                self.protocol_parameter_input[key].setText(str(value))  # set to default value
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
        self.updaterunParametersInput()
        self.show()

    def onSelectedExistingAnimal(self, index):
        animal_data = self.data.getExistingAnimalData()
        self.populateAnimalMetadataFields(animal_data[index])
        self.data.current_animal = animal_data[index].get('animal_id')

    def updateExistingAnimalInput(self):
        self.existing_animal_input.clear()
        for animal_data in self.data.getExistingAnimalData():
            self.existing_animal_input.addItem(animal_data['animal_id'])
        index = self.existing_animal_input.findText(self.data.current_animal)
        if index >= 0:
            self.existing_animal_input.setCurrentIndex(index)

    def populateAnimalMetadataFields(self, animal_data_dict):
        self.animal_id_input.setText(animal_data_dict['animal_id'])
        self.animal_age_input.setValue(animal_data_dict['age'])
        self.animal_notes_input.setText(animal_data_dict['notes'])
        for key in self.animal_metadata_inputs:
            self.animal_metadata_inputs[key].setCurrentText(animal_data_dict[key])

    def updaterunParametersInput(self):
        self.run_params_ct = 0
        # Run parameters list
        for key, value in self.protocol_object.run_parameters.items():
            if key not in ['protocol_ID', 'run_start_time']:
                self.run_params_ct += 1
                # delete existing labels:
                item = self.protocol_grid.itemAtPosition(2 + self.run_params_ct, 0)
                if item is not None:
                    item.widget().deleteLater()

                # write new labels:
                newLabel = QLabel(key + ':')
                self.protocol_grid.addWidget(newLabel, 2 + self.run_params_ct, 0)

                if isinstance(value, bool):
                    self.run_parameter_input[key] = QCheckBox()
                    self.run_parameter_input[key].setChecked(value)
                else:
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
        self.data.updateSeriesCount(self.series_counter_input.value())
        if self.data.experimentFileExists:
            if self.data.getSeriesCount() <= self.data.getHighestSeriesCount():
                self.series_counter_input.setStyleSheet("background-color: rgb(255, 0, 0);")
            else:
                self.series_counter_input.setStyleSheet("background-color: rgb(255, 255, 255);")

    def sendRun(self, save_metadata_flag=True):
        # check to make sure a protocol has been selected
        if self.protocol_object.run_parameters['protocol_ID'] == '':
            self.status_label.setText('Select a protocol')
            return  # no protocol exists, don't send anything

        # check to make sure the series count does not already exist
        if save_metadata_flag:
            self.data.updateSeriesCount(self.series_counter_input.value())
            if (self.data.getSeriesCount() in self.data.getExistingSeries()):
                self.series_counter_input.setStyleSheet("background-color: rgb(255, 0, 0);")
                self.status_label.setText('Select an unused series number')
                return  # group already exists, don't send anything
            else:
                self.series_counter_input.setStyleSheet("background-color: rgb(255, 255, 255);")

        # Populate parameters from filled fields
        self.updateParametersFromFillableFields()

        # start the epoch run thread:
        self.runSeriesThread = runSeriesThread(self.epoch_run,
                                               self.protocol_object,
                                               self.data,
                                               self.client,
                                               save_metadata_flag)

        self.runSeriesThread.finished.connect(lambda: self.runFinished(save_metadata_flag))
        self.runSeriesThread.started.connect(lambda: self.runStarted(save_metadata_flag))

        self.runSeriesThread.start()

    def runStarted(self, save_metadata_flag):
        # Lock the view and run buttons to prevent spinning up multiple threads
        self.viewButton.setEnabled(False)
        self.recordButton.setEnabled(False)
        if save_metadata_flag:
            self.status_label.setText('Recording series ' + str(self.data.getSeriesCount()))
        else:
            self.status_label.setText('Viewing...')

    def runFinished(self, save_metadata_flag):
        # re-enable view/record buttons
        self.viewButton.setEnabled(True)
        self.recordButton.setEnabled(True)

        self.status_label.setText('Ready')
        self.pauseButton.setText('Pause')
        if save_metadata_flag:
            self.updateExistingAnimalInput()
            # Advance the series_count:
            self.data.advanceSeriesCount()
            self.series_counter_input.setValue(self.data.getSeriesCount())
            self.populateGroups()

    def updateParametersFromFillableFields(self):
        for key, value in self.run_parameter_input.items():
            if isinstance(self.run_parameter_input[key], QCheckBox): #QCheckBox
                self.protocol_object.run_parameters[key] = self.run_parameter_input[key].isChecked()
            else: # QLineEdit
                self.protocol_object.run_parameters[key] = float(self.run_parameter_input[key].text())

        for key, value in self.protocol_parameter_input.items():
            if isinstance(self.protocol_parameter_input[key], QCheckBox): #QCheckBox
                self.protocol_object.protocol_parameters[key] = self.protocol_parameter_input[key].isChecked()
            elif isinstance(self.protocol_object.protocol_parameters[key], str):
                self.protocol_object.protocol_parameters[key] = self.protocol_parameter_input[key].text() # Pass the string
            else:  # QLineEdit
                new_param_entry = self.protocol_parameter_input[key].text()

                if new_param_entry[0] == '[':  # User trying to enter a list of values
                    to_a_list = []
                    for x in new_param_entry[1:-1].split(','): to_a_list.append(float(x))
                    self.protocol_object.protocol_parameters[key] = to_a_list
                else:
                    self.protocol_object.protocol_parameters[key] = float(new_param_entry)

        if self.cfg['loco_avail']:
            self.data.cfg['do_loco'] = self.loco_checkbox.isChecked() # loco

    def populateGroups(self):
        file_path = os.path.join(self.data.data_directory, self.data.experiment_file_name + '.hdf5')
        group_dset_dict = h5io.getHierarchy(file_path, additional_exclusions='rois')
        self._populateTree(self.groupTree, group_dset_dict)

    def _populateTree(self, widget, dict):
        widget.clear()
        self.fill_item(widget.invisibleRootItem(), dict)

    def fill_item(self, item, value):
        item.setExpanded(True)
        if type(value) is dict:
            for key, val in sorted(value.items()):
                child = QTreeWidgetItem()
                child.setText(0, key)
                item.addChild(child)
                self.fill_item(child, val)
        elif type(value) is list:
            for val in value:
                child = QTreeWidgetItem()
                item.addChild(child)
                if type(val) is dict:
                    child.setText(0, '[dict]')
                    self.fill_item(child, val)
                elif type(val) is list:
                    child.setText(0, '[list]')
                    self.fill_item(child, val)
                else:
                    child.setText(0, val)
                child.setExpanded(True)
        else:
            child = QTreeWidgetItem()
            child.setText(0, value)
            item.addChild(child)

    def onTreeItemClicked(self, item, column):
        file_path = os.path.join(self.data.data_directory, self.data.experiment_file_name + '.hdf5')
        group_path = h5io.getPathFromTreeItem(self.groupTree.selectedItems()[0])

        if group_path != '':
            attr_dict = h5io.getAttributesFromGroup(file_path, group_path)
            if 'series' in group_path.split('/')[-1]:
                editable_values = False  # don't let user edit epoch parameters
            else:
                editable_values = True
            self.populate_attrs(attr_dict = attr_dict, editable_values = editable_values)

    def populate_attrs(self, attr_dict=None, editable_values=False):
        """ Populate attribute for currently selected group """
        self.tableAttributes.blockSignals(True)  # block udpate signals for auto-filled forms
        self.tableAttributes.setRowCount(0)
        self.tableAttributes.setColumnCount(2)
        self.tableAttributes.setSortingEnabled(False)

        if attr_dict:
            for num, key in enumerate(attr_dict):
                self.tableAttributes.insertRow(self.tableAttributes.rowCount())
                key_item = QTableWidgetItem(key)
                key_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.tableAttributes.setItem(num, 0, key_item)

                val_item = QTableWidgetItem(str(attr_dict[key]))
                if editable_values:
                    val_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
                else:
                    val_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.tableAttributes.setItem(num, 1, val_item)

        self.tableAttributes.blockSignals(False)

    def update_attrs_to_file(self, item):
        file_path = os.path.join(self.data.data_directory, self.data.experiment_file_name + '.hdf5')
        group_path = cfg.getPathFromTreeItem(self.groupTree.selectedItems()[0])

        attr_key = self.tableAttributes.item(item.row(), 0).text()
        attr_val = item.text()

        # update attr in file
        cfg.changeAttribute(file_path, group_path, attr_key, attr_val)
        print('Changed attr {} to = {}'.format(attr_key, attr_val))

# # # Other accessory classes. For data file initialization and threading # # # #


class InitializeExperimentGUI(QWidget):
    def setupUI(self, experimentGuiObject, parent=None):
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

        if os.path.isfile(os.path.join(self.experimentGuiObject.data.data_directory, self.experimentGuiObject.data.experiment_file_name) + '.hdf5'):
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
        if os.path.isdir(self.experimentGuiObject.data.data_directory):
            filePath = str(QFileDialog.getExistingDirectory(self, "Select Directory", self.experimentGuiObject.data.data_directory))
        else:
            filePath = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        
        self.le_DataDirectory.setText(filePath)

class InitializeRigGUI(QWidget):
    def setupUI(self, experimentGuiObject, parent=None):
        super(InitializeRigGUI, self).__init__(parent)
        self.parent = parent
        self.experimentGuiObject = experimentGuiObject
        self.user_name = None
        self.draw_screens = False
        self.available_rig_configs = []

        self.layout = QFormLayout()
        self.resize(200, 400)

        label_UserName = QLabel('User Name:')
        self.UserComboBox = QComboBox()
        self.UserComboBox.activated.connect(self.onSelectedUserName)
        for choiceID in config_tools.getAvailableUserNames():
            self.UserComboBox.addItem(choiceID)
        self.layout.addRow(label_UserName, self.UserComboBox)

        label_RigName = QLabel('Rig Config:')
        self.RigComboBox = QComboBox()
        self.RigComboBox.activated.connect(self.onSelectedRig)
        self.layout.addRow(label_RigName, self.RigComboBox)
        self.updateAvailableRigs()

        label_DrawScreens = QLabel('Draw Screens:')
        self.DrawScreensBox = QCheckBox()
        self.DrawScreensBox.setChecked(False)
        self.DrawScreensBox.stateChanged.connect(lambda x: self.should_draw_screens())
        self.layout.addRow(label_DrawScreens, self.DrawScreensBox)

        self.setLayout(self.layout)
        self.show()

    def updateAvailableRigs(self):
        self.RigComboBox.clear()
        for choiceID in self.available_rig_configs:
            self.RigComboBox.addItem(choiceID)

    def onSelectedUserName(self):
        self.user_name = self.UserComboBox.currentText()
        self.available_rig_configs = config_tools.getAvailableRigConfigs(self.user_name)
        self.updateAvailableRigs()
        self.show()

    def onSelectedRig(self):
        self.rig_name = self.RigComboBox.currentText()
        self.experimentGuiObject.user_name = self.user_name
        self.experimentGuiObject.rig_name = self.rig_name
        self.experimentGuiObject.draw_screens = self.draw_screens
        self.close()
        self.parent.close()

    def should_draw_screens(self):
        if self.DrawScreensBox.isChecked():
            self.draw_screens = True
        else:
            self.draw_screens = False


class runSeriesThread(QThread):
    # https://nikolak.com/pyqt-threading-tutorial/
    # https://stackoverflow.com/questions/41848769/pyqt5-object-has-no-attribute-connect
    def __init__(self, epoch_run, protocol_object, data, client, save_metadata_flag):
        QThread.__init__(self)
        self.epoch_run = epoch_run
        self.protocol_object = protocol_object
        self.data = data
        self.client = client
        self.save_metadata_flag = save_metadata_flag

    def __del__(self):
        self.wait()

    def _sendRun(self):
        self.epoch_run.startRun(self.protocol_object, self.data, self.client, save_metadata_flag=self.save_metadata_flag)

    def run(self):
        self._sendRun()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImagingExperimentGUI()
    sys.exit(app.exec())
