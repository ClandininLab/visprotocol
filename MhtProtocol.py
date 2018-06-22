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

def start(run_parameters, protocol_parameters, port=62632):
    client = ServerProxy('http://127.0.0.1:{}'.format(port))
    # Load initialized metadata file
    data_directory = '/Users/mhturner/documents/stashedObjects/'
    date = datetime.now().isoformat()[:-16]
    try:
        experiment_file = squirrel.get(date, data_directory)
    except FileNotFoundError as e:
        raise NameError('Initialize experiment file first using initialize_experiment_file')
            

    run_parameters['run_start_time'] = datetime.now().strftime('%H:%M:%S.%f')[:-4]
    new_run = {'run_parameters':run_parameters,
               'epoch': []} # list epoch will grow with each iteration
    experiment_file['epoch_run'].append(new_run)

    for epoch in range(int(run_parameters['num_epochs'])):
        #  get stimulus parameters for this epoch
        stimulus_ID, epoch_parameters = getEpochParameters(run_parameters['protocol_ID'], protocol_parameters, epoch)

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
        squirrel.stash(experiment_file, date ,data_directory)

if __name__ == '__start__':
    start()
    
# Function that selects the stimulus parameters sent to FlyStim for an epoch
# E.g. reset a random seed each epoch, or select a parameter value from among a list of possible values
def getEpochParameters(protocol_ID, protocol_parameters, epoch):
    epoch_parameters = protocol_parameters
    background_color = epoch_parameters['background_color']
    if not isinstance(background_color,tuple):
        epoch_parameters['background_color'] = (background_color, background_color, background_color)
    
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
def getParameterDefaults(protocol_ID):
    if protocol_ID == 'CheckerboardWhiteNoise':
        params = {'theta_period':15,
                   'phi_period':15,
                   'rand_min':0,
                   'rand_max':1.0,
                   'start_seed':0,
                   'update_rate':60.0,
                   'background_color':0.5}
        
    elif protocol_ID == 'RotatingSquareGrating':
        params = {'period':20,
                   'duty_cycle':0.5,
                   'rate':10,
                   'color':1.0,
                   'background_color':0.5}
    
    else:
        raise NameError('Unrecognized stimulus ID')         
        
    return params
