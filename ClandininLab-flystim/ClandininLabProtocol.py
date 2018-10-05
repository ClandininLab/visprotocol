#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 11:05:55 2018

This is an abstract parent class that handles epoch runs, experiment notes,
run parameters, and anything else that is constant across protocols and users

This cannot be used by itself to play stimuli. It requires a sub-class to
handle things like initializing the screen, and passing parameters to flystim

@author: mhturner
"""

from time import sleep
from flystim.launch import MultiCall
from datetime import datetime
from PyQt5.QtWidgets import QApplication
import h5py
import os
import nidaqmx
from sys import platform

#TODO: clean up var names etc
class ClandininLabProtocol():
    def __init__(self):
        super().__init__()
        
        self.getDefaultRunParameters() # Run parameters that are constant across all protocols
        self.protocol_parameters = {} # populated in GUI or user protocol
        self.fly_metadata = {}  # populated in GUI or user protocol
        self.stop = False
        self.num_epochs_completed = 0
        
        self.series_count = 1

        # Experiment file should be initialized by the user
        self.experiment_file = None
        self.experiment_file_name = None
        
    def start(self, run_parameters, protocol_parameters, fly_metadata, save_metadata_flag):
        self.stop = False
        self.manager.set_idle_background(run_parameters['idle_color'])
        run_start_time = datetime.now().strftime('%H:%M:%S.%f')[:-4]
        
        if save_metadata_flag:
            # create a new epoch run group
            self.reOpenExperimentFile()
            epochRuns = self.experiment_file['/epoch_runs']
            newEpochRun = epochRuns.create_group(str(self.series_count))
            newEpochRun.attrs['run_start_time'] = run_start_time
            for key in run_parameters: #save out run parameters as an attribute of this epoch run
                newEpochRun.attrs[key] = run_parameters[key]

            for key in fly_metadata: #save out fly metadata as an attribute of this epoch run
                newEpochRun.attrs[key] = fly_metadata[key]
                
            self.experiment_file.close()

        else:
            print('Warning - you are not saving your metadata!')
    
        self.num_epochs_completed = 0
        for epoch in range(int(run_parameters['num_epochs'])):
            QApplication.processEvents()
            if self.stop is True:
                self.stop = False
                break
            #  get stimulus parameters for this epoch
            epoch_parameters, convenience_parameters = self.protocol_ID_object.getEpochParameters(self)
 
            if save_metadata_flag:
                # update epoch metadata
                self.reOpenExperimentFile()
                epoch_time = datetime.now().strftime('%H:%M:%S.%f')[:-4]
                newEpoch = self.experiment_file['/epoch_runs/' + str(self.series_count)].create_group('epoch_'+str(self.num_epochs_completed))
                newEpoch.attrs['epoch_time'] = epoch_time
                
                epochParametersGroup = newEpoch.create_group('epoch_parameters')
                for key in epoch_parameters: #save out epoch parameters
                    newValue = epoch_parameters[key]
                    if type(newValue) is dict: #TODO: Find a way to split this into subgroups. Hacky work around. 
                        newValue = str(newValue)
                    epochParametersGroup.attrs[key] = newValue
              
                convenienceParametersGroup = newEpoch.create_group('convenience_parameters')
                for key in convenience_parameters: #save out convenience parameters
                    convenienceParametersGroup.attrs[key] = convenience_parameters[key]
                self.experiment_file.close()

            if platform == "win32":
                # Send a TTL pulse through the NI-USB to trigger acquisition
                with nidaqmx.Task() as task:
                    task.co_channels.add_co_pulse_chan_time("Dev5/ctr0",
                                                            low_time=0.002,
                                                            high_time=0.001)
                    task.start()

            # send the stimulus to flystim
            passedParameters = epoch_parameters.copy()
            multicall = MultiCall(self.manager)
            multicall.load_stim(**passedParameters)
            
            # play the presentation
            #Pre time
            sleep(run_parameters['pre_time'])
            
            #stim time
            multicall.start_stim()
            multicall.start_corner_square()
            multicall()
            sleep(run_parameters['stim_time'])
            
            #tail time
            multicall = MultiCall(self.manager)
            multicall.stop_stim()
            multicall.black_corner_square()
            multicall()
            sleep(run_parameters['tail_time'])
            
            self.num_epochs_completed += 1
            
            
    def getDefaultRunParameters(self):
        self.run_parameters = {'protocol_ID':'',
              'num_epochs':5,
              'pre_time':0.5,
              'stim_time':5.0,
              'tail_time':0.5,
              'idle_color':0.5}

    def addNoteToExperimentFile(self, noteText):
        noteTime = datetime.now().strftime('%H:%M:%S.%f')[:-4]
        self.reOpenExperimentFile()
        notes = self.experiment_file['/notes']
        notes.attrs[noteTime] = noteText
        self.experiment_file.close()

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
        
    def reOpenExperimentFile(self):
        self.experiment_file = h5py.File(os.path.join(self.data_directory, self.experiment_file_name + '.hdf5'), 'r+')
