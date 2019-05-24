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
class UniformFlash(BaseProtocol):
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
        self.protocol_parameters = {'height':270.0,
                       'width':270.0,
                       'center': [90.0, 120.0],
                       'intensity': [0, 0.25, 0.375, 0.625, 0.75, 1.0],
                       'randomize_order': True}


    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'UniformFlash',
              'num_epochs':10,
              'pre_time':1.0,
              'stim_time':0.5,
              'tail_time':1.0,
              'idle_color':0.5}
