#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data file class

Data File structure is:
yyyy-mm-dd
    Client
    Animals
        animal_id
            epoch_runs
                series_00n (attrs = protocol_parameters)
                    acquisition
                    epochs
                        epoch_001
                        epoch_002
                    stimulus_timing
    Notes

"""
import h5py
import os
from datetime import datetime
import numpy as np

from visprotocol.util import config_tools


class BaseData():
    def __init__(self, cfg):
        self.cfg = cfg

        self.experiment_file_name = None
        self.series_count = 1
        self.animal_metadata = {}  # populated in GUI or user protocol
        self.current_animal = None

        # default data_directory, experiment_file_name, experimenter from cfg
        # may be overwritten by GUI or other before initialize_experiment_file() is called
        self.data_directory = config_tools.get_data_directory(self.cfg)
        self.experiment_file_name = datetime.now().isoformat()[:-16]
        self.experimenter = config_tools.get_experimenter(self.cfg)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # #  Creating experiment file and groups  # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def initialize_experiment_file(self):
        """
        Create HDF5 data file and initialize top-level hierarchy nodes
        """
        with h5py.File(os.path.join(self.data_directory, self.experiment_file_name + '.hdf5'), 'w-') as experiment_file:
            # Experiment date/time
            init_now = datetime.now()
            date = init_now.isoformat()[:-16]
            init_time = init_now.strftime("%H:%M:%S")

            # Write experiment metadata as top-level attributes
            experiment_file.attrs['date'] = date
            experiment_file.attrs['init_time'] = init_time
            experiment_file.attrs['data_directory'] = self.data_directory
            experiment_file.attrs['experimenter'] = self.experimenter
            experiment_file.attrs['rig_config'] = self.cfg.get('current_rig_name', '')
            rig_config = self.cfg.get('rig_config').get(self.cfg.get('current_rig_name'))
            for key in rig_config:
                experiment_file.attrs[key] = rig_config.get(key)

            # Create a top-level group for epoch runs and user-entered notes
            experiment_file.create_group('Animals')
            experiment_file.create_group('Notes')
            
    def create_animal(self, animal_metadata):
        """
        """
        if animal_metadata.get('animal_id') in [x.get('animal_id') for x in self.get_existing_animal_data()]:
            print('A animal with this ID already exists')
            return

        if self.experiment_file_exists():
            with h5py.File(os.path.join(self.data_directory, self.experiment_file_name + '.hdf5'), 'r+') as experiment_file:
                animal_init_time = datetime.now().strftime('%H:%M:%S.%f')[:-4]
                animals_group = experiment_file['/Animals']
                new_animal = animals_group.create_group(animal_metadata.get('animal_id'))
                new_animal.attrs['init_time'] = animal_init_time
                for key in animal_metadata:
                    new_animal.attrs[key] = animal_metadata.get(key)

                new_animal.create_group('epoch_runs')

            self.select_animal(animal_metadata.get('animal_id'))
            print('Created animal {}'.format(animal_metadata.get('animal_id')))
        else:
            print('Initialize a data file before defining a animal')

    def create_epoch_run(self, protocol_object):
        """"
        """
        # create a new epoch run group in the data file
        if (self.current_animal_exists() and self.experiment_file_exists()):
            with h5py.File(os.path.join(self.data_directory, self.experiment_file_name + '.hdf5'), 'r+') as experiment_file:
                run_start_time = datetime.now().strftime('%H:%M:%S.%f')[:-4]
                animal_group = experiment_file['/Animals/{}/epoch_runs'.format(self.current_animal)]
                new_epoch_run = animal_group.create_group('series_{}'.format(str(self.series_count).zfill(3)))
                new_epoch_run.attrs['run_start_time'] = run_start_time
                for key in protocol_object.run_parameters:  # add run parameter attributes
                    new_epoch_run.attrs[key] = protocol_object.run_parameters[key]

                for key in protocol_object.protocol_parameters:  # add user-entered protocol params
                    new_epoch_run.attrs[key] = protocol_object.protocol_parameters[key]

                # add subgroups:
                new_epoch_run.create_group('acquisition')
                new_epoch_run.create_group('epochs')
                new_epoch_run.create_group('stimulus_timing')

        else:
            print('Create a data file and/or define a animal first')

    def create_epoch(self, protocol_object):
        """
        """
        if (self.current_animal_exists() and self.experiment_file_exists()):
            with h5py.File(os.path.join(self.data_directory, self.experiment_file_name + '.hdf5'), 'r+') as experiment_file:
                epoch_time = datetime.now().strftime('%H:%M:%S.%f')
                epoch_run_group = experiment_file['/Animals/{}/epoch_runs/series_{}/epochs'.format(self.current_animal, str(self.series_count).zfill(3))]
                new_epoch = epoch_run_group.create_group('epoch_{}'.format(str(protocol_object.num_epochs_completed+1).zfill(3)))
                new_epoch.attrs['epoch_time'] = epoch_time

                epoch_parameters_group = new_epoch
                if type(protocol_object.epoch_parameters) is tuple:  # stimulus is tuple of multiple stims layered on top of one another
                    num_stims = len(protocol_object.epoch_parameters)
                    for stim_ind in range(num_stims):
                        for key in protocol_object.epoch_parameters[stim_ind]:
                            prefix = 'stim{}_'.format(str(stim_ind))
                            epoch_parameters_group.attrs[prefix + key] = hdf5ify_parameter(protocol_object.epoch_parameters[stim_ind][key])

                elif type(protocol_object.epoch_parameters) is dict:  # single stim class
                    for key in protocol_object.epoch_parameters:
                        epoch_parameters_group.attrs[key] = hdf5ify_parameter(protocol_object.epoch_parameters[key])

                convenience_parameters_group = new_epoch
                for key in protocol_object.convenience_parameters:  # save out convenience parameters
                    convenience_parameters_group.attrs[key] = hdf5ify_parameter(protocol_object.convenience_parameters[key])

        else:
            print('Create a data file and/or define a animal first')

    def create_note(self, noteText):
        ""
        ""
        if self.experiment_file_exists():
            with h5py.File(os.path.join(self.data_directory, self.experiment_file_name + '.hdf5'), 'r+') as experiment_file:
                noteTime = datetime.now().strftime('%H:%M:%S.%f')[:-4]
                notes = experiment_file['/Notes']
                notes.attrs[noteTime] = noteText
        else:
            print('Initialize a data file before writing a note')

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # #  Retrieve / query data file # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def experiment_file_exists(self):
        if self.experiment_file_name is None:
            tf = False
        else:
            tf = os.path.isfile(os.path.join(self.data_directory, self.experiment_file_name + '.hdf5'))
        return tf

    def current_animal_exists(self):
        if self.current_animal is None:
            tf = False
        else:
            tf = True
        return tf

    def get_existing_series(self):
        all_series = []
        with h5py.File(os.path.join(self.data_directory, self.experiment_file_name + '.hdf5'), 'r') as experiment_file:
            for animal_id in list(experiment_file['/Animals'].keys()):
                new_series = list(experiment_file['/Animals/{}/epoch_runs'.format(animal_id)].keys())
                all_series.append(new_series)
        all_series = [val for s in all_series for val in s]
        series = [int(x.split('_')[-1]) for x in all_series]
        return series

    def get_highest_series_count(self):
        series = self.get_existing_series()
        if len(series) == 0:
            return 0
        else:
            return np.max(series)

    def get_existing_animal_data(self):
        # return list of dicts for animal metadata already present in experiment file
        animal_data_list = []
        if self.experiment_file_exists():
            with h5py.File(os.path.join(self.data_directory, self.experiment_file_name + '.hdf5'), 'r') as experiment_file:
                for animal in experiment_file['/Animals']:
                    new_animal = experiment_file['/Animals'][animal]
                    new_dict = {}
                    for at in new_animal.attrs:
                        new_dict[at] = new_animal.attrs[at]

                    animal_data_list.append(new_dict)
        return animal_data_list

    def select_animal(self, animal_id):
        self.current_animal = animal_id

    def advance_series_count(self):
        self.series_count += 1

    def update_series_count(self, val):
        self.series_count = val

    def get_series_count(self):
        return self.series_count

    def reload_series_count(self):
        all_series = []
        with h5py.File(os.path.join(self.data_directory, self.experiment_file_name + '.hdf5'), 'r') as experiment_file:
            for animal_id in list(experiment_file['/Animals'].keys()):
                new_series = list(experiment_file['/Animals/{}/epoch_runs'.format(animal_id)].keys())
                all_series.append(new_series)
        all_series = [val for s in all_series for val in s]
        series = [int(x.split('_')[-1]) for x in all_series]

        if len(series) == 0:
            self.series_count = 0 + 1
        else:
            self.series_count = np.max(series) + 1


def hdf5ify_parameter(value):
    if value is None:
        value = 'None'
    if type(value) is dict:  # TODO: Find a way to split this into subgroups. Hacky work around.
        value = str(value)
    if type(value) is np.str_:
        value = str(value)

    return value
