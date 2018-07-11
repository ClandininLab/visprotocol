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

#!/usr/bin/env python3

from time import sleep
from flystim.launch import MultiCall

from datetime import datetime
import squirrel

# TODO: repeated use of the same screen, e.g. re-initialize or replace screen maybe? Button in GUI?
# TODO: interrupt mid-run. Threading?

class ClandininLabProtocol():
    def __init__(self):
        super().__init__()
        # TODO: background color and clear color == and run param
        # Run parameters that are constant across all protocols
        self.run_parameters = {'protocol_ID':'',
              'num_epochs':5,
              'pre_time':0.5,
              'stim_time':5,
              'tail_time':0.5}
        self.protocol_parameters = {}

    def start(self, run_parameters, protocol_parameters, port=62632):
        run_parameters['run_start_time'] = datetime.now().strftime('%H:%M:%S.%f')[:-4]
        new_run = {'run_parameters':run_parameters,
                   'epoch': []} # list epoch will grow with each iteration
        self.experiment_file['epoch_run'].append(new_run)
    
        for epoch in range(int(run_parameters['num_epochs'])):
            #  get stimulus parameters for this epoch
            stimulus_ID, epoch_parameters = self.getEpochParameters(run_parameters['protocol_ID'], protocol_parameters, epoch)
 
            # update epoch metadata
            epoch_time = datetime.now().strftime('%H:%M:%S.%f')[:-4]
            new_run['epoch'].append({'epoch_time':epoch_time, 'epoch_parameters':epoch_parameters.copy()})
            
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
            
            # update experiment_file now, in case of interrupt in mid-run
            squirrel.stash(self.experiment_file, self.date , self.data_directory)

    def addNoteToExperimentFile(self, noteText):
        noteTime = datetime.now().strftime('%H:%M:%S.%f')[:-4]
        newNoteEntry = dict({'noteTime':noteTime, 'noteText':noteText})
        self.experiment_file['notes'].append(newNoteEntry)
        # update experiment_file
        squirrel.stash(self.experiment_file, self.date , self.data_directory)
        
