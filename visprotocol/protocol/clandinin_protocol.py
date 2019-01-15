#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Protocol parent class. Override any methods in here in the user protocol subclass
"""
import numpy as np
from time import sleep
from datetime import datetime

import os.path
from fiver.utilities import squirrel

class BaseProtocol():
    def __init__(self):
        self.num_epochs_completed = 0
        self.parameter_preset_directory = os.path.curdir
        self.send_ttl = False
        self.getRunParameterDefaults()
        self.getParameterDefaults()
        self.loadParameterPresets()
   
    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'',
              'num_epochs':5,
              'pre_time':1.0,
              'stim_time':4.0,
              'tail_time':1.0,
              'idle_color':0.5}
        
    def getParameterDefaults(self):
        self.protocol_parameters = {}
        
    def loadParameterPresets(self):
        fname = os.path.join(self.parameter_preset_directory, self.run_parameters['protocol_ID']) + '.pkl'
        if os.path.isfile(fname):
            self.parameter_presets = squirrel.get(self.run_parameters['protocol_ID'], data_directory = self.parameter_preset_directory)
        else:
            self.parameter_presets = {}
        
    def updateParameterPresets(self, name):
        self.loadParameterPresets()
        new_preset = {'run_parameters': self.run_parameters,
                      'protocol_parameters': self.protocol_parameters}
        self.parameter_presets[name] = new_preset
        squirrel.stash(self.parameter_presets, self.run_parameters['protocol_ID'], data_directory = self.parameter_preset_directory)
        
    def selectProtocolPreset(self, name):
        if name in self.parameter_presets:
            self.run_parameters = self.parameter_presets[name]['run_parameters']
            self.protocol_parameters = self.parameter_presets[name]['protocol_parameters']
        else:
            self.getRunParameterDefaults()
            self.getParameterDefaults()
            
        
    def advanceEpochCounter(self):
        self.num_epochs_completed += 1
        
        
    def loadStimuli(self, multicall):
        passedParameters = self.epoch_parameters.copy()
        multicall.load_stim(**passedParameters)
        
    def startStimuli(self, multicall):
        sleep(self.run_parameters['pre_time'])
        #stim time
        multicall.start_stim()
        multicall.start_corner_square()
        multicall()
        sleep(self.run_parameters['stim_time'])
        
        #tail time
        multicall.stop_stim()
        multicall.black_corner_square()
        multicall()
        sleep(self.run_parameters['tail_time'])     
        
        
    def saveEpochRunMetaData(self, data):
        # create a new epoch run group in the data file
        run_start_time = datetime.now().strftime('%H:%M:%S.%f')[:-4]
        data.reOpenExperimentFile()
        epochRuns = data.experiment_file['/epoch_runs']
        newEpochRun = epochRuns.create_group(str(data.series_count))
        newEpochRun.attrs['run_start_time'] = run_start_time
        for key in self.run_parameters: #save out run parameters as an attribute of this epoch run
            newEpochRun.attrs[key] = self.run_parameters[key]

        for key in data.fly_metadata: #save out fly metadata as an attribute of this epoch run
            newEpochRun.attrs[key] = data.fly_metadata[key]
            
        data.experiment_file.close()
        
    def saveEpochMetaData(self,data):
        # update epoch metadata for this epoch
        data.reOpenExperimentFile()
        epoch_time = datetime.now().strftime('%H:%M:%S.%f')[:-4]
        newEpoch = data.experiment_file['/epoch_runs/' + str(data.series_count)].create_group('epoch_'+str(self.num_epochs_completed))
        newEpoch.attrs['epoch_time'] = epoch_time
        
        epochParametersGroup = newEpoch.create_group('epoch_parameters')
        for key in self.epoch_parameters: #save out epoch parameters
            newValue = self.epoch_parameters[key]
            if type(newValue) is dict: #TODO: Find a way to split this into subgroups. Hacky work around. 
                newValue = str(newValue)
            epochParametersGroup.attrs[key] = newValue
      
        convenienceParametersGroup = newEpoch.create_group('convenience_parameters')
        for key in self.convenience_parameters: #save out convenience parameters
            convenienceParametersGroup.attrs[key] = self.convenience_parameters[key]
        data.experiment_file.close()
        
        
    # Convenience functions shared across protocols...
    def selectParametersFromLists(self, parameter_list, all_combinations = True, randomize_order = False):
        """
        inputs
        parameter_list can be:
            -list/array of parameters
            -single value (int, float etc)
            -tuple of lists, where each list contains values for a single parameter
                    in this case, all_combinations = True will return all possible combinations of parameters, taking 
                    one from each parameter list. If all_combinations = False, keeps params associated across lists
        randomize_order will randomize sequence or sequences at the beginning of each new sequence
        """
        
        # parameter_list is a tuple of lists or a single list
        if type(parameter_list) is list: #single protocol parameter list, choose one from this list
            parameter_sequence = parameter_list
            
        elif type(parameter_list) is tuple: #multiple lists of protocol parameters
            if all_combinations:
                parameter_list_new = []
                
                # check for non-list elements of the tuple (int or float user entry)
                for param in list(parameter_list):
                    if type(param) is not list:
                        parameter_list_new.append([param])
                    else:
                        parameter_list_new.append(param)
                parameter_list = tuple(parameter_list_new)
                
                # parameter_sequence is num_combinations by num params
                parameter_sequence = np.array(np.meshgrid(*parameter_list)).T.reshape(np.prod(list(len(x) for x in parameter_list)),len(parameter_list))
            else:
                #keep params in lists associated with one another
                #requires param lists of equal length
                parameter_sequence = np.vstack(parameter_list).T 
    
        else: #user probably entered a single value (int or float), convert to list
            parameter_sequence = [parameter_list] 
    
    
        if self.num_epochs_completed == 0: #new run: initialize persistent sequences
                self.persistent_parameters = {'parameter_sequence':parameter_sequence}
                
        draw_ind = np.mod(self.num_epochs_completed,len(self.persistent_parameters['parameter_sequence']))
        if draw_ind == 0 and randomize_order: #randomize sequence
            rand_inds = np.random.permutation(len(self.persistent_parameters['parameter_sequence']))
            if len(np.shape(self.persistent_parameters['parameter_sequence'])) == 1:
                self.persistent_parameters['parameter_sequence'] = list(np.array(self.persistent_parameters['parameter_sequence'])[rand_inds])
            else:
                self.persistent_parameters['parameter_sequence'] = list(np.array(self.persistent_parameters['parameter_sequence'])[rand_inds,:])
        
        current_parameters = self.persistent_parameters['parameter_sequence'][draw_ind]
    
        return current_parameters