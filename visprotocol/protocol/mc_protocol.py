#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import inspect
import numpy as np

import visprotocol
from visprotocol.protocol import clandinin_protocol
from flystim.trajectory import RectangleTrajectory


class BaseProtocol(clandinin_protocol.BaseProtocol):
    def __init__(self):
        super().__init__() #call the parent class init method first
        user_name = 'mc'
        self.parameter_preset_directory = os.path.join(inspect.getfile(visprotocol).split('visprotocol')[0], 'visprotocol', 'resources', user_name, 'parameter_presets')


# %%
class UniformSquareFlash(BaseProtocol):
    def __init__(self):
        super().__init__()

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        stimulus_ID = 'MovingPatch'
        current_width, current_angle, current_intensity = self.selectParametersFromLists(
                (self.protocol_parameters['width'],
                    self.protocol_parameters['angle'],
                    self.protocol_parameters['intensity']),
                all_combinations = True,
                randomize_order = self.protocol_parameters['randomize_order'])

        #adjust center to screen center
        adj_center = self.adjustCenter(self.protocol_parameters['center'])

        trajectory = RectangleTrajectory(x = adj_center[0],
                                          y = adj_center[1],
                                          angle = current_angle,
                                          h = current_width,
                                          w = current_width,
                                          color = current_intensity).to_dict()

        self.epoch_parameters = {'name':stimulus_ID,
                            'background':self.run_parameters['idle_color'],
                            'trajectory':trajectory}
        self.convenience_parameters = {}
        self.convenience_parameters['current_width'] = current_width
        self.convenience_parameters['current_angle'] = current_angle
        self.convenience_parameters['current_intensity'] = current_intensity


    def getParameterDefaults(self):
        self.protocol_parameters = {'center': [0, 0],
                       'width':[20.0, 120.0],
                       'angle': [0],
                       'intensity': [0, 1.0],
                       'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'UniformSquareFlash',
              'num_epochs':160,
              'pre_time':0.5,
              'stim_time':0.02,
              'tail_time':1.0,
              'idle_color':0.5}

# %%
class UniformFlashOld(BaseProtocol):
    def __init__(self):
        super().__init__()

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        stimulus_ID = 'MovingPatch'

        #adjust center to screen center
        adj_center = self.adjustCenter(self.protocol_parameters['center'])

        trajectory = RectangleTrajectory(x = adj_center[0],
                              y = adj_center[1],
                              angle = 0,
                              h = self.protocol_parameters['height'],
                              w = self.protocol_parameters['width'],
                              color = self.protocol_parameters['intensity']).to_dict()

        self.epoch_parameters = {'name':stimulus_ID,
                            'background':self.run_parameters['idle_color'],
                            'trajectory':trajectory}

    def getParameterDefaults(self):
        self.protocol_parameters = {'height':120.0,
                       'width':120.0,
                       'center': [0, 0],
                       'intensity': 1.0}


    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'UniformFlash',
              'num_epochs':10,
              'pre_time':1.0,
              'stim_time':0.5,
              'tail_time':1.0,
              'idle_color':0.5}
# %%
class SpotSizes(BaseProtocol):
    def __init__(self):
        super().__init__()

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        stimulus_ID = 'MovingPatch'

        #adjust center to screen center
        adj_center = self.adjustCenter(self.protocol_parameters['center'])

        current_size = self.selectParametersFromLists(self.protocol_parameters['size'],
                randomize_order = self.protocol_parameters['randomize_order'])

        trajectory = RectangleTrajectory(x = adj_center[0],
                              y = adj_center[1],
                              angle = 0,
                              h = current_size,
                              w = current_size,
                              color = self.protocol_parameters['intensity']).to_dict()

        self.epoch_parameters = {'name':stimulus_ID,
                            'background':self.run_parameters['idle_color'],
                            'trajectory':trajectory}
        self.convenience_parameters = {}
        self.convenience_parameters['current_size'] = current_size

    def getParameterDefaults(self):
        self.protocol_parameters = {'size':[5, 10, 20, 30, 40, 50],
                       'center': [0, 0],
                       'intensity': 1.0,
                       'randomize_order':True}


    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'SpotSizes',
              'num_epochs':10,
              'pre_time':1.0,
              'stim_time':1.0,
              'tail_time':1.0,
              'idle_color':0.5}


# %%
class MovingRectangle(BaseProtocol):
    def __init__(self):
        super().__init__()

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        current_angle = self.selectParametersFromLists(self.protocol_parameters['angle'],
               randomize_order = self.protocol_parameters['randomize_order'])

        self.epoch_parameters = self.getMovingPatchParameters(angle = current_angle)

        self.convenience_parameters = {}
        self.convenience_parameters['current_angle'] = current_angle

    def getParameterDefaults(self):
        self.protocol_parameters = {'width':20.0,
                       'height':120.0,
                       'color':1.0,
                       'center': [0, 0],
                       'speed':20.0,
                       'angle': [0.0, 90.0, 180.0, 270.0],
                       'randomize_order':True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'MovingRectangle',
              'num_epochs':40,
              'pre_time':1.0,
              'stim_time':5.0,
              'tail_time':1.0,
              'idle_color':0.5}

# %%
class SpatialTernaryNoise(BaseProtocol):
    def __init__(self):
        super().__init__()

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        stimulus_ID  = 'RandomGrid'

        start_seed = int(np.random.choice(range(int(1e6))))


        distribution_data = {'name':'Ternary',
                     'args':[],
                     'kwargs':{'rand_min':self.protocol_parameters['rand_min'],
                               'rand_max':self.protocol_parameters['rand_max']}}

        self.epoch_parameters = {'name':stimulus_ID,
                    'theta_period':self.protocol_parameters['checker_width'],
                    'phi_period':self.protocol_parameters['checker_width'],
                    'start_seed':start_seed,
                    'update_rate':self.protocol_parameters['update_rate'],
                    'distribution_data':distribution_data}
        self.convenience_parameters = {}
        self.convenience_parameters['start_seed'] = start_seed

    def getParameterDefaults(self):
        self.protocol_parameters = {'checker_width':2.5,
                       'update_rate':50.0,
                       'rand_min': 0.0,
                       'rand_max':1.0}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'SpatialTernaryNoise',
              'num_epochs':10,
              'pre_time':1.0,
              'stim_time':30.0,
              'tail_time':1.0,
              'idle_color':0.5}
