#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import os
import inspect
from datetime import datetime
from time import sleep


import visprotocol
from visprotocol.protocol import clandinin_protocol
from flystim.trajectory import RectangleTrajectory, Trajectory


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
              'num_epochs':30,
              'pre_time':0.25,
              'stim_time':0.5,
              'tail_time':0.25,
              'idle_color':0.5}

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
              'pre_time':0.08,
              'stim_time':0.02,
              'tail_time':0.5,
              'idle_color':0.5}
        
# %%
class LoomingPatch(BaseProtocol):
    def __init__(self):
        super().__init__()
        
        self.getRunParameterDefaults()
        self.getParameterDefaults()
        
    def getEpochParameters(self):
        stimulus_ID = 'MovingPatch'

        stim_time = self.run_parameters['stim_time']
        start_size = self.protocol_parameters['start_size']
        end_size = self.protocol_parameters['end_size']
        
        rv_ratio = self.protocol_parameters['rv_ratio'] #msec
        trajectory_code = [0, 1, 2] #0 = expanding, 1 = reversed (shrinking), 2 = randomized

        current_rv_ratio, current_trajectory_code = self.selectParametersFromLists((rv_ratio, trajectory_code),
                                                                                             all_combinations = True, 
                                                                                             randomize_order = self.protocol_parameters['randomize_order'])
        
        current_rv_ratio = current_rv_ratio / 1e3 #msec -> sec
    
        time_steps = np.arange(0,stim_time-0.001,0.001) #time steps of trajectory
        # calculate angular size at each time step for this rv ratio
        angular_size = 2 * np.rad2deg(np.arctan(current_rv_ratio * (1 /(stim_time - time_steps))))
        
        # shift curve vertically so it starts at start_size
        min_size = angular_size[0]
        size_adjust = min_size - start_size
        angular_size = angular_size - size_adjust
        # Cap the curve at end_size and have it just hang there
        max_size_ind = np.where(angular_size > end_size)[0][0]
        angular_size[max_size_ind:] = end_size

        # Get the correct trajectory type
        if current_trajectory_code == 0:
            current_trajectory_type = 'expanding'
            angular_size = angular_size # initial trajectory
            
        elif current_trajectory_code == 1:
            current_trajectory_type = 'contracting'
            angular_size = np.flip(angular_size, axis = 0) # reverse in time
            
        elif current_trajectory_code == 2:
            current_trajectory_type = 'randomized'
            angular_size = np.random.permutation(angular_size) #randomize in time

        # time-modulated trajectories
        h = Trajectory(list(zip(time_steps,angular_size)), kind = 'previous')
        w = Trajectory(list(zip(time_steps,angular_size)), kind = 'previous')
        
        #adjust center to screen center
        adj_center = self.adjustCenter(self.protocol_parameters['center'])

        # constant trajectories:
        centerX = Trajectory(adj_center[0])
        centerY = Trajectory(adj_center[1])
        color = Trajectory(self.protocol_parameters['color'])
        angle = Trajectory(0)
        trajectory = {'x': centerX.to_dict(), 'y': centerY.to_dict(), 'w': w.to_dict(), 'h': h.to_dict(),
            'angle': angle.to_dict(), 'color': color.to_dict()}
        

        self.epoch_parameters = {'name':stimulus_ID,
                            'background':self.run_parameters['idle_color'],
                            'trajectory':trajectory}

        self.convenience_parameters = self.protocol_parameters.copy()
        self.convenience_parameters['current_rv_ratio'] = current_rv_ratio
        self.convenience_parameters['time_steps'] = time_steps
        self.convenience_parameters['angular_size'] = angular_size
        self.convenience_parameters['current_trajectory_type'] = current_trajectory_type


    def getParameterDefaults(self):
        self.protocol_parameters = {'color':0.0,
                       'center': [0, 0],
                       'start_size': 2.5,
                       'end_size': 120.0,
                       'rv_ratio':[5.0, 10.0, 20.0, 40.0, 80.0],
                       'randomize_order': True}
    
    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'LoomingPatch',
              'num_epochs':75,
              'pre_time':0.5,
              'stim_time':1.0,
              'tail_time':1.0,
              'idle_color':0.5}