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
from datetime import datetime, timezone
import numpy as np


class Data():
    def __init__(self, cfg):
        self.experiment_file_name = None
        self.series_count = 1
        self.fly_metadata = {}  # populated in GUI or user protocol
        self.current_fly = None
        self.user_name = cfg.get('user_name')
        self.rig_name = cfg.get('rig_name')
        self.cfg = cfg

        # # # Metadata defaults # # #
        self.experimenter = self.cfg.get('experimenter', '')

        # # #  Lists of fly metadata # # #
        self.prepChoices = self.cfg.get('prep_choices', [])
        self.driverChoices = self.cfg.get('driver_choices', [])
        self.indicatorChoices = self.cfg.get('indicator_choices', [])
        self.effectorChoices = self.cfg.get('effector_choices', [])

        # load rig-specific metadata things
        self.data_directory = self.cfg.get('rig_config').get(self.rig_name).get('data_directory', os.getcwd())
        self.rig = self.cfg.get('rig_config').get(self.rig_name).get('rig', '(rig)')
        self.screen_center = self.cfg.get('rig_config').get(self.rig_name).get('screen_center', [0, 0])

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
            init_unix_time = init_now.astimezone(timezone.utc).timestamp()

            # Write experiment metadata as top-level attributes
            experiment_file.attrs['date'] = date
            experiment_file.attrs['init_time'] = init_time
            experiment_file.attrs['init_unix_time'] = init_unix_time
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
                fly_init_now = datetime.now()
                fly_init_time = fly_init_now.strftime('%H:%M:%S.%f')[:-4]
                fly_init_unix_time = fly_init_now.astimezone(timezone.utc).timestamp()
                flies_group = experiment_file['/Flies']
                new_fly = flies_group.create_group(fly_metadata.get('fly_id'))
                new_fly.attrs['init_time'] = fly_init_time
                new_fly.attrs['init_unix_time'] = fly_init_unix_time
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
                run_start_now = datetime.now()
                run_start_time = run_start_now.strftime('%H:%M:%S.%f')[:-4]
                run_start_unix_time = run_start_now.astimezone(timezone.utc).timestamp()
                fly_group = experiment_file['/Flies/{}/epoch_runs'.format(self.current_fly)]
                new_epoch_run = fly_group.create_group('series_{}'.format(str(self.series_count).zfill(3)))
                new_epoch_run.attrs['run_start_time'] = run_start_time
                new_epoch_run.attrs['run_start_unix_time'] = run_start_unix_time
                for key in protocol_object.run_parameters:  # add run parameter attributes
                    new_epoch_run.attrs[key] = protocol_object.run_parameters[key]

                for key in protocol_object.protocol_parameters:  # add user-entered protocol params
                    new_epoch_run.attrs[key] = protocol_object.protocol_parameters[key]

                # add subgroups:
                new_epoch_run.create_group('acquisition')
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
                epoch_now = datetime.now()
                epoch_time = epoch_now.strftime('%H:%M:%S.%f')
                epoch_unix_time = epoch_now.astimezone(timezone.utc).timestamp()
                epoch_run_group = experiment_file['/Flies/{}/epoch_runs/series_{}/epochs'.format(self.current_fly, str(self.series_count).zfill(3))]
                new_epoch = epoch_run_group.create_group('epoch_{}'.format(str(protocol_object.num_epochs_completed+1).zfill(3)))
                new_epoch.attrs['epoch_time'] = epoch_time
                new_epoch.attrs['epoch_unix_time'] = epoch_unix_time

                epochParametersGroup = new_epoch
                if type(protocol_object.epoch_parameters) is tuple:  # stimulus is tuple of multiple stims layered on top of one another
                    num_stims = len(protocol_object.epoch_parameters)
                    for stim_ind in range(num_stims):
                        for key in protocol_object.epoch_parameters[stim_ind]:
                            prefix = 'stim{}_'.format(str(stim_ind))
                            epochParametersGroup.attrs[prefix + key] = hdf5ifyParameter(protocol_object.epoch_parameters[stim_ind][key])

                elif type(protocol_object.epoch_parameters) is dict:  # single stim class
                    for key in protocol_object.epoch_parameters:
                        epochParametersGroup.attrs[key] = hdf5ifyParameter(protocol_object.epoch_parameters[key])

                convenienceParametersGroup = new_epoch
                for key in protocol_object.convenience_parameters:  # save out convenience parameters
                    convenienceParametersGroup.attrs[key] = hdf5ifyParameter(protocol_object.convenience_parameters[key])

        else:
            print('Create a data file and/or define a fly first')

    def endEpoch(self, protocol_object):
        """
        Save the timestamp when the epoch ends
        """
        with h5py.File(os.path.join(self.data_directory, self.experiment_file_name + '.hdf5'), 'r+') as experiment_file:
            epoch_end_now = datetime.now()
            epoch_end_time = epoch_end_now.strftime('%H:%M:%S.%f')
            epoch_end_unix_time = epoch_end_now.astimezone(timezone.utc).timestamp()
            epoch_run_group = experiment_file['/Flies/{}/epoch_runs/series_{}/epochs'.format(self.current_fly, str(self.series_count).zfill(3))]
            epoch_group = epoch_run_group['epoch_{}'.format(str(protocol_object.num_epochs_completed+1).zfill(3))]
            epoch_group.attrs['epoch_end_time'] = epoch_end_time
            epoch_group.attrs['epoch_end_unix_time'] = epoch_end_unix_time

    def createNote(self, noteText):
        ""
        ""
        if self.experimentFileExists():
            with h5py.File(os.path.join(self.data_directory, self.experiment_file_name + '.hdf5'), 'r+') as experiment_file:
                note_now = datetime.now()
                note_time = note_now.strftime('%H:%M:%S.%f')[:-4]
                note_unix_time = note_now.astimezone(timezone.utc).timestamp()
                notes = experiment_file['/Notes']
                notes.attrs[note_time] = f'[{note_unix_time}] {noteText}'
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

    def updateSeriesCount(self, val):
        self.series_count = val

    def getSeriesCount(self):
        return self.series_count

    def reloadSeriesCount(self):
        all_series = []
        with h5py.File(os.path.join(self.data_directory, self.experiment_file_name + '.hdf5'), 'r') as experiment_file:
            for fly_id in list(experiment_file['/Flies'].keys()):
                new_series = list(experiment_file['/Flies/{}/epoch_runs'.format(fly_id)].keys())
                all_series.append(new_series)
        all_series = [val for s in all_series for val in s]
        series = [int(x.split('_')[-1]) for x in all_series]

        if len(series) == 0:
            self.series_count = 0 + 1
        else:
            self.series_count = np.max(series) + 1


