#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 10:20:02 2018

@author: mhturner
"""

#!/usr/bin/env python3


from xmlrpc.client import ServerProxy
from time import sleep
from datetime import datetime
import numpy.random as random
import squirrel
from sys import platform

class MhtProtocol():
    def __init__(self):
        super().__init__()
        # Load initialized metadata file
        # TODO: hdf5 experiment file. GUI for expt file initialization?
        # TODO: split off a parent class for lab-wide protocol. Then sub-class individual protocols
        
        if platform == "darwin":
            self.data_directory = '/Users/mhturner/documents/stashedObjects/'
        elif platform == "win32":
            self.data_directory = '/Users/Main/Documents/Data/'
        self.date = datetime.now().isoformat()[:-16]
        try:
            self.experiment_file = squirrel.get(self.date, self.data_directory)
        except FileNotFoundError as e:
            raise NameError('Initialize experiment file first using initialize_experiment_file')


    def start(self, run_parameters, protocol_parameters, port=62632):
        client = ServerProxy('http://127.0.0.1:{}'.format(port))
        run_parameters['run_start_time'] = datetime.now().strftime('%H:%M:%S.%f')[:-4]
        new_run = {'run_parameters':run_parameters,
                   'epoch': []} # list epoch will grow with each iteration
        self.experiment_file['epoch_run'].append(new_run)
    
        for epoch in range(int(run_parameters['num_epochs'])):
            #  get stimulus parameters for this epoch
            stimulus_ID, epoch_parameters = self.getEpochParameters(run_parameters['protocol_ID'], protocol_parameters, epoch)
    
            # send the stimulus to flystim
            client.load_stim(stimulus_ID, epoch_parameters)
            
            # update epoch metadata
            epoch_time = datetime.now().strftime('%H:%M:%S.%f')[:-4]
            new_run['epoch'].append({'epoch_time':epoch_time, 'epoch_parameters':epoch_parameters.copy()})
            
            # play the presentation
            sleep(run_parameters['pre_time'])
            client.start_stim()
            sleep(run_parameters['stim_time'])
            client.stop_stim()
            sleep(run_parameters['tail_time'])
            
            # update experiment_file now, in case of interrupt in mid-run
            squirrel.stash(self.experiment_file, self.date , self.data_directory)
    
    # Function that selects the stimulus parameters sent to FlyStim for an epoch
    # E.g. reset a random seed each epoch, or select a parameter value from among a list of possible values
    def getEpochParameters(self, protocol_ID, protocol_parameters, epoch):
        epoch_parameters = protocol_parameters
        if protocol_ID == 'CheckerboardWhiteNoise':
            stimulus_ID = 'RandomGrid'
            epoch_parameters['start_seed'] = int(random.choice(range(int(1e6))))
            epoch_parameters['theta_period'] = int(epoch_parameters['theta_period'])
            epoch_parameters['phi_period'] = int(epoch_parameters['phi_period'])
            
        elif protocol_ID == 'RotatingSquareGrating':
            stimulus_ID = 'RotatingBars'
            
            
            
        else:
            raise NameError('Unrecognized stimulus ID')
            
        return stimulus_ID, epoch_parameters
    
    
    # For each protocol, default stimulus parameters are stored here:
    def getParameterDefaults(self, protocol_ID):
        if protocol_ID == 'CheckerboardWhiteNoise':
            params = {'theta_period':15,
                       'phi_period':15,
                       'rand_min':0,
                       'rand_max':1.0,
                       'start_seed':0,
                       'update_rate':60.0}
            
        elif protocol_ID == 'RotatingSquareGrating':
            params = {'period':20,
                       'duty_cycle':0.5,
                       'rate':10,
                       'color':1.0,
                       'background':0.5}
        
        else:
            raise NameError('Unrecognized stimulus ID')         
            
        return params
    
    def addNoteToExperimentFile(self, noteText):
        noteTime = datetime.now().strftime('%H:%M:%S.%f')[:-4]
        newNoteEntry = dict({'noteTime':noteTime, 'noteText':noteText})
        self.experiment_file['notes'].append(newNoteEntry)
        # update experiment_file
        squirrel.stash(self.experiment_file, self.date , self.data_directory)
        
