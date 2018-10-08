#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 15:14:14 2018

@author: mhturner
"""
import numpy as np

class SparseNoise():
    def getEpochParameters(protocolObject):
        stimulus_ID = 'RandomGrid'
        
        start_seed = int(np.random.choice(range(int(1e6))))
        
        distribution_data = {'name':'SparseBinary',
                                 'args':[],
                                 'kwargs':{'rand_min':protocolObject.protocol_parameters['rand_min'],
                                           'rand_max':protocolObject.protocol_parameters['rand_max'],
                                           'sparseness':protocolObject.protocol_parameters['sparseness']}}
        
        
        
        epoch_parameters = {'name': stimulus_ID,
                            'theta_period': protocolObject.protocol_parameters['checker_width'],
                            'phi_period': protocolObject.protocol_parameters['checker_width'],
                            'start_seed': start_seed, 
                            'update_rate': protocolObject.protocol_parameters['update_rate'],
                            'distribution_data': distribution_data}
        
        convenience_parameters = {}

        return epoch_parameters, convenience_parameters
        
        
    def getParameterDefaults():
        protocol_parameters = {'checker_width':5.0,
                               'update_rate':8.0,
                               'rand_min': 0.0,
                               'rand_max':1.0,
                               'sparseness':0.95}
        
        return protocol_parameters


    def getRunParameterDefaults():
        run_parameters = {'protocol_ID':'SparseNoise',
              'num_epochs':10,
              'pre_time':1.0,
              'stim_time':30.0,
              'tail_time':1.0,
              'idle_color':0.5}
        return run_parameters