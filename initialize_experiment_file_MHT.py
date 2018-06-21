#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 09:03:14 2018

e.g.: in python
import initialize_experiment_file_MHT
initialize_experiment_file_MHT.main(age= 3, prep = 'Optic lobe - left', indicator1 = 'GCaMP6f', driver1 = '21Dhh')

@author: mhturner
"""

import squirrel
from datetime import datetime
import os

def main(age = 0, prep = '',indicator1 = '', driver1 = '', indicator2 = '', driver2 = '',  
         data_directory = '/Users/mhturner/documents/stashedObjects/', experimenter = 'MHT'):
    
    
    init_now = datetime.now()
    date = init_now.isoformat()[:-16]
    init_time = init_now.strftime("%H:%M:%S")
    
    experiment_metadata = {'date':date, 
                           'init_time':init_time,
                           'data_directory':data_directory,
                           'experimenter':experimenter,
                           'age':age,
                           'prep':prep,
                           'indicator1':indicator1,
                           'driver1':driver1,
                           'indicator2':indicator2,
                           'driver2':driver2}


    experiment_file = {'experiment_metadata':experiment_metadata,
                       'epoch_run':[]}
    if os.path.isfile(data_directory + date + '.pkl'):
        raise NameError('Experiment file already exists! Please move or re-name existing file if you would like to start a new one')
        
    squirrel.stash(experiment_file, date ,data_directory)
    
if __name__ == '__main__':
    main()