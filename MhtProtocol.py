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

def start(protocol_ID, port=62632):
    client = ServerProxy('http://127.0.0.1:{}'.format(port))
    # Load initialized metadata file
    data_directory = '/Users/mhturner/documents/stashedObjects/'
    date = datetime.now().isoformat()[:-16]
    try:
        experiment_file = squirrel.get(date, data_directory)
    except FileNotFoundError as e:
        raise NameError('Initialize experiment file first using initialize_experiment_file')
            
    run_start_time = datetime.now().strftime('%H:%M:%S.%f')[:-4]
    run_parameters = {'protocol_ID':protocol_ID,
              'num_trials':5,
              'pre_time':0.5,
              'stim_time':5,
              'tail_time':0.5,
              'run_start_time':run_start_time}
    new_run = {'run_parameters':run_parameters,
               'epoch': []} # list epoch will grow with each iteration
    experiment_file['epoch_run'].append(new_run)

    for trial in range(run_parameters['num_trials']):
        #  get stimulus parameters for this trial
        stimulus_ID, stimulus_parameters = getStimulusParameters(protocol_ID,trial)

        # send the stimulus to flystim
        client.load_stim(stimulus_ID, stimulus_parameters)
        
        # update epoch metadata
        epoch_time = datetime.now().strftime('%H:%M:%S.%f')[:-4]
        new_run['epoch'].append({'epoch_time':epoch_time, 'stimulus_parameters':stimulus_parameters})
        
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
        
def getStimulusParameters(protocol_ID,trial):
    if protocol_ID == 'CheckerboardWhiteNoise':
        # params constant across trials:
        stimulus_ID = 'RandomGrid'
        stimulus_parameters = {'theta_period':15,
                           'phi_period':15,
                           'rand_min':0,
                           'rand_max':1.0,
                           'start_seed':0,
                           'update_rate':60.0,
                           'background_color':(0.5, 0.5, 0.5)}
        # params that change each trial:
        stimulus_parameters['start_seed'] = int(random.choice(range(int(1e6))))
        return stimulus_ID, stimulus_parameters
    
    else:
        raise NameError('Unrecognized stimulus ID')          
