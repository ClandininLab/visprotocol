#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data parent class. Override any methods in here in the user data subclass
"""
import h5py
import os
import inspect
import yaml
import socket
from datetime import datetime

import visprotocol

class Data():
    def __init__(self, user_name):
        self.experiment_file = None
        self.experiment_file_name = None
        self.series_count = 1
        self.fly_metadata = {}  # populated in GUI or user protocol
        
        #load user config file based on user name
        path_to_config_file = os.path.join(inspect.getfile(visprotocol).split('visprotocol')[0], 'visprotocol', 'config', user_name + '_config.yaml')
        with open(path_to_config_file, 'r') as ymlfile:
            cfg = yaml.load(ymlfile)

        # # # Other metadata defaults # # #
        self.experimenter = cfg['experimenter']
    
        # # #  Lists of fly metadata # # # 
        self.prepChoices = cfg['prep_choices']
        self.driverChoices = cfg['driver_choices']
        self.indicatorChoices = cfg['indicator_choices']
           
        #load rig-specific metadata things
        if socket.gethostname() == 'DESKTOP-4Q3O7LU':  # AODscope Karthala
            self.data_directory = 'D:/Max/FlystimData'
            self.rig = 'AODscope'
        elif socket.gethostname() == 'USERBRU-I10P5LO':  # Bruker
            self.data_directory = 'E:/Max/FlystimData/'
            self.rig = 'Bruker'
        else:
            self.data_directory = os.getcwd()
            self.rig = '(rig)'

    def initializeExperimentFile(self):
        # Create HDF5 file
        self.experiment_file = h5py.File(os.path.join(self.data_directory, self.experiment_file_name + '.hdf5'), 'w-')
        
        # Experiment date/time
        init_now = datetime.now()
        date = init_now.isoformat()[:-16]
        init_time = init_now.strftime("%H:%M:%S")
        
        # Write experiment metadata as top-level attributes
        self.experiment_file.attrs['date'] = date;
        self.experiment_file.attrs['init_time'] = init_time;
        self.experiment_file.attrs['data_directory'] = self.data_directory;
        self.experiment_file.attrs['experimenter'] = self.experimenter;
        self.experiment_file.attrs['rig'] = self.rig;
        
        # Create a top-level group for epoch runs and user-entered notes
        self.experiment_file.create_group('epoch_runs')
        self.experiment_file.create_group('notes')
        self.experiment_file.close()
        
    def saveEpochRunMetaData(self, protocol_object):
        # create a new epoch run group in the data file
        run_start_time = datetime.now().strftime('%H:%M:%S.%f')[:-4]
        self.reOpenExperimentFile()
        epochRuns = self.experiment_file['/epoch_runs']
        newEpochRun = epochRuns.create_group(str(self.series_count))
        newEpochRun.attrs['run_start_time'] = run_start_time
        for key in protocol_object.run_parameters: #save out run parameters as an attribute of this epoch run
            newEpochRun.attrs[key] = protocol_object.run_parameters[key]

        for key in self.fly_metadata: #save out fly metadata as an attribute of this epoch run
            newEpochRun.attrs[key] = self.fly_metadata[key]
            
        self.experiment_file.close()
        
    def saveEpochMetaData(self,protocol_object):
        # update epoch metadata for this epoch
        self.reOpenExperimentFile()
        epoch_time = datetime.now().strftime('%H:%M:%S.%f')[:-4]
        newEpoch = self.experiment_file['/epoch_runs/' + str(self.series_count)].create_group('epoch_'+str(protocol_object.num_epochs_completed))
        newEpoch.attrs['epoch_time'] = epoch_time
        
        epochParametersGroup = newEpoch.create_group('epoch_parameters')
        for key in protocol_object.epoch_parameters: #save out epoch parameters
            newValue = protocol_object.epoch_parameters[key]
            if type(newValue) is dict: #TODO: Find a way to split this into subgroups. Hacky work around. 
                newValue = str(newValue)
            epochParametersGroup.attrs[key] = newValue
      
        convenienceParametersGroup = newEpoch.create_group('convenience_parameters')
        for key in protocol_object.convenience_parameters: #save out convenience parameters
            convenienceParametersGroup.attrs[key] = protocol_object.convenience_parameters[key]
        self.experiment_file.close()

    def addNoteToExperimentFile(self, noteText):
        noteTime = datetime.now().strftime('%H:%M:%S.%f')[:-4]
        self.reOpenExperimentFile()
        notes = self.experiment_file['/notes']
        notes.attrs[noteTime] = noteText
        self.experiment_file.close()
        
    def reOpenExperimentFile(self):
        self.experiment_file = h5py.File(os.path.join(self.data_directory, self.experiment_file_name + '.hdf5'), 'r+')
        
    def advanceSeriesCount(self):
        self.series_count += 1
        
