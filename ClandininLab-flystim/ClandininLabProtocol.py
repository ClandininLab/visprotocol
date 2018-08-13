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
# TODO: hdf5 experiment file instead of pickle file?
# TODO: port for remote server playing?

from time import sleep
from flystim.launch import MultiCall
from datetime import datetime
import squirrel
from PyQt5.QtWidgets import QApplication

class ClandininLabProtocol():
    def __init__(self):
        super().__init__()
        # Run parameters that are constant across all protocols
        self.run_parameters = {'protocol_ID':'',
              'num_epochs':5,
              'pre_time':0.5,
              'stim_time':5,
              'tail_time':0.5,
              'idle_color':0.5}
        self.protocol_parameters = {}
        self.stop = False
        self.num_epochs_completed = 0

        # Fly should be initialized by the user
        self.currentFly = None
        
        # Experiment file should be initialized by the user
        self.experiment_file = None
        self.experiment_file_name = None
        
    def start(self, run_parameters, protocol_parameters, port=62632):
        self.stop = False
        self.manager.set_idle_background(run_parameters['idle_color'])
        run_parameters['run_start_time'] = datetime.now().strftime('%H:%M:%S.%f')[:-4]
        new_run = {'run_parameters':run_parameters,
                   'epoch': []} # list epoch will grow with each iteration
        if self.experiment_file is not None:
            self.experiment_file['epoch_run'].append(new_run)
        else:
            print('Warning - you are not saving your metadata!')
    
        self.num_epochs_completed = 0
        for epoch in range(int(run_parameters['num_epochs'])):
            QApplication.processEvents()
            if self.stop is True:
                self.stop = False
                break
            #  get stimulus parameters for this epoch
            stimulus_ID, epoch_parameters, convenience_parameters = self.getEpochParameters(run_parameters['protocol_ID'], protocol_parameters, epoch)
 
            # update epoch metadata
            epoch_time = datetime.now().strftime('%H:%M:%S.%f')[:-4]
            new_run['epoch'].append({'epoch_time':epoch_time,
                   'epoch_parameters':epoch_parameters.copy(),
                   'convenience_parameters':convenience_parameters.copy()})
            
            # send the stimulus to flystim
            passedParameters = epoch_parameters.copy()
            passedParameters['name'] = stimulus_ID
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
            
            # update experiment_file now, in case of interrupt in mid-run
            if self.experiment_file is not None:
                squirrel.stash(self.experiment_file, self.experiment_file_name , self.data_directory)

    def addNoteToExperimentFile(self, noteText):
        noteTime = datetime.now().strftime('%H:%M:%S.%f')[:-4]
        newNoteEntry = dict({'noteTime':noteTime, 'noteText':noteText})
        self.experiment_file['notes'].append(newNoteEntry)
        # update experiment_file
        squirrel.stash(self.experiment_file, self.experiment_file_name , self.data_directory)
        
    def initializeExperimentFile(self):
        init_now = datetime.now()
        date = init_now.isoformat()[:-16]
        init_time = init_now.strftime("%H:%M:%S")
        
        experiment_metadata = {'date':date, 
                               'init_time':init_time,
                               'data_directory':self.data_directory,
                               'experimenter':self.experimenter,
                               'rig':self.rig}
    
        self.experiment_file = {'experiment_metadata':experiment_metadata,
                           'epoch_run':[],
                           'notes':[]}
        
        squirrel.stash(self.experiment_file, self.experiment_file_name , self.data_directory)
        