class AODscopeData(Data):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.poi_scan = True
        self.poi_count = 1
        self.xyt_count = 1

    def advanceSeriesCount(self):
        self.series_count += 1
        if self.poi_scan:
            self.poi_count += 1
        else:
            self.xyt_count += 1

    def updateSeriesCount(self, val):
        if self.poi_scan:
            self.poi_count = val
        else:
            self.xyt_count = val

    def getSeriesCount(self):
        if self.poi_scan:
            return self.poi_count
        else:
            return self.xyt_count

    def getExistingSeries(self):
        poi_series = []
        xyt_series = []
        with h5py.File(os.path.join(self.data_directory, self.experiment_file_name + '.hdf5'), 'r') as experiment_file:
            for fly_id in list(experiment_file['/Flies'].keys()):
                for series_id in experiment_file['/Flies/{}/epoch_runs'.format(fly_id)]:
                    acq_group = experiment_file['/Flies/{}/epoch_runs/{}/acquisition'.format(fly_id, series_id)]
                    if acq_group.attrs['poi_scan']:
                        poi_series.append(acq_group.attrs['poi_count'])
                    else:
                        xyt_series.append(acq_group.attrs['xyt_count'])

        poi_series = [int(x) for x in poi_series]
        xyt_series = [int(x) for x in xyt_series]

        if self.poi_scan:
            return poi_series
        else:
            return xyt_series

    def createEpochRun(self, protocol_object):
        """"
        """
        # create a new epoch run group in the data file
        if (self.currentFlyExists() and self.experimentFileExists()):
            with h5py.File(os.path.join(self.data_directory, self.experiment_file_name + '.hdf5'), 'r+') as experiment_file:
                run_start_now = datetime.now()
                run_start_time = run_start_now.strftime('%H:%M:%S.%f')[:-4]
                run_start_unix_time = run_start_now.astimezone(timezone.utc).timestamp()
                fly_group = experiment_file['/Flies/{}/epoch_runs'.format(self.current_fly)]
                new_epoch_run = fly_group.create_group('series_{}'.format(str(self.series_count).zfill(3)))
                new_epoch_run.attrs['run_start_time'] = run_start_time
                new_epoch_run.attrs['run_start_unix_time'] = run_start_unix_time
                for key in protocol_object.run_parameters:  # add run parameter attributes
                    new_epoch_run.attrs[key] = protocol_object.run_parameters[key]

                for key in protocol_object.protocol_parameters:  # add user-entered protocol params
                    new_epoch_run.attrs[key] = protocol_object.protocol_parameters[key]

                # add subgroups:
                new_epoch_run.create_group('acquisition')
                new_epoch_run.create_group('epochs')
                new_epoch_run.create_group('rois')
                new_epoch_run.create_group('stimulus_timing')

                # AODscope-specific data stuff:
                new_epoch_run['acquisition'].attrs['poi_scan'] = self.poi_scan
                if self.poi_scan:
                    new_epoch_run['acquisition'].attrs['poi_count'] = self.poi_count
                else:
                    new_epoch_run['acquisition'].attrs['xyt_count'] = self.xyt_count
        else:
            print('Create a data file and/or define a fly first')

# %% Useful functions. Outside classes.


def hdf5ifyParameter(value):
    if value is None:
        value = 'None'
    if type(value) is dict:  # TODO: Find a way to split this into subgroups. Hacky work around.
        value = str(value)
    if type(value) is np.str_:
        value = str(value)

    return value
