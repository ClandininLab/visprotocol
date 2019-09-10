#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 10:20:02 2018

@author: mhturner
"""
import numpy as np
from time import sleep

from visprotocol.protocol import clandinin_protocol
from flystim.trajectory import RectangleTrajectory, Trajectory


class BaseProtocol(clandinin_protocol.BaseProtocol):
    def __init__(self, user_name, rig_config):
        super().__init__(user_name, rig_config)  # call the parent class init method

    def getMovingPatchParameters(self, center = None, angle = None, speed = None, width = None, height = None, color = None, background = None, distance_to_travel = None):
        if center is None: center = self.adjustCenter(self.protocol_parameters['center'])
        if angle is None: angle = self.protocol_parameters['angle']
        if speed is None: speed = self.protocol_parameters['speed']
        if width is None: width = self.protocol_parameters['width']
        if height is None: height = self.protocol_parameters['height']
        if color is None: color = self.protocol_parameters['color']
        if background is None: background = self.run_parameters['idle_color']

        centerX = center[0]
        centerY = center[1]
        stim_time = self.run_parameters['stim_time']
        if distance_to_travel is None:  # distance_to_travel is set by speed and stim_time
            distance_to_travel = speed * stim_time
            # trajectory just has two points, at time=0 and time=stim_time
            startX = (0, centerX - np.cos(np.radians(angle)) * distance_to_travel/2)
            endX = (stim_time, centerX + np.cos(np.radians(angle)) * distance_to_travel/2)
            startY = (0, centerY - np.sin(np.radians(angle)) * distance_to_travel/2)
            endY = (stim_time, centerY + np.sin(np.radians(angle)) * distance_to_travel/2)
            x = [startX, endX]
            y = [startY, endY]

        else: #distance_to_travel is specified, so only go that distance at the defined speed. Hang pre- and post- for any extra stim time
            travel_time = distance_to_travel / speed
            if travel_time > stim_time:
                print('Warning: stim_time is too short to show whole trajectory at this speed!')
                hang_time = 0
            else:
                hang_time = (stim_time - travel_time)/2

            # split up hang time in pre and post such that trajectory always hits centerX,centerY at stim_time/2
            x_1 = (0,centerX - np.cos(np.radians(angle)) * distance_to_travel/2)
            x_2 = (hang_time,centerX - np.cos(np.radians(angle)) * distance_to_travel/2)
            x_3 = (hang_time+travel_time, centerX + np.cos(np.radians(angle)) * distance_to_travel/2)
            x_4 = (hang_time+travel_time+hang_time, centerX + np.cos(np.radians(angle)) * distance_to_travel/2)

            y_1 = (0,centerY - np.sin(np.radians(angle)) * distance_to_travel/2)
            y_2 = (hang_time,centerY - np.sin(np.radians(angle)) * distance_to_travel/2)
            y_3 = (hang_time+travel_time, centerY + np.sin(np.radians(angle)) * distance_to_travel/2)
            y_4 = (hang_time+travel_time+hang_time, centerY + np.sin(np.radians(angle)) * distance_to_travel/2)

            x = [x_1,x_2,x_3,x_4]
            y = [y_1, y_2, y_3, y_4]

        trajectory = RectangleTrajectory(x=x,
                                         y=y,
                                         angle=angle,
                                         h = height,
                                         w = width,
                                         color = color).to_dict()

        patch_parameters = {'name':'MovingPatch',
                                'background':background,
                                'trajectory':trajectory}
        return patch_parameters

    def getRotatingGratingParameters(self, angle = None, rate = None, period = None, color = None, background = None):
        if angle is None: angle = self.protocol_parameters['angle']
        if rate is None: rate = self.protocol_parameters['rate']
        if period is None: period = self.protocol_parameters['period']
        if color is None: color = self.protocol_parameters['color']
        if background is None: background = self.protocol_parameters['background']

        grate_parameters = {'name':'RotatingBars',
                            'period':period,
                            'duty_cycle':0.5,
                            'rate':rate,
                            'color':color,
                            'background':background,
                            'angle':angle}
        return grate_parameters


    def getColorAndBackgroundFromContrast(self, contrast): #for grating stims
        color = self.run_parameters['idle_color'] + contrast * self.run_parameters['idle_color']
        background = self.run_parameters['idle_color'] - contrast * self.run_parameters['idle_color']

        return color, background
# %%


class CheckerboardWhiteNoise(BaseProtocol):
    def __init__(self, user_name, rig_config):
        super().__init__(user_name, rig_config)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        stimulus_ID  = 'RandomGrid'

        start_seed = int(np.random.choice(range(int(1e6))))


        distribution_data = {'name':'Gaussian',
                                 'args':[],
                                 'kwargs':{'rand_mean':self.protocol_parameters['rand_mean'],
                                           'rand_stdev':self.protocol_parameters['rand_stdev']}}

        self.epoch_parameters = {'name':stimulus_ID,
                            'theta_period':self.protocol_parameters['checker_width'],
                            'phi_period':self.protocol_parameters['checker_width'],
                            'start_seed':start_seed,
                            'update_rate':self.protocol_parameters['update_rate'],
                            'distribution_data':distribution_data}
        self.convenience_parameters = {'start_seed': start_seed}

    def getParameterDefaults(self):
        self.protocol_parameters = {'checker_width':5.0,
                       'update_rate':0.5,
                       'rand_mean': 0.5,
                       'rand_stdev':0.15}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'CheckerboardWhiteNoise',
              'num_epochs':10,
              'pre_time':1.0,
              'stim_time':30.0,
              'tail_time':1.0,
              'idle_color':0.5}

# %%


class ContrastReversingGrating(BaseProtocol):
    def __init__(self, user_name, rig_config):
        super().__init__(user_name, rig_config)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        current_temporal_frequency = self.selectParametersFromLists(self.protocol_parameters['temporal_frequency'],
                                                                randomize_order = self.protocol_parameters['randomize_order'])

        self.epoch_parameters =  {'name':'ContrastReversingGrating',
                                  'spatial_period':self.protocol_parameters['spatial_period'],
                                  'temporal_frequency':current_temporal_frequency,
                                  'contrast_scale':self.protocol_parameters['contrast_scale'],
                                  'mean':self.protocol_parameters['mean'],
                                  'angle':self.protocol_parameters['angle']}

        self.convenience_parameters = {'current_temporal_frequency': current_temporal_frequency}

        self.meta_parameters = {'center_size':self.protocol_parameters['center_size'],
                                'center':self.adjustCenter(self.protocol_parameters['center'])}
    def loadStimuli(self, multicall):
        passed_parameters = self.epoch_parameters.copy()
        box_min_x = self.meta_parameters['center'][0] - self.meta_parameters['center_size']/2
        box_max_x = self.meta_parameters['center'][0] + self.meta_parameters['center_size']/2

        box_min_y = self.meta_parameters['center'][1] - self.meta_parameters['center_size']/2
        box_max_y = self.meta_parameters['center'][1] + self.meta_parameters['center_size']/2

        multicall.load_stim(name='MovingPatch', background = self.run_parameters['idle_color'], trajectory=RectangleTrajectory(w = 0, h = 0).to_dict())

        multicall.load_stim(**passed_parameters,
                            box_min_x=box_min_x, box_max_x=box_max_x, box_min_y=box_min_y, box_max_y=box_max_y,
                            hold=True)

    def getParameterDefaults(self):
        self.protocol_parameters = {'spatial_period':20.0,
                       'contrast_scale':1.0,
                       'mean':0.5,
                       'temporal_frequency':[0.5, 1.0, 2.0, 4.0, 8.0, 16.0],
                       'center':[0, 0],
                       'center_size':40.0,
                       'angle':0.0,
                       'randomize_order':True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'ContrastReversingGrating',
              'num_epochs':40,
              'pre_time':1.0,
              'stim_time':4.0,
              'tail_time':1.0,
              'idle_color':0.5}

# %%


class DriftingSquareGrating(BaseProtocol):
    def __init__(self, user_name, rig_config):
        super().__init__(user_name, rig_config)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        current_angle = self.selectParametersFromLists(self.protocol_parameters['angle'],
                                                                randomize_order = self.protocol_parameters['randomize_order'])

        self.epoch_parameters = self.getRotatingGratingParameters(angle = current_angle)

        self.convenience_parameters = {'current_angle': current_angle}

        self.meta_parameters = {'center_size':self.protocol_parameters['center_size'],
                                'center':self.adjustCenter(self.protocol_parameters['center'])}
    def loadStimuli(self, multicall):
        passed_parameters = self.epoch_parameters.copy()
        box_min_x = self.meta_parameters['center'][0] - self.meta_parameters['center_size']/2
        box_max_x = self.meta_parameters['center'][0] + self.meta_parameters['center_size']/2

        box_min_y = self.meta_parameters['center'][1] - self.meta_parameters['center_size']/2
        box_max_y = self.meta_parameters['center'][1] + self.meta_parameters['center_size']/2

        multicall.load_stim(name='MovingPatch', background = self.run_parameters['idle_color'], trajectory=RectangleTrajectory(w = 0, h = 0).to_dict())

        multicall.load_stim(**passed_parameters,
                            box_min_x=box_min_x, box_max_x=box_max_x, box_min_y=box_min_y, box_max_y=box_max_y,
                            hold=True)

    def getParameterDefaults(self):
        self.protocol_parameters = {'period':20.0,
                       'rate':20.0,
                       'color':1.0,
                       'background':0.0,
                       'angle':[0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0],
                       'center':[0, 0],
                       'center_size':120.0,
                       'randomize_order':True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'DriftingSquareGrating',
              'num_epochs':40,
              'pre_time':1.0,
              'stim_time':4.0,
              'tail_time':1.0,
              'idle_color':0.5}
# %%


class DriftingVsStationaryGrating(BaseProtocol):
    def __init__(self, user_name, rig_config):
        super().__init__(user_name, rig_config)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        stationary_code = [0, 1] #0 = stationary, 1 = drifting

        current_temporal_frequency, current_stationary_code = self.selectParametersFromLists((self.protocol_parameters['temporal_frequency'], stationary_code),
                                                                                             all_combinations = True,
                                                                                             randomize_order = self.protocol_parameters['randomize_order'])

        if current_stationary_code == 0: #stationary, contrast reversing grating
            self.epoch_parameters =  {'name':'ContrastReversingGrating',
                                      'temporal_waveform':'square',
                                      'spatial_period':self.protocol_parameters['spatial_period'],
                                      'temporal_frequency':current_temporal_frequency,
                                      'contrast_scale':self.protocol_parameters['contrast_scale'],
                                      'mean':self.protocol_parameters['mean'],
                                      'angle':self.protocol_parameters['angle']}

        elif current_stationary_code == 1: #drifting grating
            background = self.protocol_parameters['mean'] - self.protocol_parameters['contrast_scale'] * self.protocol_parameters['mean']
            color = self.protocol_parameters['mean'] + self.protocol_parameters['contrast_scale'] * self.protocol_parameters['mean']

            rate = current_temporal_frequency * self.protocol_parameters['spatial_period']
            self.epoch_parameters = {'name':'RotatingBars',
                                     'period':self.protocol_parameters['spatial_period'],
                                     'duty_cycle':0.5,
                                     'rate':rate,
                                     'color':color,
                                     'background':background,
                                     'angle':self.protocol_parameters['angle']}

        self.convenience_parameters = {'current_temporal_frequency': current_temporal_frequency,
                                       'current_stationary_code': current_stationary_code}

        self.meta_parameters = {'center_size':self.protocol_parameters['center_size'],
                                'center':self.adjustCenter(self.protocol_parameters['center'])}

    def loadStimuli(self, multicall):
        passed_parameters = self.epoch_parameters.copy()
        box_min_x = self.meta_parameters['center'][0] - self.meta_parameters['center_size']/2
        box_max_x = self.meta_parameters['center'][0] + self.meta_parameters['center_size']/2

        box_min_y = self.meta_parameters['center'][1] - self.meta_parameters['center_size']/2
        box_max_y = self.meta_parameters['center'][1] + self.meta_parameters['center_size']/2

        multicall.load_stim(name='MovingPatch', background = self.run_parameters['idle_color'], trajectory=RectangleTrajectory(w = 0, h = 0).to_dict())

        multicall.load_stim(**passed_parameters,
                            box_min_x=box_min_x, box_max_x=box_max_x, box_min_y=box_min_y, box_max_y=box_max_y,
                            hold=True)

    def getParameterDefaults(self):
        self.protocol_parameters = {'spatial_period':10.0,
                       'contrast_scale':1.0,
                       'mean':0.5,
                       'temporal_frequency':[0.5, 1.0, 2.0, 4.0, 8.0, 16.0],
                       'center':[0, 0],
                       'center_size':30.0,
                       'angle':0.0,
                       'randomize_order':True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'DriftingVsStationaryGrating',
              'num_epochs':60,
              'pre_time':1.0,
              'stim_time':4.0,
              'tail_time':1.0,
              'idle_color':0.5}

# %%


class ExpandingMovingSquare(BaseProtocol):
    def __init__(self, user_name, rig_config):
        super().__init__(user_name, rig_config)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        current_width, current_color, current_angle = self.selectParametersFromLists((self.protocol_parameters['width'], self.protocol_parameters['color'], self.protocol_parameters['angle']),
                                                                randomize_order = self.protocol_parameters['randomize_order'])

        self.epoch_parameters = self.getMovingPatchParameters(width = current_width, height = current_width, angle = current_angle, color = current_color)

        self.convenience_parameters = {'current_width': current_width,
                                       'current_color': current_color,
                                       'current_angle': current_angle}

    def getParameterDefaults(self):
        self.protocol_parameters = {'width':[2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0],
                       'color':[0.0, 1.0],
                       'center': [0, 0],
                       'speed':80.0,
                       'angle': [0.0, 90.0, 180.0, 270.0],
                       'randomize_order':True}


    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'ExpandingMovingSquare',
              'num_epochs':70,
              'pre_time':0.5,
              'stim_time':2.0,
              'tail_time':1.0,
              'idle_color':0.5}

# %%


class FlickeringPatch(BaseProtocol):
    def __init__(self, user_name, rig_config):
        super().__init__(user_name, rig_config)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        stimulus_ID = 'MovingPatch'
        stim_time = self.run_parameters['stim_time']

        current_temporal_frequency = self.selectParametersFromLists(self.protocol_parameters['temporal_frequency'],
                                                                randomize_order = self.protocol_parameters['randomize_order'])

        trajectory_sample_rate = 100 # Hz
        nPoints = trajectory_sample_rate * stim_time
        time_points = np.linspace(0, stim_time, nPoints)
        color_values = np.sin(time_points * 2 * np.pi * current_temporal_frequency)
        color_trajectory = list(zip(time_points,color_values))

        #adjust center to screen center
        adj_center = self.adjustCenter(self.protocol_parameters['center'])

        trajectory = RectangleTrajectory(x = adj_center[0],
                                              y = adj_center[1],
                                              angle = 0,
                                              h = self.protocol_parameters['height'],
                                              w = self.protocol_parameters['width'],
                                              color = color_trajectory).to_dict()

        self.epoch_parameters = {'name':stimulus_ID,
                            'background':self.run_parameters['idle_color'],
                            'trajectory':trajectory}

        self.convenience_parameters = {'current_temporal_frequency': current_temporal_frequency}

    def getParameterDefaults(self):
        self.protocol_parameters = {'height':10.0,
                       'width':10.0,
                       'center': [0, 0],
                       'temporal_frequency': [0.5, 1.0, 2.0, 4.0, 8.0, 16.0],
                       'randomize_order':True}


    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'FlickeringPatch',
              'num_epochs':30,
              'pre_time':1.0,
              'stim_time':4.0,
              'tail_time':1.0,
              'idle_color':0.5}

# %%


class UniformFlash(BaseProtocol):
    def __init__(self, user_name, rig_config):
        super().__init__(user_name, rig_config)

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


class LoomingPatch(BaseProtocol):
    def __init__(self, user_name, rig_config):
        super().__init__(user_name, rig_config)

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

        self.convenience_parameters = {'current_rv_ratio': current_rv_ratio,
                                       'time_steps': time_steps,
                                       'angular_size': angular_size,
                                       'current_trajectory_type': current_trajectory_type}

    def getParameterDefaults(self):
        self.protocol_parameters = {'color':0.0,
                       'center': [0, 0],
                       'start_size': 2.5,
                       'end_size': 80.0,
                       'rv_ratio':[5.0, 10.0, 20.0, 40.0, 80.0],
                       'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'LoomingPatch',
              'num_epochs':75,
              'pre_time':0.5,
              'stim_time':1.0,
              'tail_time':1.0,
              'idle_color':0.5}
# %%


class MovingRectangle(BaseProtocol):
    def __init__(self, user_name, rig_config):
        super().__init__(user_name, rig_config)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        current_angle = self.selectParametersFromLists(self.protocol_parameters['angle'],
                                                       randomize_order = self.protocol_parameters['randomize_order'])

        self.epoch_parameters = self.getMovingPatchParameters(angle = current_angle)

        self.convenience_parameters = {'current_angle': current_angle}

    def getParameterDefaults(self):
        self.protocol_parameters = {'width':5.0,
                       'height':5.0,
                       'color':0.0,
                       'center': [0, 0],
                       'speed':80.0,
                       'angle': [0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0],
                       'randomize_order':True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'MovingRectangle',
              'num_epochs':40,
              'pre_time':0.5,
              'stim_time':2.0,
              'tail_time':1.0,
              'idle_color':0.5}
# %%


class MovingSquareMapping(BaseProtocol):
    def __init__(self, user_name, rig_config):
        super().__init__(user_name, rig_config)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        #adjust to screen center
        az_loc = [x + self.screen_center[0] for x in self.protocol_parameters['azimuth_locations']]
        el_loc = [x + self.screen_center[1] for x in self.protocol_parameters['elevation_locations']]

        if type(az_loc) is not list:
            az_loc = [az_loc]
        if type(el_loc) is not list:
            el_loc = [el_loc]

        center_el = np.median(el_loc)
        center_az = np.median(az_loc)

        location_list = np.concatenate((az_loc, el_loc))
        movement_axis_list = np.concatenate((np.ones(len(az_loc)), 2*np.ones(len(el_loc))))

        current_search_axis_code, current_location = self.selectParametersFromLists((movement_axis_list, location_list),
                                                                                              all_combinations = False,
                                                                                              randomize_order = self.protocol_parameters['randomize_order'])

        if current_search_axis_code == 1:
            current_search_axis = 'azimuth'
            angle = 90
            center = [current_location, center_el]
        elif current_search_axis_code == 2:
            current_search_axis = 'elevation'
            angle = 0
            center = [center_az, current_location]

        self.epoch_parameters = self.getMovingPatchParameters(height = self.protocol_parameters['square_width'],
                                                              width = self.protocol_parameters['square_width'],
                                                              angle = angle,
                                                              center = center)

        self.convenience_parameters = {'current_search_axis': current_search_axis,
                                       'current_location': current_location,
                                       'current_angle': angle,
                                       'current_center': center}

    def getParameterDefaults(self):
        self.protocol_parameters = {'square_width':5.0,
                       'color':0.0,
                       'elevation_locations': [-20, -15, -10, -5, 0, 5, 10, 15, 20],
                       'azimuth_locations': [-20, -15, -10, -5, 0, 5, 10, 15, 20],
                       'speed':80.0,
                       'randomize_order':True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'MovingSquareMapping',
              'num_epochs':100,
              'pre_time':0.5,
              'stim_time':2.0,
              'tail_time':1.0,
              'idle_color':0.5}

# %%


class SequentialOrRandomMotion(BaseProtocol):
    def __init__(self, user_name, rig_config):
        super().__init__(user_name, rig_config)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        stimulus_ID = 'MovingPatch'

        #adjust to screen center...
        adj_az = [x + self.screen_center[0] for x in self.protocol_parameters['azimuth_boundaries']]
        adj_el = self.screen_center[1] + self.protocol_parameters['elevation']

        stim_time = self.run_parameters['stim_time']
        no_steps = self.protocol_parameters['no_steps']

        time_steps = np.linspace(0,stim_time,no_steps)
        x_steps = np.linspace(adj_az[0],adj_az[1],no_steps)
        y_steps = np.linspace(adj_el,adj_el,no_steps)

        #switch back and forth between sequential and random
        randomized_order = bool(np.mod(self.num_epochs_completed,2))
        if randomized_order:
            x_steps = np.random.permutation(x_steps)

        # time-modulated trajectories
        x = Trajectory(list(zip(time_steps,x_steps)), kind = 'previous') #note interp kind is previous
        y = Trajectory(list(zip(time_steps,y_steps)), kind = 'previous')
        # constant trajectories:
        w = Trajectory(self.protocol_parameters['square_width'])
        h = Trajectory(self.protocol_parameters['square_width'])
        angle = Trajectory(0)
        color = Trajectory(self.protocol_parameters['color'])
        trajectory = {'x': x.to_dict(), 'y': y.to_dict(), 'w': w.to_dict(), 'h': h.to_dict(),
            'angle': angle.to_dict(), 'color': color.to_dict()}

        self.epoch_parameters = {'name':stimulus_ID,
                            'background':self.run_parameters['idle_color'],
                            'trajectory':trajectory}
        self.convenience_parameters = {'randomized_order': randomized_order,
                                       'x_steps': x_steps}

    def getParameterDefaults(self):
        self.protocol_parameters = {'square_width':5.0,
                       'color':0.0,
                       'elevation': 0.0,
                       'azimuth_boundaries': [-15.0, 15.0],
                       'no_steps': 8}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'SequentialOrRandomMotion',
              'num_epochs':20,
              'pre_time':0.5,
              'stim_time':0.5,
              'tail_time':1.0,
              'idle_color':0.5}

# %%


class SpeedTuningSquare(BaseProtocol):
    def __init__(self, user_name, rig_config):
        super().__init__(user_name, rig_config)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        current_speed = self.selectParametersFromLists(self.protocol_parameters['speed'],
                                                                randomize_order = self.protocol_parameters['randomize_order'])

        self.epoch_parameters = self.getMovingPatchParameters(speed = current_speed,
                                                              height = self.protocol_parameters['width'],
                                                              distance_to_travel = 140)

        self.convenience_parameters = {'current_speed': current_speed}

    def getParameterDefaults(self):
        self.protocol_parameters = {'width': 5.0,
                       'color':0.0,
                       'center': [0, 0],
                       'speed':[20.0, 30.0, 40.0, 60.0, 80.0, 100.0, 120.0, 140.0, 160.0, 180.0, 200.0],
                       'angle': 0.0,
                       'randomize_order':True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'SpeedTuningSquare',
              'num_epochs':50,
              'pre_time':0.5,
              'stim_time':7.0,
              'tail_time':1.0,
              'idle_color':0.5}

# %%


class CenterSurroundDriftingSquareGrating(BaseProtocol):
    def __init__(self, user_name, rig_config):
        super().__init__(user_name, rig_config)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        current_surround_rate, current_center_rate = self.selectParametersFromLists((self.protocol_parameters['rate_surround'], self.protocol_parameters['rate_center']),
                                                                                             all_combinations = True,
                                                                                             randomize_order = self.protocol_parameters['randomize_order'])

        color_surround, background_surround = self.getColorAndBackgroundFromContrast(self.protocol_parameters['contrast_surround'])
        color_center, background_center = self.getColorAndBackgroundFromContrast(self.protocol_parameters['contrast_center'])

        surround_parameters = self.getRotatingGratingParameters(angle = self.protocol_parameters['angle'],
                                                                rate = current_surround_rate,
                                                                period = self.protocol_parameters['period_surround'],
                                                                color = color_surround,
                                                                background = background_surround)
        center_parameters = self.getRotatingGratingParameters(angle = self.protocol_parameters['angle'],
                                                                rate = current_center_rate,
                                                                period = self.protocol_parameters['period_center'],
                                                                color = color_center,
                                                                background = background_center)

        self.epoch_parameters = (surround_parameters, center_parameters)

        self.meta_parameters = {'center_size':self.protocol_parameters['center_size'],
                                'center':self.adjustCenter(self.protocol_parameters['center'])}
        self.convenience_parameters = {'current_surround_rate': current_surround_rate,
                                       'current_center_rate': current_center_rate}

    def loadStimuli(self, multicall):
        surround_parameters = self.epoch_parameters[0].copy()
        center_parameters = self.epoch_parameters[1].copy()

        box_min_x = self.meta_parameters['center'][0] - self.meta_parameters['center_size']/2
        box_max_x = self.meta_parameters['center'][0] + self.meta_parameters['center_size']/2

        box_min_y = self.meta_parameters['center'][1] - self.meta_parameters['center_size']/2
        box_max_y = self.meta_parameters['center'][1] + self.meta_parameters['center_size']/2

        multicall.load_stim(**surround_parameters)
        multicall.load_stim(**center_parameters,
                            box_min_x=box_min_x, box_max_x=box_max_x, box_min_y=box_min_y, box_max_y=box_max_y,
                            hold=True)

    def getParameterDefaults(self):
        self.protocol_parameters = {'period_center':20.0,
                       'rate_center':[20.0, 40.0, 80.0],
                       'contrast_center': 1.0,
                       'period_surround':20.0,
                       'rate_surround':[-100.0, -80.0, -40.0, -20.0, -10.0, 0.0,
                                     10.0, 20.0, 40.0, 80.0, 100.0],
                       'contrast_surround': 0.5,
                       'center_size':20.0,
                       'center': [0, 0],
                       'angle':0.0,
                       'randomize_order':True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'CenterSurroundDriftingSquareGrating',
              'num_epochs':165,
              'pre_time':1.0,
              'stim_time':4.0,
              'tail_time':1.0,
              'idle_color':0.5}

# %%


class MovingPatchOnDriftingGrating(BaseProtocol):
    def __init__(self, user_name, rig_config):
        super().__init__(user_name, rig_config)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        current_patch_speed, current_grate_rate = self.selectParametersFromLists((self.protocol_parameters['patch_speed'], self.protocol_parameters['grate_rate']),
                                                                                             all_combinations = True,
                                                                                             randomize_order = self.protocol_parameters['randomize_order'])

        patch_parameters = self.getMovingPatchParameters(center = self.adjustCenter(self.protocol_parameters['center']),
                                                         angle = self.protocol_parameters['angle'],
                                                         speed = current_patch_speed,
                                                         width = self.protocol_parameters['patch_size'],
                                                         height = self.protocol_parameters['patch_size'],
                                                         color = self.protocol_parameters['patch_color'],
                                                         distance_to_travel = 140)
        patch_parameters['background'] = None #transparent background

        grate_color, grate_background = self.getColorAndBackgroundFromContrast(self.protocol_parameters['grate_contrast'])
        grate_parameters = self.getRotatingGratingParameters(angle = self.protocol_parameters['angle'],
                                                    rate = current_grate_rate,
                                                    period = self.protocol_parameters['grate_period'],
                                                    color = grate_color,
                                                    background = grate_background)

        self.epoch_parameters = (grate_parameters, patch_parameters)
        self.convenience_parameters = {'current_patch_speed': current_patch_speed,
                                       'current_grate_rate': current_grate_rate}

    def loadStimuli(self, multicall):
        grate_parameters = self.epoch_parameters[0].copy()
        patch_parameters = self.epoch_parameters[1].copy()

        multicall.load_stim(**grate_parameters)
        multicall.load_stim(**patch_parameters, vary='intensity', hold=True)

    def getParameterDefaults(self):
        self.protocol_parameters = {'center': [0, 0],
                                    'patch_size':10.0,
                                    'patch_color':0.0,
                       'patch_speed':[20.0, 40.0, 80.0],
                       'grate_period':10.0,
                       'grate_rate':[-100.0, -80.0, -40.0, -20.0, -10.0, 0.0,
                                     10.0, 20.0, 40.0, 80.0, 100.0],
                       'grate_contrast':0.5,
                       'angle':0.0,
                       'randomize_order':True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'MovingPatchOnDriftingGrating',
              'num_epochs':165,
              'pre_time':1.0,
              'stim_time':7.0,
              'tail_time':1.0,
              'idle_color':0.5}

# %%


class VelocitySwitchGrating(BaseProtocol):
    def __init__(self, user_name, rig_config):
        super().__init__(user_name, rig_config)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        current_start_rate, current_switch_rate = self.selectParametersFromLists((self.protocol_parameters['start_rate'], self.protocol_parameters['switch_rate']),
                                                                                             all_combinations = True,
                                                                                             randomize_order = self.protocol_parameters['randomize_order'])

        self.epoch_parameters = self.getRotatingGratingParameters(angle = self.protocol_parameters['angle'],
                                                    rate = current_start_rate,
                                                    period = self.protocol_parameters['grate_period'],
                                                    color = self.protocol_parameters['grate_color'],
                                                    background = self.protocol_parameters['grate_background'])

        self.convenience_parameters = {'current_start_rate': current_start_rate,
                                       'current_switch_rate': current_switch_rate}

        self.meta_parameters = {'center_size':self.protocol_parameters['center_size'],
                                'center':self.adjustCenter(self.protocol_parameters['center']),
                                'switch_rate':current_switch_rate}

    def loadStimuli(self, multicall):
        passed_parameters = self.epoch_parameters.copy()
        box_min_x = self.meta_parameters['center'][0] - self.meta_parameters['center_size']/2
        box_max_x = self.meta_parameters['center'][0] + self.meta_parameters['center_size']/2

        box_min_y = self.meta_parameters['center'][1] - self.meta_parameters['center_size']/2
        box_max_y = self.meta_parameters['center'][1] + self.meta_parameters['center_size']/2

        multicall.load_stim(name='MovingPatch', background = self.run_parameters['idle_color'], trajectory=RectangleTrajectory(w = 0, h = 0).to_dict())

        multicall.load_stim(**passed_parameters,
                            box_min_x=box_min_x, box_max_x=box_max_x, box_min_y=box_min_y, box_max_y=box_max_y,
                            hold=True)



    def startStimuli(self, multicall):
        sleep(self.run_parameters['pre_time'])
        #stim time
        multicall.start_stim()
        multicall.start_corner_square()
        multicall()
        sleep(self.run_parameters['stim_time'] / 2)

        multicall.update_stim(rate=self.meta_parameters['switch_rate'])
        multicall()

        sleep(self.run_parameters['stim_time'] / 2)

        #tail time
        multicall.stop_stim()
        multicall.black_corner_square()
        multicall()
        sleep(self.run_parameters['tail_time'])

    def getParameterDefaults(self):
        self.protocol_parameters = {'center':[0, 0],
                                    'center_size':20.0,
                                    'start_rate':[20.0, 40.0, 80.0],
                                    'switch_rate':[-100.0, -80.0, -40.0, -20.0, -10.0, 0.0,
                                                   10.0, 20.0, 40.0, 80.0, 100.0],
                                    'grate_period':10.0,
                                    'grate_color':1.0,
                                    'grate_background':0,
                                    'angle':0.0,
                                    'randomize_order':True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'VelocitySwitchGrating',
              'num_epochs':165,
              'pre_time':1.0,
              'stim_time':8.0,
              'tail_time':1.0,
              'idle_color':0.5}
# %%


class SparseNoise(BaseProtocol):
    def __init__(self, user_name, rig_config):
        super().__init__(user_name, rig_config)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        stimulus_ID = 'RandomGrid'

        start_seed = int(np.random.choice(range(int(1e6))))

        distribution_data = {'name':'SparseBinary',
                                 'args':[],
                                 'kwargs':{'rand_min':self.protocol_parameters['rand_min'],
                                           'rand_max':self.protocol_parameters['rand_max'],
                                           'sparseness':self.protocol_parameters['sparseness']}}

        self.epoch_parameters = {'name': stimulus_ID,
                            'theta_period': self.protocol_parameters['checker_width'],
                            'phi_period': self.protocol_parameters['checker_width'],
                            'start_seed': start_seed,
                            'update_rate': self.protocol_parameters['update_rate'],
                            'distribution_data': distribution_data}

        self.convenience_parameters = {'distribution_name': 'SparseBinary',
                                       'start_seed': start_seed}

    def getParameterDefaults(self):
        self.protocol_parameters = {'checker_width':5.0,
                               'update_rate':8.0,
                               'rand_min': 0.0,
                               'rand_max':1.0,
                               'sparseness':0.95}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'SparseNoise',
              'num_epochs':10,
              'pre_time':1.0,
              'stim_time':30.0,
              'tail_time':1.0,
              'idle_color':0.5}


# %%


class StationaryMapping(BaseProtocol):
    def __init__(self, user_name, rig_config):
        super().__init__(user_name, rig_config)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        stimulus_ID = 'MovingPatch'
        #adjust to screen center
        az_loc = [x + self.screen_center[0] for x in self.protocol_parameters['azimuth_locations']]
        el_loc = [x + self.screen_center[1] for x in self.protocol_parameters['elevation_locations']]

        if type(az_loc) is not list:
            az_loc = [az_loc]
        if type(el_loc) is not list:
            el_loc = [el_loc]


        stim_time = self.run_parameters['stim_time'] #sec
        flash_duration = self.protocol_parameters['flash_duration'] #sec

        time_steps = np.arange(0,stim_time,flash_duration)
        no_steps = len(time_steps)
        x_steps = np.random.choice(az_loc, size = no_steps, replace=True)
        y_steps = np.random.choice(el_loc, size = no_steps, replace=True)


        # time-modulated trajectories
        x = Trajectory(list(zip(time_steps,x_steps)), kind = 'previous') #note interp kind is previous
        y = Trajectory(list(zip(time_steps,y_steps)), kind = 'previous')
        # constant trajectories:
        w = Trajectory(self.protocol_parameters['square_width'])
        h = Trajectory(self.protocol_parameters['square_width'])
        angle = Trajectory(0)
        color = Trajectory(self.protocol_parameters['color'])
        trajectory = {'x': x.to_dict(), 'y': y.to_dict(), 'w': w.to_dict(), 'h': h.to_dict(),
            'angle': angle.to_dict(), 'color': color.to_dict()}

        self.epoch_parameters = {'name':stimulus_ID,
                            'background':self.run_parameters['idle_color'],
                            'trajectory':trajectory}
        self.convenience_parameters = {'time_steps': time_steps,
                                       'x_steps': x_steps,
                                       'y_steps': y_steps}

    def getParameterDefaults(self):
        self.protocol_parameters = {'square_width':5.0,
                       'color':0.0,
                       'elevation_locations': [-20, -15, -10, -5, 0, 5, 10, 15, 20],
                       'azimuth_locations': [-20, -15, -10, -5, 0, 5, 10, 15, 20],
                       'flash_duration':0.25}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'StationaryMapping',
              'num_epochs':6,
              'pre_time':2.0,
              'stim_time':100.0,
              'tail_time':2.0,
              'idle_color':0.5}

# %%


class SineTrajectoryPatch(BaseProtocol):
    def __init__(self, user_name, rig_config):
        super().__init__(user_name, rig_config)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        stimulus_ID = 'MovingPatch'

        current_temporal_frequency = self.selectParametersFromLists(self.protocol_parameters['temporal_frequency'],
                                                                randomize_order = self.protocol_parameters['randomize_order'])

        adj_center = self.adjustCenter(self.protocol_parameters['center'])
        centerX = adj_center[0]
        centerY = adj_center[1]
        amplitude = self.protocol_parameters['amplitude']
        movement_axis = self.protocol_parameters['movement_axis']

        stim_time = self.run_parameters['stim_time']

        time_steps = np.arange(0,stim_time,0.005) #time steps of trajectory
        distance_along_movement_axis = amplitude * np.sin(time_steps * 2 * np.pi * current_temporal_frequency)

        x_steps = centerX + np.cos(np.radians(movement_axis)) * distance_along_movement_axis
        y_steps = centerY + np.sin(np.radians(movement_axis)) * distance_along_movement_axis

        # time-modulated trajectories
        x = Trajectory(list(zip(time_steps,x_steps)), kind = 'previous')
        y = Trajectory(list(zip(time_steps,y_steps)), kind = 'previous')

        # constant trajectories:
        color = Trajectory(self.protocol_parameters['color'])
        w = Trajectory(self.protocol_parameters['width'])
        h = Trajectory(self.protocol_parameters['height'])
        angle = Trajectory(movement_axis)

        trajectory = {'x': x.to_dict(), 'y': y.to_dict(), 'w': w.to_dict(), 'h': h.to_dict(),
            'angle': angle.to_dict(), 'color': color.to_dict()}


        self.epoch_parameters = {'name':stimulus_ID,
                            'background':self.run_parameters['idle_color'],
                            'trajectory':trajectory}

        self.convenience_parameters = {'current_temporal_frequency': current_temporal_frequency,
                                       'time_steps': time_steps,
                                       'x_steps': x_steps,
                                       'y_steps': y_steps}

    def getParameterDefaults(self):
        self.protocol_parameters = {'width':5.0,
                       'height':5.0,
                       'color':0.0,
                       'center': [0, 0],
                       'amplitude': 20, #deg, half of total travel distance
                       'temporal_frequency': [1, 2, 4, 6, 8], #Hz
                       'movement_axis': 0,
                       'randomize_order':True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'SineTrajectoryPatch',
              'num_epochs':40,
              'pre_time':0.5,
              'stim_time':2.0,
              'tail_time':0.5,
              'idle_color':0.5}
