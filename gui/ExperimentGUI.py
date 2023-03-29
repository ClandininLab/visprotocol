#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 10:51:42 2018

@author: mhturner
"""
from datetime import datetime
import os
import sys
import importlib
from PyQt5.QtWidgets import (QPushButton, QWidget, QLabel, QTextEdit, QGridLayout, QApplication,
                             QComboBox, QLineEdit, QFormLayout, QDialog, QFileDialog, QInputDialog,
                             QMessageBox, QCheckBox, QSpinBox, QTabWidget, QVBoxLayout, QFrame,
                             QTableWidget, QTableWidgetItem, QTreeWidget, QTreeWidgetItem,
                             QScrollArea, QSizePolicy)
import PyQt5.QtCore as QtCore
from PyQt5.QtCore import QThread
import PyQt5.QtGui as QtGui

from visprotocol.util import config_tools, h5io
from visprotocol.control import EpochRun
from visprotocol import protocol, data, client


class ExperimentGUI(QWidget):

    def __init__(self):
        super().__init__()
        self.note_text = ''
        self.run_parameter_input = {}
        self.protocol_parameter_input = {}
        # self.ignore_warnings = False  # TODO does this do anything?

        # user input to select configuration file and rig name
        # sets self.cfg, self.cfg_name, and self.rig_name
        dialog = QDialog()
        dialog.ui = InitializeRigGUI(parent=dialog)
        dialog.ui.setupUI(self, dialog)
        dialog.setFixedSize(200, 200)
        dialog.exec()

        print('# # # Loading protocol, data and client modules # # #')

        user_protocol_module = config_tools.load_user_module(self.cfg, 'protocol')
        if user_protocol_module is not None:
            self.protocol_object = user_protocol_module.BaseProtocol(self.cfg)
            self.available_protocols =  user_protocol_module.BaseProtocol.__subclasses__()
        else:   # use the built-in
            self.protocol_object =  protocol.BaseProtocol(self.cfg)
            self.available_protocols =  protocol.BaseProtocol.__subclasses__()

        # start a data object
        user_data_module = config_tools.load_user_module(self.cfg, 'data')
        if user_data_module is not None:
            self.data = user_data_module.Data(self.cfg)
        else:  # use the built-in
            self.data = data.BaseData(self.cfg)

        # start a client
        user_client_module = config_tools.load_user_module(self.cfg, 'client')
        if user_client_module is not None:
            self.client = user_client_module.Client(self.cfg)
        else:  # use the built-in
            self.client = client.BaseClient(self.cfg)

        # get an epoch run object
        self.epoch_run = EpochRun()


        print('# # # # # # # # # # # # # # # #')

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.tabs = QTabWidget()

        self.protocol_box = QWidget()
        self.protocol_grid = QGridLayout()
        self.protocol_grid.setSpacing(10)
        self.protocol_box.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,
                                            QSizePolicy.MinimumExpanding))
        
        self.protocol_params_scroll_box = QScrollArea()
        self.protocol_params_scroll_box.setWidget(self.protocol_box)
        self.protocol_params_scroll_box.setWidgetResizable(True)

        self.protocol_control_box = QWidget()
        self.protocol_control_box.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,
                                                            QSizePolicy.Fixed))
        self.protocol_control_grid = QGridLayout()

        self.protocol_tab = QWidget()
        self.protocol_tab_layout = QVBoxLayout()
        self.protocol_tab_layout.addWidget(self.protocol_params_scroll_box)
        self.protocol_tab_layout.addWidget(self.protocol_control_box)

        self.data_tab = QWidget()
        self.data_form = QFormLayout()
        self.data_form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.data_form.setLabelAlignment(QtCore.Qt.AlignCenter)

        self.file_tab = QWidget()
        self.file_form = QFormLayout()
        self.file_form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.file_form.setLabelAlignment(QtCore.Qt.AlignCenter)

        self.tabs.addTab(self.protocol_tab, "Main")
        self.tabs.addTab(self.data_tab, "Animal")
        self.tabs.addTab(self.file_tab, "File")

        self.tabs.resize(450, 500)

        # Status window:
        new_label = QLabel('Status:')
        self.protocol_control_grid.addWidget(new_label, 0, 0)
        self.status_label = QLabel()
        self.status_label.setFrameShadow(QFrame.Shadow(1))
        self.protocol_control_grid.addWidget(self.status_label, 0, 1)
        self.status_label.setText('')

        # Current series counter
        new_label = QLabel('Series counter:')
        self.protocol_control_grid.addWidget(new_label, 0, 2)
        self.series_counter_input = QSpinBox()
        self.series_counter_input.setMinimum(1)
        self.series_counter_input.setMaximum(1000)
        self.series_counter_input.setValue(1)
        self.series_counter_input.valueChanged.connect(self.on_entered_series_count)
        self.protocol_control_grid.addWidget(self.series_counter_input, 0, 3)

        # Epoch count refresh button:
        check_epoch_count_button = QPushButton("Check epochs:", self)
        check_epoch_count_button.clicked.connect(self.on_pressed_button)
        self.protocol_control_grid.addWidget(check_epoch_count_button, 1, 0)
        # Epoch count window:
        self.epoch_count = QLabel()
        self.epoch_count.setFrameShadow(QFrame.Shadow(1))
        self.protocol_control_grid.addWidget(self.epoch_count, 1, 1)
        self.epoch_count.setText('')

        # View button:
        self.view_button = QPushButton("View", self)
        self.view_button.clicked.connect(self.on_pressed_button)
        self.protocol_control_grid.addWidget(self.view_button, 2, 0)

        # Record button:
        self.record_button = QPushButton("Record", self)
        self.record_button.clicked.connect(self.on_pressed_button)
        self.protocol_control_grid.addWidget(self.record_button, 2, 1)

        # Pause/resume button:
        self.pause_button = QPushButton("Pause", self)
        self.pause_button.clicked.connect(self.on_pressed_button)
        self.protocol_control_grid.addWidget(self.pause_button, 2, 2)

        # Stop button:
        stop_button = QPushButton("Stop", self)
        stop_button.clicked.connect(self.on_pressed_button)
        self.protocol_control_grid.addWidget(stop_button, 2, 3)

        # Enter note button:
        note_button = QPushButton("Enter note", self)
        note_button.clicked.connect(self.on_pressed_button)
        self.protocol_control_grid.addWidget(note_button, 3, 0)

        # Notes field:
        self.notes_edit = QTextEdit()
        self.notes_edit.setFixedHeight(30)
        self.protocol_control_grid.addWidget(self.notes_edit, 3, 1, 1, 3)

        # # # TAB 1: MAIN controls, for selecting / playing stimuli
        # Protocol ID drop-down:
        combo_box = QComboBox(self)
        combo_box.addItem("(select a protocol to run)")
        for sub_class in self.available_protocols:
            combo_box.addItem(sub_class.__name__)
        protocol_label = QLabel('Protocol:')
        combo_box.activated[str].connect(self.on_selected_protocol_ID)
        self.protocol_grid.addWidget(protocol_label, 1, 0)
        self.protocol_grid.addWidget(combo_box, 1, 1, 1, 1)

        # Parameter preset drop-down:
        parameter_preset_label = QLabel('Parameter_preset:')
        self.protocol_grid.addWidget(parameter_preset_label, 2, 0)
        self.update_parameter_preset_selector()

        # Save parameter preset button:
        save_preset_button = QPushButton("Save preset", self)
        save_preset_button.clicked.connect(self.on_pressed_button)
        self.protocol_grid.addWidget(save_preset_button, 2, 2)

        # Run paramters input:
        self.update_run_parameters_input()


        # # # TAB 2: Current animal metadata information
        # # Animal info:
        new_label = QLabel('Load existing animal')
        self.existing_animal_input = QComboBox()
        self.existing_animal_input.activated[int].connect(self.on_selected_existing_animal)
        self.data_form.addRow(new_label, self.existing_animal_input)
        self.update_existing_animal_input()

        new_label = QLabel('Current Animal info:')
        new_label.setAlignment(QtCore.Qt.AlignCenter)
        self.data_form.addRow(new_label)

        # Only built-ins are "animal_id," "age" and "notes"
        # Animal ID:
        new_label = QLabel('Animal ID:')
        self.animal_id_input = QLineEdit()
        self.data_form.addRow(new_label, self.animal_id_input)

        # Age: 
        new_label = QLabel('Age:')
        self.animal_age_input = QSpinBox()
        self.animal_age_input.setMinimum(0)
        self.animal_age_input.setValue(1)
        self.data_form.addRow(new_label, self.animal_age_input)

        # Notes: 
        new_label = QLabel('Notes:')
        self.animal_notes_input = QTextEdit()
        self.data_form.addRow(new_label, self.animal_notes_input)

        # Use user cfg to populate other metadata options
        self.animal_metadata_inputs = {}
        ct = 0
        for key in self.cfg['animal_metadata']:
            if key == 'transgenes':
                pass
            else:
                ct += 1
                new_label = QLabel(key)
                new_input = QComboBox()
                for choiceID in self.cfg['animal_metadata'][key]:
                    new_input.addItem(choiceID)
                self.data_form.addRow(new_label, new_input)

                self.animal_metadata_inputs[key] = new_input
            
        new_label = QLabel('Transgenes')
        self.data_form.addRow(new_label)

        # Create animal button
        create_animal_button = QPushButton("Create animal", self)
        create_animal_button.clicked.connect(self.on_created_animal)
        self.data_form.addRow(create_animal_button)

        # # # TAB 3: FILE tab - init, load, close etc. h5 file
        # Data file info
        # Initialize new experiment button
        initialize_button = QPushButton("Initialize experiment", self)
        initialize_button.clicked.connect(self.on_pressed_button)
        new_label = QLabel('Current data file:')
        self.file_form.addRow(initialize_button, new_label)
        # Load existing experiment button
        load_button = QPushButton("Load experiment", self)
        load_button.clicked.connect(self.on_pressed_button)
        # Label with current expt file
        self.current_experiment_label = QLabel('')
        self.file_form.addRow(load_button, self.current_experiment_label)

        # # # # Data browser: # # # # # # # #
        self.group_tree = QTreeWidget(self)
        self.group_tree.setHeaderHidden(True)
        self.group_tree.itemClicked.connect(self.on_tree_item_clicked)
        self.file_form.addRow(self.group_tree)

        # Attribute table
        self.table_attributes = QTableWidget()
        self.table_attributes.setStyleSheet("")
        self.table_attributes.setColumnCount(2)
        self.table_attributes.setObjectName("table_attributes")
        self.table_attributes.setRowCount(0)
        item = QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(10)
        item.setFont(font)
        item.setBackground(QtGui.QColor(121, 121, 121))
        brush = QtGui.QBrush(QtGui.QColor(91, 91, 91))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setForeground(brush)
        self.table_attributes.setHorizontalHeaderItem(0, item)
        item = QTableWidgetItem()
        item.setBackground(QtGui.QColor(123, 123, 123))
        brush = QtGui.QBrush(QtGui.QColor(91, 91, 91))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setForeground(brush)
        self.table_attributes.setHorizontalHeaderItem(1, item)
        self.table_attributes.horizontalHeader().setCascadingSectionResizes(True)
        self.table_attributes.horizontalHeader().setDefaultSectionSize(200)
        self.table_attributes.horizontalHeader().setHighlightSections(False)
        self.table_attributes.horizontalHeader().setSortIndicatorShown(True)
        self.table_attributes.horizontalHeader().setStretchLastSection(True)
        self.table_attributes.verticalHeader().setVisible(False)
        self.table_attributes.verticalHeader().setHighlightSections(False)
        self.table_attributes.setMinimumSize(QtCore.QSize(200, 400))
        item = self.table_attributes.horizontalHeaderItem(0)
        item.setText("Attribute")
        item = self.table_attributes.horizontalHeaderItem(1)
        item.setText("Value")

        self.table_attributes.itemChanged.connect(self.update_attrs_to_file)

        self.file_form.addRow(self.table_attributes)

        # Add all layouts to window
        self.layout.addWidget(self.tabs)
        self.protocol_tab.setLayout(self.protocol_tab_layout)
        self.protocol_control_box.setLayout(self.protocol_control_grid)
        self.protocol_box.setLayout(self.protocol_grid)
        self.data_tab.setLayout(self.data_form)
        self.file_tab.setLayout(self.file_form)
        self.setWindowTitle('Visprotocol')

        # Resize window based on protocol tab
        self.update_window_width()

        self.show()

    def on_selected_protocol_ID(self, text):
        if text == "(select a protocol to run)":
            return
        # Clear old params list from grid
        self.reset_layout()

        # initialize the selected protocol object
        prot_names = [x.__name__ for x in self.available_protocols]
        self.protocol_object = self.available_protocols[prot_names.index(text)](self.cfg)

        # update display lists of run & protocol parameters
        self.protocol_object.load_parameter_presets()
        self.update_parameter_preset_selector()
        self.update_protocol_parameters_input()
        self.update_run_parameters_input()
        self.update_window_width()
        self.show()

    def on_pressed_button(self):
        sender = self.sender()
        if sender.text() == 'Record':
            if (self.data.experiment_file_exists() and self.data.current_animal_exists()):
                self.send_run(save_metadata_flag=True)
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
            self.send_run(save_metadata_flag=False)
            self.pause_button.setText('Pause')

        elif sender.text() == 'Pause':
            self.epoch_run.pause_run()
            self.pause_button.setText('Resume')
            self.status_label.setText('Paused...')
            self.show()

        elif sender.text() == 'Resume':
            self.epoch_run.resume_run()
            self.pause_button.setText('Pause')
            self.status_label.setText('Viewing...')
            self.show()

        elif sender.text() == 'Stop':
            self.epoch_run.stop_run()
            self.pause_button.setText('Pause')

        elif sender.text() == 'Enter note':
            self.note_text = self.notes_edit.toPlainText()
            if self.data.experiment_file_exists() is True:
                self.data.create_note(self.note_text)  # save note to expt file
                self.notes_edit.clear()  # clear notes box
            else:
                self.notes_edit.setTextColor(QtGui.QColor("Red"))

        elif sender.text() == 'Save preset':
            self.update_parameters_from_fillable_fields()  # get the state of the param input from GUI
            start_name = self.parameter_preset_comboBox.currentText()
            if start_name == 'Default':
                start_name = ''

            text, _ = QInputDialog.getText(self, "Save preset", "Preset Name:", QLineEdit.Normal, start_name)

            self.protocol_object.update_parameter_presets(text)

        elif sender.text() == 'Initialize experiment':
            dialog = QDialog()

            dialog.ui = InitializeExperimentGUI(parent=dialog)
            dialog.ui.setupUI(self, dialog)
            dialog.setFixedSize(300, 200)
            dialog.exec_()

            self.data.experiment_file_name = dialog.ui.le_filename.text()
            self.data.data_directory = dialog.ui.le_data_directory.text()
            self.data.experimenter = dialog.ui.le_experimenter.text()

            self.update_existing_animal_input()
            self.populate_groups()

        elif sender.text() == 'Load experiment':
            if os.path.isdir(self.data.data_directory):
                filePath, _ = QFileDialog.getOpenFileName(self, "Open file", self.data.data_directory)
            else:
                filePath, _ = QFileDialog.getOpenFileName(self, "Open file")
            self.data.experiment_file_name = os.path.split(filePath)[1].split('.')[0]
            self.data.data_directory = os.path.split(filePath)[0]

            if self.data.experiment_file_name != '':
                self.current_experiment_label.setText(self.data.experiment_file_name)
                # update series count to reflect already-collected series
                self.data.reload_series_count()
                self.series_counter_input.setValue(self.data.get_highest_series_count() + 1)
                self.update_existing_animal_input()
                self.populate_groups()

        elif sender.text() == 'Check epochs:':
            self.epoch_count.setText(str(self.protocol_object.num_epochs_completed))

    def on_created_animal(self):
        # Populate animal metadata from animal data fields
        animal_metadata = {}
        # Built-ins
        animal_metadata['animal_id'] = self.animal_id_input.text()
        animal_metadata['age'] = self.animal_age_input.value()
        animal_metadata['notes'] = self.animal_notes_input.toPlainText()

        # user-defined:
        for key in self.animal_metadata_inputs:
            animal_metadata[key] = self.animal_metadata_inputs[key].currentText()

        self.data.create_animal(animal_metadata)  # creates new animal and selects it as the current animal
        self.update_existing_animal_input()

    def reset_layout(self):
        for ii in range(3, self.protocol_grid.rowCount()):
            item = self.protocol_grid.itemAtPosition(ii, 0)
            if item is not None:
                item.widget().deleteLater()
            item = self.protocol_grid.itemAtPosition(ii, 1)
            if item is not None:
                item.widget().deleteLater()
        self.show()

    def update_protocol_parameters_input(self):
        # update display window to show parameters for this protocol
        new_label = QLabel('Protocol parameters:')
        self.protocol_grid.addWidget(new_label, self.run_params_ct + 3, 0)
        
        self.protocol_parameter_input = {}  # clear old input params dict
        ct = 0
        for key, value in self.protocol_object.protocol_parameters.items():
            ct += 1
            new_label = QLabel(key + ':')
            row_offset = self.run_params_ct + 4 + ct
            self.protocol_grid.addWidget(new_label, row_offset, 0)

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
            self.protocol_grid.addWidget(self.protocol_parameter_input[key], row_offset, 1, 1, 2)


    def update_parameter_preset_selector(self):
        self.parameter_preset_comboBox = QComboBox(self)
        self.parameter_preset_comboBox.addItem("Default")
        for name in self.protocol_object.parameter_presets.keys():
            self.parameter_preset_comboBox.addItem(name)
        self.parameter_preset_comboBox.activated[str].connect(self.on_selected_parameter_preset)
        self.protocol_grid.addWidget(self.parameter_preset_comboBox, 2, 1, 1, 1)

    def on_selected_parameter_preset(self, text):
        self.protocol_object.select_protocol_preset(text)
        self.reset_layout()
        self.update_protocol_parameters_input()
        self.update_run_parameters_input()
        self.show()

    def on_selected_existing_animal(self, index):
        animal_data = self.data.get_existing_animal_data()
        self.populate_animal_metadata_fields(animal_data[index])
        self.data.current_animal = animal_data[index].get('animal_id')

    def update_existing_animal_input(self):
        self.existing_animal_input.clear()
        for animal_data in self.data.get_existing_animal_data():
            self.existing_animal_input.addItem(animal_data['animal_id'])
        index = self.existing_animal_input.findText(self.data.current_animal)
        if index >= 0:
            self.existing_animal_input.setCurrentIndex(index)

    def populate_animal_metadata_fields(self, animal_data_dict):
        self.animal_id_input.setText(animal_data_dict['animal_id'])
        self.animal_age_input.setValue(animal_data_dict['age'])
        self.animal_notes_input.setText(animal_data_dict['notes'])
        for key in self.animal_metadata_inputs:
            self.animal_metadata_inputs[key].setCurrentText(animal_data_dict[key])

    def update_run_parameters_input(self):
        self.run_params_ct = 0
        self.run_parameter_input = {}  # clear old input params dict
        
        # Run parameters list
        for key, value in self.protocol_object.run_parameters.items():
            if key not in ['protocol_ID', 'run_start_time']:
                self.run_params_ct += 1
                # delete existing labels:
                item = self.protocol_grid.itemAtPosition(2 + self.run_params_ct, 0)
                if item is not None:
                    item.widget().deleteLater()

                # write new labels:
                new_label = QLabel(key + ':')
                self.protocol_grid.addWidget(new_label, 2 + self.run_params_ct, 0)

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

    def on_entered_series_count(self):
        self.data.update_series_count(self.series_counter_input.value())
        if self.data.experiment_file_exists() is True:
            if self.data.get_series_count() <= self.data.get_highest_series_count():
                self.series_counter_input.setStyleSheet("background-color: rgb(255, 0, 0);")
            else:
                self.series_counter_input.setStyleSheet("background-color: rgb(255, 255, 255);")

    def send_run(self, save_metadata_flag=True):
        # check to make sure a protocol has been selected
        if self.protocol_object.run_parameters['protocol_ID'] == '':
            self.status_label.setText('Select a protocol')
            return  # no protocol exists, don't send anything

        # check to make sure the series count does not already exist
        if save_metadata_flag:
            self.data.update_series_count(self.series_counter_input.value())
            if (self.data.get_series_count() in self.data.get_existing_series()):
                self.series_counter_input.setStyleSheet("background-color: rgb(255, 0, 0);")
                self.status_label.setText('Select an unused series number')
                return  # group already exists, don't send anything
            else:
                self.series_counter_input.setStyleSheet("background-color: rgb(255, 255, 255);")

        # Populate parameters from filled fields
        self.update_parameters_from_fillable_fields()

        # start the epoch run thread:
        self.run_series_thread = runSeriesThread(self.epoch_run,
                                               self.protocol_object,
                                               self.data,
                                               self.client,
                                               save_metadata_flag)

        self.run_series_thread.finished.connect(lambda: self.run_finished(save_metadata_flag))
        self.run_series_thread.started.connect(lambda: self.run_started(save_metadata_flag))

        self.run_series_thread.start()

    def run_started(self, save_metadata_flag):
        # Lock the view and run buttons to prevent spinning up multiple threads
        self.view_button.setEnabled(False)
        self.record_button.setEnabled(False)
        if save_metadata_flag:
            self.status_label.setText('Recording series ' + str(self.data.get_series_count()))
        else:
            self.status_label.setText('Viewing...')

    def run_finished(self, save_metadata_flag):
        # re-enable view/record buttons
        self.view_button.setEnabled(True)
        self.record_button.setEnabled(True)

        self.status_label.setText('Ready')
        self.pause_button.setText('Pause')
        if save_metadata_flag:
            self.update_existing_animal_input()
            # Advance the series_count:
            self.data.advance_series_count()
            self.series_counter_input.setValue(self.data.get_series_count())
            self.populate_groups()

    def update_parameters_from_fillable_fields(self):
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

    def populate_groups(self):
        file_path = os.path.join(self.data.data_directory, self.data.experiment_file_name + '.hdf5')
        group_dset_dict = h5io.get_hierarchy(file_path, additional_exclusions='rois')
        self._populateTree(self.group_tree, group_dset_dict)

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

    def on_tree_item_clicked(self, item, column):
        file_path = os.path.join(self.data.data_directory, self.data.experiment_file_name + '.hdf5')
        group_path = h5io.get_path_from_tree_item(self.group_tree.selectedItems()[0])

        if group_path != '':
            attr_dict = h5io.get_attributes_from_group(file_path, group_path)
            if 'series' in group_path.split('/')[-1]:
                editable_values = False  # don't let user edit epoch parameters
            else:
                editable_values = True
            self.populate_attrs(attr_dict = attr_dict, editable_values = editable_values)

    def populate_attrs(self, attr_dict=None, editable_values=False):
        """ Populate attribute for currently selected group """
        self.table_attributes.blockSignals(True)  # block udpate signals for auto-filled forms
        self.table_attributes.setRowCount(0)
        self.table_attributes.setColumnCount(2)
        self.table_attributes.setSortingEnabled(False)

        if attr_dict:
            for num, key in enumerate(attr_dict):
                self.table_attributes.insertRow(self.table_attributes.rowCount())
                key_item = QTableWidgetItem(key)
                key_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.table_attributes.setItem(num, 0, key_item)

                val_item = QTableWidgetItem(str(attr_dict[key]))
                if editable_values:
                    val_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
                else:
                    val_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.table_attributes.setItem(num, 1, val_item)

        self.table_attributes.blockSignals(False)

    def update_attrs_to_file(self, item):
        file_path = os.path.join(self.data.data_directory, self.data.experiment_file_name + '.hdf5')
        group_path = h5io.get_path_from_tree_item(self.group_tree.selectedItems()[0])

        attr_key = self.table_attributes.item(item.row(), 0).text()
        attr_val = item.text()

        # update attr in file
        h5io.change_attribute(file_path, group_path, attr_key, attr_val)
        print('Changed attr {} to = {}'.format(attr_key, attr_val))

    def update_window_width(self):
        self.resize(100, self.height())
        window_width = self.protocol_box.sizeHint().width() + self.protocol_params_scroll_box.verticalScrollBar().sizeHint().width() + 40
        self.resize(window_width, self.height())

# # # Other accessory classes. For data file initialization and threading # # # #
class InitializeExperimentGUI(QWidget):
    def setupUI(self, experiment_gui_object, parent=None):
        super(InitializeExperimentGUI, self).__init__(parent)
        self.parent = parent
        self.experiment_gui_object = experiment_gui_object
        layout = QFormLayout()

        label_filename = QLabel('File Name:')
        init_now = datetime.now()
        defaultName = init_now.isoformat()[:-16]
        self.le_filename = QLineEdit(defaultName)
        layout.addRow(label_filename, self.le_filename)

        select_directory_button = QPushButton("Select Directory...", self)
        select_directory_button.clicked.connect(self.on_pressed_directory_button)
        self.le_data_directory = QLineEdit(config_tools.get_data_directory(self.experiment_gui_object.cfg))
        layout.addRow(select_directory_button, self.le_data_directory)

        label_experimenter = QLabel('Experimenter:')
        self.le_experimenter = QLineEdit(config_tools.get_experimenter(self.experiment_gui_object.cfg))
        layout.addRow(label_experimenter, self.le_experimenter)

        self.label_status = QLabel('Enter experiment info')
        layout.addRow(self.label_status)

        enter_button = QPushButton("Enter", self)
        enter_button.clicked.connect(self.on_pressed_enter_button)
        layout.addRow(enter_button)

        self.setLayout(layout)

    def on_pressed_enter_button(self):
        self.experiment_gui_object.data.experiment_file_name = self.le_filename.text()
        self.experiment_gui_object.data.data_directory = self.le_data_directory.text()
        self.experiment_gui_object.data.experimenter = self.le_experimenter.text()

        if os.path.isfile(os.path.join(self.experiment_gui_object.data.data_directory, self.experiment_gui_object.data.experiment_file_name) + '.hdf5'):
           self.label_status.setText('Experiment file already exists!')
        elif not os.path.isdir(self.experiment_gui_object.data.data_directory):
            self.label_status.setText('Data directory does not exist!')
        else:
            self.label_status.setText('Data entered')
            self.experiment_gui_object.current_experiment_label.setText(self.experiment_gui_object.data.experiment_file_name)
            self.experiment_gui_object.data.initialize_experiment_file()
            self.experiment_gui_object.series_counter_input.setValue(1)
            self.close()
            self.parent.close()

    def on_pressed_directory_button(self):
        if os.path.isdir(self.experiment_gui_object.data.data_directory):
            filepath = str(QFileDialog.getExistingDirectory(self, "Select Directory", self.experiment_gui_object.data.data_directory))
        else:
            filepath = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        
        self.le_data_directory.setText(filepath)

class InitializeRigGUI(QWidget):
    def setupUI(self, experiment_gui_object, parent=None):
        super(InitializeRigGUI, self).__init__(parent)
        self.parent = parent
        self.experiment_gui_object = experiment_gui_object

        self.cfg_name = None
        self.cfg = None
        self.available_rig_configs = []

        self.layout = QFormLayout()
        self.resize(200, 400)

        label_config = QLabel('Config')
        self.config_combobox = QComboBox()
        self.config_combobox.activated.connect(self.on_selected_config)
        for choiceID in config_tools.get_available_config_files():
            self.config_combobox.addItem(choiceID)
        self.layout.addRow(label_config, self.config_combobox)

        label_rigname = QLabel('Rig Config:')
        self.rig_combobox = QComboBox()
        self.rig_combobox.activated.connect(self.on_selected_rig)
        self.layout.addRow(label_rigname, self.rig_combobox)
        self.update_available_rigs()

        self.setLayout(self.layout)
        self.show()

    def update_available_rigs(self):
        self.rig_combobox.clear()
        for choiceID in self.available_rig_configs:
            self.rig_combobox.addItem(choiceID)

    def on_selected_config(self):
        self.cfg_name = self.config_combobox.currentText()
        self.cfg = config_tools.get_configuration_file(self.cfg_name)
        self.available_rig_configs = config_tools.get_available_rig_configs(self.cfg)
        self.update_available_rigs()
        self.show()

    def on_selected_rig(self):
        # Store the rig and cfg names in the cfg dict
        self.cfg['current_rig_name'] = self.rig_combobox.currentText()
        self.cfg['current_cfg_name'] = self.cfg_name

        # Pass cfg up to experiment GUI object
        self.experiment_gui_object.cfg = self.cfg

        self.close()
        self.parent.close()


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

    def _send_run(self):
        self.epoch_run.start_run(self.protocol_object, self.data, self.client, save_metadata_flag=self.save_metadata_flag)

    def run(self):
        self._send_run()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ExperimentGUI()
    sys.exit(app.exec())
