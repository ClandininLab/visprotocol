#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import inspect

import visprotocol
from visprotocol.protocol import clandinin_protocol
from flystim.trajectory import RectangleTrajectory


class BaseProtocol(clandinin_protocol.BaseProtocol):
    def __init__(self):
        super().__init__() #call the parent class init method first
        user_name = 'mmp'
        self.parameter_preset_directory = os.path.join(inspect.getfile(visprotocol).split('visprotocol')[0], 'visprotocol', 'resources', user_name, 'parameter_presets')
        
# %%
class BinaryFlash(BaseProtocol):
    def __init__(self):
        super().__init__()
        
        self.getRunParameterDefaults()
        self.getParameterDefaults()
    
    def getEpochParameters(self):
        stimulus_ID = 'MovingPatch'

        trajectory = RectangleTrajectory(x = self.protocol_parameters['center'][0],
                                              y = self.protocol_parameters['center'][1],
                                              angle = 0,
                                              h = self.protocol_parameters['height'],
                                              w = self.protocol_parameters['width'],
                                              color = self.protocol_parameters['intensity']).to_dict()  

        self.epoch_parameters = {'name':stimulus_ID,
                            'background':self.run_parameters['idle_color'],
                            'trajectory':trajectory}
        self.convenience_parameters = self.protocol_parameters.copy()

    def getParameterDefaults(self):
        self.protocol_parameters = {'height':180.0,
                       'width':180.0,
                       'center': [90.0, 120.0],
                       'intensity': 1.0}


    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'BinaryFlash',
              'num_epochs':100,
              'pre_time':0.25,
              'stim_time':0.5,
              'tail_time':0.25,
              'idle_color':0}

#%%
class MultipleContrastFlash(BaseProtocol):
    def __init__(self):
        super().__init__()
        
        self.getRunParameterDefaults()
        self.getParameterDefaults()
    
    def getEpochParameters(self):
        stimulus_ID = 'MovingPatch'
        current_intensity = self.selectParametersFromLists(self.protocol_parameters['intensity'],
                                                                randomize_order = self.protocol_parameters['randomize_order'])
        
        trajectory = RectangleTrajectory(x = self.protocol_parameters['center'][0],
                                              y = self.protocol_parameters['center'][1],
                                              angle = 0,
                                              h = self.protocol_parameters['height'],
                                              w = self.protocol_parameters['width'],
                                              color = current_intensity).to_dict()   

        self.epoch_parameters = {'name':stimulus_ID,
                            'background':self.run_parameters['idle_color'],
                            'trajectory':trajectory}
        self.convenience_parameters = self.protocol_parameters.copy()
        self.convenience_parameters['current_intensity'] = current_intensity

    def getParameterDefaults(self):
        self.protocol_parameters = {'height':180.0,
                       'width':180.0,
                       'center': [90.0, 120.0],
                       'intensity': [0, 0.25, 0.375, 0.625, 0.75, 1.0],
                       'randomize_order': True}


    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'MultipleContrastFlash',
              'num_epochs':100,
              'pre_time':0.5,
              'stim_time':0.02,
              'tail_time':0.5,
              'idle_color':0.5}