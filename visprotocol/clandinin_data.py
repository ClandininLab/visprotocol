#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data file class

Data File structure is:
yyyy-mm-dd
    Client
    Flies
        Fly_n
            epoch_runs
                series_00n (attrs = protocol_parameters)
                    acquisition
                    epochs
                        epoch_001 (attrs = epoch_parameters, convenience_parameters)
                        epoch_002
                    rois
                    stimulus_timing
    Notes

"""
import h5py
import os
import inspect
import yaml
from datetime import datetime
import numpy as np
import visprotocol


class Data():
    def __init__(self, user_name, rig_config):
        self.experiment_file_name = None
        self.series_count = 1
        self.fly_metadata = {}  # populated in GUI or user protocol
        self.current_fly = None

        # load user config file based on user name
        path_to_config_file = os.path.join(inspect.getfile(visprotocol).split('visprotocol')[0], 'visprotocol', 'config', user_name + '_config.yaml')
        with open(path_to_config_file, 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)

        # # # Other metadata defaults # # #
        self.experimenter = cfg.get('experimenter', '')

        # # #  Lists of fly metadata # # #
        self.prepChoices = cfg.get('prep_choices', [])
        self.driverChoices = cfg.get('driver_choices', [])
        self.indicatorChoices = cfg.get('indicator_choices', [])

        # load rig-specific metadata things
        self.data_directory = cfg.get('rig_config').get(rig_config).get('data_directory', os.getcwd())
        self.rig = cfg.get('rig_config').get(rig_config).get('rig', '(rig)')
        self.screen_center = cfg.get('rig_config').get(rig_config).get('screen_center', [0, 0])

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # #  Creating experiment file and groups  # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def initializeExperimentFile(self):
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
            experiment_file.attrs['rig'] = self.rig

            # Create a top-level group for epoch runs and user-entered notes
            experiment_file.create_group('Client')
            experiment_file.create_group('Flies')
            experiment_file.create_group('Notes')

    def createFly(self, fly_metadata):
        """
        """
        if fly_metadata.get('fly_id') in [x.get('fly_id') for x in self.getExistingFlyData()]:
            print('A fly with this ID already exists')
            return

        if self.experimentFileExists():
            with h5py.File(os.path.join(self.data_directory, self.experiment_file_name + '.hdf5'), 'r+') as experiment_file:
                fly_init_time = datetime.now().strftime('%H:%M:%S.%f')[:-4]
                flies_group = experiment_file['/Flies']
                new_fly = flies_group.create_group(fly_metadata.get('fly_id'))
                new_fly.attrs['init_time'] = fly_init_time
                for key in fly_metadata:
                    new_fly.attrs[key] = fly_metadata.get(key)

                new_fly.create_group('epoch_runs')

            self.selectFly(fly_metadata.get('fly_id'))
        else:
            print('Initialize a data file before defining a fly')

    def createEpochRun(self, protocol_object):
        """"
        """
        # create a new epoch run group in the data file
        if (self.currentFlyExists() and self.experimentFileExists()):
            with h5py.File(os.path.join(self.data_directory, self.experiment_file_name + '.hdf5'), 'r+') as experiment_file:
                run_start_time = datetime.now().strftime('%H:%M:%S.%f')[:-4]
                fly_group = experiment_file['/Flies/{}/epoch_runs'.format(self.current_fly)]
                new_epoch_run = fly_group.create_group('series_{}'.format(str(self.series_count).zfill(3)))
                new_epoch_run.attrs['run_start_time'] = run_start_time
                for key in protocol_object.run_parameters:  # add run parameter attributes
                    new_epoch_run.attrs[key] = protocol_object.run_parameters[key]

                for key in protocol_object.protocol_parameters:  # add user-entered protocol params
                    new_epoch_run.attrs[key] = protocol_object.protocol_parameters[key]

                # add subgroups:
                new_epoch_run.create_group('epochs')
                new_epoch_run.create_group('rois')
                new_epoch_run.create_group('stimulus_timing')

        else:
            print('Create a data file and/or define a fly first')

    def createEpoch(self, protocol_object):
        """
        """
        if (self.currentFlyExists() and self.experimentFileExists()):
            with h5py.File(os.path.join(self.data_directory, self.experiment_file_name + '.hdf5'), 'r+') as experiment_file:
                epoch_time = datetime.now().strftime('%H:%M:%S.%f')[:-4]
                epoch_run_group = experiment_file['/Flies/{}/epoch_runs/series_{}/epochs'.format(self.current_fly, str(self.series_count).zfill(3))]
                new_epoch = epoch_run_group.create_group('epoch_{}'.format(str(protocol_object.num_epochs_completed+1).zfill(3)))
                new_epoch.attrs['epoch_time'] = epoch_time

                epochParametersGroup = new_epoch
                if type(protocol_object.epoch_parameters) is tuple:  # stimulus is tuple of multiple stims layered on top of one another
                    num_stims = len(protocol_object.epoch_parameters)
                    for stim_ind in range(num_stims):
                        for key in protocol_object.epoch_parameters[stim_ind]:
                            newValue = protocol_object.epoch_parameters[stim_ind][key]
                            if type(newValue) is dict:
                                newValue = str(newValue)
                            prefix = 'stim' + str(stim_ind) + '_'
                            if newValue is None:
                                newValue = 'None'
                            epochParametersGroup.attrs[prefix + key] = newValue

                elif type(protocol_object.epoch_parameters) is dict:
                    for key in protocol_object.epoch_parameters:  # save out epoch parameters
                        newValue = protocol_object.epoch_parameters[key]
                        if type(newValue) is dict:  # TODO: Find a way to split this into subgroups. Hacky work around.
                            newValue = str(newValue)
                        if newValue is None:
                            newValue = 'None'
                        epochParametersGroup.attrs[key] = newValue

                convenienceParametersGroup = new_epoch
                for key in protocol_object.convenience_parameters:  # save out convenience parameters
                    convenienceParametersGroup.attrs[key] = protocol_object.convenience_parameters[key]

        else:
            print('Create a data file and/or define a fly first')

    def createNote(self, noteText):
        ""
        ""
        if self.experimentFileExists():
            with h5py.File(os.path.join(self.data_directory, self.experiment_file_name + '.hdf5'), 'r+') as experiment_file:
                noteTime = datetime.now().strftime('%H:%M:%S.%f')[:-4]
                notes = experiment_file['/Notes']
                notes.attrs[noteTime] = noteText
        else:
            print('Initialize a data file before writing a note')

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # #  Retrieve / query data file # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def experimentFileExists(self):
        if self.experiment_file_name is None:
            tf = False
        else:
            tf = os.path.isfile(os.path.join(self.data_directory, self.experiment_file_name + '.hdf5'))
        return tf

    def currentFlyExists(self):
        if self.current_fly is None:
            tf = False
        else:
            tf = True
        return tf

    def getExistingSeries(self):
        all_series = []
        with h5py.File(os.path.join(self.data_directory, self.experiment_file_name + '.hdf5'), 'r') as experiment_file:
            for fly_id in list(experiment_file['/Flies'].keys()):
                new_series = list(experiment_file['/Flies/{}/epoch_runs'.format(fly_id)].keys())
                all_series.append(new_series)
        all_series = [val for s in all_series for val in s]
        series = [int(x.split('_')[-1]) for x in all_series]
        return series

    def getHighestSeriesCount(self):
        series = self.getExistingSeries()
        if len(series) == 0:
            return 0
        else:
            return np.max(series)

    def getExistingFlyData(self):
        # return list of dicts for fly metadata already present in experiment file
        fly_data_list = []
        if self.experimentFileExists():
            with h5py.File(os.path.join(self.data_directory, self.experiment_file_name + '.hdf5'), 'r') as experiment_file:
                for fly in experiment_file['/Flies']:
                    new_fly = experiment_file['/Flies'][fly]
                    new_dict = {}
                    for at in new_fly.attrs:
                        new_dict[at] = new_fly.attrs[at]

                    fly_data_list.append(new_dict)
        return fly_data_list

    def selectFly(self, fly_id):
        self.current_fly = fly_id

    def advanceSeriesCount(self):
        self.series_count += 1
