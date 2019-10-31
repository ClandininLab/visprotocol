#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 10:20:02 2018

@author: mhturner
"""
import numpy as np

from visprotocol.protocol import clandinin_protocol
from flystim.trajectory import Trajectory


class BaseProtocol(clandinin_protocol.BaseProtocol):
    def __init__(self, user_name, rig_config):
        super().__init__(user_name, rig_config)  # call the parent class init method

    def getMovingPatchParameters(self, center=None, angle=None, speed=None, width=None, height=None, color=None, distance_to_travel=None):
        if center is None: center = self.adjustCenter(self.protocol_parameters['center'])
        if angle is None: angle = self.protocol_parameters['angle']
        if speed is None: speed = self.protocol_parameters['speed']
        if width is None: width = self.protocol_parameters['width']
        if height is None: height = self.protocol_parameters['height']
        if color is None: color = self.protocol_parameters['color']

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

        else:  # distance_to_travel is specified, so only go that distance at the defined speed. Hang pre- and post- for any extra stim time
            travel_time = distance_to_travel / speed
            if travel_time > stim_time:
                print('Warning: stim_time is too short to show whole trajectory at this speed!')
                hang_time = 0
            else:
                hang_time = (stim_time - travel_time)/2

            # split up hang time in pre and post such that trajectory always hits centerX,centerY at stim_time/2
            x_1 = (0, centerX - np.cos(np.radians(angle)) * distance_to_travel/2)
            x_2 = (hang_time, centerX - np.cos(np.radians(angle)) * distance_to_travel/2)
            x_3 = (hang_time+travel_time, centerX + np.cos(np.radians(angle)) * distance_to_travel/2)
            x_4 = (hang_time+travel_time+hang_time, centerX + np.cos(np.radians(angle)) * distance_to_travel/2)

            y_1 = (0, centerY - np.sin(np.radians(angle)) * distance_to_travel/2)
            y_2 = (hang_time, centerY - np.sin(np.radians(angle)) * distance_to_travel/2)
            y_3 = (hang_time+travel_time, centerY + np.sin(np.radians(angle)) * distance_to_travel/2)
            y_4 = (hang_time+travel_time+hang_time, centerY + np.sin(np.radians(angle)) * distance_to_travel/2)

            x = [x_1, x_2, x_3, x_4]
            y = [y_1, y_2, y_3, y_4]

        x_trajectory = Trajectory(x, kind='linear').to_dict()
        y_trajectory = Trajectory(y, kind='linear').to_dict()

        patch_parameters = {'name': 'MovingPatch',
                            'width': width,
                            'height': height,
                            'color': color,
                            'theta': x_trajectory,
                            'phi': y_trajectory,
                            'angle': angle}
        return patch_parameters


    def getMovingSpotParameters(self, center=None, angle=None, speed=None, radius=None, color=None, distance_to_travel=None):
        if center is None: center = self.adjustCenter(self.protocol_parameters['center'])
        if angle is None: angle = self.protocol_parameters['angle']
        if speed is None: speed = self.protocol_parameters['speed']
        if radius is None: radius = self.protocol_parameters['radius']
        if color is None: color = self.protocol_parameters['color']

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

        else:  # distance_to_travel is specified, so only go that distance at the defined speed. Hang pre- and post- for any extra stim time
            travel_time = distance_to_travel / speed
            if travel_time > stim_time:
                print('Warning: stim_time is too short to show whole trajectory at this speed!')
                hang_time = 0
            else:
                hang_time = (stim_time - travel_time)/2

            # split up hang time in pre and post such that trajectory always hits centerX,centerY at stim_time/2
            x_1 = (0, centerX - np.cos(np.radians(angle)) * distance_to_travel/2)
            x_2 = (hang_time, centerX - np.cos(np.radians(angle)) * distance_to_travel/2)
            x_3 = (hang_time+travel_time, centerX + np.cos(np.radians(angle)) * distance_to_travel/2)
            x_4 = (hang_time+travel_time+hang_time, centerX + np.cos(np.radians(angle)) * distance_to_travel/2)

            y_1 = (0, centerY - np.sin(np.radians(angle)) * distance_to_travel/2)
            y_2 = (hang_time, centerY - np.sin(np.radians(angle)) * distance_to_travel/2)
            y_3 = (hang_time+travel_time, centerY + np.sin(np.radians(angle)) * distance_to_travel/2)
            y_4 = (hang_time+travel_time+hang_time, centerY + np.sin(np.radians(angle)) * distance_to_travel/2)

            x = [x_1, x_2, x_3, x_4]
            y = [y_1, y_2, y_3, y_4]

        x_trajectory = Trajectory(x, kind='linear').to_dict()
        y_trajectory = Trajectory(y, kind='linear').to_dict()

        spot_parameters = {'name': 'MovingSpot',
                           'radius': radius,
                           'color': color,
                           'theta': x_trajectory,
                           'phi': y_trajectory}
        return spot_parameters

# %%

# TODO update
# class CheckerboardWhiteNoise(BaseProtocol):
#     def __init__(self, user_name, rig_config):
#         super().__init__(user_name, rig_config)
#
#         self.getRunParameterDefaults()
#         self.getParameterDefaults()
#
#     def getEpochParameters(self):
#         stimulus_ID  = 'RandomGrid'
#
#         start_seed = int(np.random.choice(range(int(1e6))))
#
#
#         distribution_data = {'name':'Gaussian',
#                                  'args':[],
#                                  'kwargs':{'rand_mean':self.protocol_parameters['rand_mean'],
#                                            'rand_stdev':self.protocol_parameters['rand_stdev']}}
#
#         self.epoch_parameters = {'name':stimulus_ID,
#                             'theta_period':self.protocol_parameters['checker_width'],
#                             'phi_period':self.protocol_parameters['checker_width'],
#                             'start_seed':start_seed,
#                             'update_rate':self.protocol_parameters['update_rate'],
#                             'distribution_data':distribution_data}
#         self.convenience_parameters = {'start_seed': start_seed}
#
#     def getParameterDefaults(self):
#         self.protocol_parameters = {'checker_width':5.0,
#                        'update_rate':0.5,
#                        'rand_mean': 0.5,
#                        'rand_stdev':0.15}
#
#     def getRunParameterDefaults(self):
#         self.run_parameters = {'protocol_ID':'CheckerboardWhiteNoise',
#               'num_epochs':10,
#               'pre_time':1.0,
#               'stim_time':30.0,
#               'tail_time':1.0,
#               'idle_color':0.5}

# %%


class ContrastReversingGrating(BaseProtocol):
    def __init__(self, user_name, rig_config):
        super().__init__(user_name, rig_config)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        # TODO: center size with aperture (center and center_size): maybe parent class aperture method?
        current_temporal_frequency = self.selectParametersFromLists(self.protocol_parameters['temporal_frequency'], randomize_order=self.protocol_parameters['randomize_order'])

        # Make the contrast trajectory
        t = np.arange(0, self.run_parameters['stim_time'], 0.001)
        c = self.protocol_parameters['contrast'] * np.sin(2*np.pi*current_temporal_frequency*t)
        tv_pairs = list(zip(t, c))
        contrast_traj = Trajectory(tv_pairs, kind='linear').to_dict()

        self.epoch_parameters = {'name': 'CylindricalGrating',
                                 'period': self.protocol_parameters['spatial_period'],
                                 'color': [1, 1, 1, 1],
                                 'mean': self.protocol_parameters['mean'],
                                 'contrast': contrast_traj,
                                 'angle': self.protocol_parameters['angle'],
                                 'offset': 0.0,
                                 'cylinder_radius': 1.0,
                                 'cylinder_height': 10.0,
                                 'profile': 'square'}

        self.convenience_parameters = {'current_temporal_frequency': current_temporal_frequency}

        self.meta_parameters = {'center_size': self.protocol_parameters['center_size'],
                                'center': self.adjustCenter(self.protocol_parameters['center'])}

    def getParameterDefaults(self):
        self.protocol_parameters = {'spatial_period': 20.0,
                                    'contrast': 1.0,
                                    'mean': 0.5,
                                    'temporal_frequency': [0.5, 1.0, 2.0, 4.0, 8.0, 16.0],
                                    'center': [0, 0],
                                    'center_size': 40.0,
                                    'angle': 0.0,
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'ContrastReversingGrating',
                               'num_epochs': 40,
                               'pre_time': 1.0,
                               'stim_time': 4.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}

# %%


class DriftingSquareGrating(BaseProtocol):
    def __init__(self, user_name, rig_config):
        super().__init__(user_name, rig_config)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        # TODO: center size with aperture (center and center_size)
        current_angle = self.selectParametersFromLists(self.protocol_parameters['angle'], randomize_order = self.protocol_parameters['randomize_order'])

        self.epoch_parameters = {'name': 'RotatingGrating',
                                 'period': self.protocol_parameters['period'],
                                 'rate': self.protocol_parameters['rate'],
                                 'color': [1, 1, 1, 1],
                                 'mean': self.protocol_parameters['mean'],
                                 'contrast': self.protocol_parameters['contrast'],
                                 'angle': current_angle,
                                 'offset': 0.0,
                                 'cylinder_radius': 1,
                                 'cylinder_height': 10,
                                 'profile': 'square'}

        self.convenience_parameters = {'current_angle': current_angle}

        self.meta_parameters = {'center_size': self.protocol_parameters['center_size'],
                                'center': self.adjustCenter(self.protocol_parameters['center'])}

    def getParameterDefaults(self):
        self.protocol_parameters = {'period': 20.0,
                                    'rate': 20.0,
                                    'contrast': 1.0,
                                    'mean': 0.5,
                                    'angle': [0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0],
                                    'center': [0, 0],
                                    'center_size': 180.0,
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'DriftingSquareGrating',
                               'num_epochs': 40,
                               'pre_time': 1.0,
                               'stim_time': 4.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}
# %%

# TODO update or toss?
# class DriftingVsStationaryGrating(BaseProtocol):
#     def __init__(self, user_name, rig_config):
#         super().__init__(user_name, rig_config)
#
#         self.getRunParameterDefaults()
#         self.getParameterDefaults()
#
#     def getEpochParameters(self):
#         stationary_code = [0, 1] #0 = stationary, 1 = drifting
#
#         current_temporal_frequency, current_stationary_code = self.selectParametersFromLists((self.protocol_parameters['temporal_frequency'], stationary_code),
#                                                                                              all_combinations = True,
#                                                                                              randomize_order = self.protocol_parameters['randomize_order'])
#
#         if current_stationary_code == 0: #stationary, contrast reversing grating
#             self.epoch_parameters =  {'name':'ContrastReversingGrating',
#                                       'temporal_waveform':'square',
#                                       'spatial_period':self.protocol_parameters['spatial_period'],
#                                       'temporal_frequency':current_temporal_frequency,
#                                       'contrast_scale':self.protocol_parameters['contrast_scale'],
#                                       'mean':self.protocol_parameters['mean'],
#                                       'angle':self.protocol_parameters['angle']}
#
#         elif current_stationary_code == 1: #drifting grating
#             background = self.protocol_parameters['mean'] - self.protocol_parameters['contrast_scale'] * self.protocol_parameters['mean']
#             color = self.protocol_parameters['mean'] + self.protocol_parameters['contrast_scale'] * self.protocol_parameters['mean']
#
#             rate = current_temporal_frequency * self.protocol_parameters['spatial_period']
#             self.epoch_parameters = {'name':'RotatingBars',
#                                      'period':self.protocol_parameters['spatial_period'],
#                                      'duty_cycle':0.5,
#                                      'rate':rate,
#                                      'color':color,
#                                      'background':background,
#                                      'angle':self.protocol_parameters['angle']}
#
#         self.convenience_parameters = {'current_temporal_frequency': current_temporal_frequency,
#                                        'current_stationary_code': current_stationary_code}
#
#         self.meta_parameters = {'center_size':self.protocol_parameters['center_size'],
#                                 'center':self.adjustCenter(self.protocol_parameters['center'])}
#
#     def loadStimuli(self, multicall):
#         passed_parameters = self.epoch_parameters.copy()
#         box_min_x = self.meta_parameters['center'][0] - self.meta_parameters['center_size']/2
#         box_max_x = self.meta_parameters['center'][0] + self.meta_parameters['center_size']/2
#
#         box_min_y = self.meta_parameters['center'][1] - self.meta_parameters['center_size']/2
#         box_max_y = self.meta_parameters['center'][1] + self.meta_parameters['center_size']/2
#
#         multicall.load_stim(name='MovingPatch', background = self.run_parameters['idle_color'], trajectory=RectangleTrajectory(w = 0, h = 0).to_dict())
#
#         multicall.load_stim(**passed_parameters,
#                             box_min_x=box_min_x, box_max_x=box_max_x, box_min_y=box_min_y, box_max_y=box_max_y,
#                             hold=True)
#
#     def getParameterDefaults(self):
#         self.protocol_parameters = {'spatial_period':10.0,
#                        'contrast_scale':1.0,
#                        'mean':0.5,
#                        'temporal_frequency':[0.5, 1.0, 2.0, 4.0, 8.0, 16.0],
#                        'center':[0, 0],
#                        'center_size':30.0,
#                        'angle':0.0,
#                        'randomize_order':True}
#
#     def getRunParameterDefaults(self):
#         self.run_parameters = {'protocol_ID':'DriftingVsStationaryGrating',
#               'num_epochs':60,
#               'pre_time':1.0,
#               'stim_time':4.0,
#               'tail_time':1.0,
#               'idle_color':0.5}

# %%


class ExpandingMovingSpot(BaseProtocol):
    def __init__(self, user_name, rig_config):
        super().__init__(user_name, rig_config)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        current_diameter, current_intensity = self.selectParametersFromLists((self.protocol_parameters['diameter'], self.protocol_parameters['intensity']), randomize_order=self.protocol_parameters['randomize_order'])

        self.epoch_parameters = self.getMovingSpotParameters(radius=current_diameter/2,
                                                             color=current_intensity)

        self.convenience_parameters = {'current_diameter': current_diameter,
                                       'current_intensity': current_intensity}

    def getParameterDefaults(self):
        self.protocol_parameters = {'diameter': [2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0],
                                    'intensity': [0.0, 1.0],
                                    'center': [0, 0],
                                    'speed': 80.0,
                                    'angle': 0.0,
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'ExpandingMovingSquare',
                               'num_epochs': 70,
                               'pre_time': 0.5,
                               'stim_time': 2.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}

# %%


class FlickeringPatch(BaseProtocol):
    def __init__(self, user_name, rig_config):
        super().__init__(user_name, rig_config)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        adj_center = self.adjustCenter(self.protocol_parameters['center'])

        current_temporal_frequency = self.selectParametersFromLists(self.protocol_parameters['temporal_frequency'], randomize_order=self.protocol_parameters['randomize_order'])

        # make color trajectory
        t = np.arange(0, self.run_parameters['stim_time'], 0.001)
        contrast = self.protocol_parameters['contrast'] * np.sin(2*np.pi*current_temporal_frequency*t)
        col = self.protocol_parameters['mean'] + self.protocol_parameters['mean'] * contrast
        tv_pairs = list(zip(t, col))
        color_traj = Trajectory(tv_pairs, kind='linear').to_dict()

        self.epoch_parameters = {'name': 'MovingPatch',
                                 'width': self.protocol_parameters['width'],
                                 'height': self.protocol_parameters['height'],
                                 'sphere_radius': 1,
                                 'color': color_traj,
                                 'theta': adj_center[0],
                                 'phi': adj_center[1],
                                 'angle': 0}

        self.convenience_parameters = {'current_temporal_frequency': current_temporal_frequency}

    def getParameterDefaults(self):
        self.protocol_parameters = {'height': 10.0,
                                    'width': 10.0,
                                    'center': [0, 0],
                                    'contrast': 1.0,
                                    'mean': 0.5,
                                    'temporal_frequency': [0.5, 1.0, 2.0, 4.0, 8.0, 16.0],
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'FlickeringPatch',
                               'num_epochs': 30,
                               'pre_time': 1.0,
                               'stim_time': 4.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}

# %%


class UniformFlash(BaseProtocol):
    def __init__(self, user_name, rig_config):
        super().__init__(user_name, rig_config)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        adj_center = self.adjustCenter(self.protocol_parameters['center'])

        current_intensity = self.selectParametersFromLists(self.protocol_parameters['intensity'], randomize_order=self.protocol_parameters['randomize_order'])

        self.epoch_parameters = {'name': 'MovingPatch',
                                 'width': self.protocol_parameters['width'],
                                 'height': self.protocol_parameters['height'],
                                 'sphere_radius': 1,
                                 'color': current_intensity,
                                 'theta': adj_center[0],
                                 'phi': adj_center[1],
                                 'angle': 0}
        self.convenience_parameters = {'current_intensity': current_intensity}

    def getParameterDefaults(self):
        self.protocol_parameters = {'height': 120.0,
                                    'width': 120.0,
                                    'center': [0, 0],
                                    'intensity': [1.0, 0.0],
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'UniformFlash',
                               'num_epochs': 10,
                               'pre_time': 1.0,
                               'stim_time': 0.5,
                               'tail_time': 1.0,
                               'idle_color': 0.5}
# %%


class LoomingSpot(BaseProtocol):
    def __init__(self, user_name, rig_config):
        super().__init__(user_name, rig_config)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        stim_time = self.run_parameters['stim_time']
        start_size = self.protocol_parameters['start_size']
        end_size = self.protocol_parameters['end_size']

        # adjust center to screen center
        adj_center = self.adjustCenter(self.protocol_parameters['center'])
        rv_ratio = self.protocol_parameters['rv_ratio']  # msec
        trajectory_code = [0]  # 0 = expanding, 1 = reversed (shrinking), 2 = randomized
        if self.protocol_parameters['include_reversed_loom']:
            trajectory_code.append(1)
        if self.protocol_parameters['include_randomized_loom']:
            trajectory_code.append(2)

        current_rv_ratio, current_trajectory_code = self.selectParametersFromLists((rv_ratio, trajectory_code),
                                                                                             all_combinations=True,
                                                                                             randomize_order=self.protocol_parameters['randomize_order'])
        current_rv_ratio = current_rv_ratio / 1e3  # msec -> sec
        time_steps, angular_size = getLoomTrajectory(current_rv_ratio, stim_time, start_size, end_size)

        # Get the correct trajectory type
        if current_trajectory_code == 0:
            current_trajectory_type = 'expanding'
            angular_size = angular_size  # initial trajectory

        elif current_trajectory_code == 1:
            current_trajectory_type = 'contracting'
            angular_size = np.flip(angular_size, axis=0)  # reverse in time

        elif current_trajectory_code == 2:
            current_trajectory_type = 'randomized'
            angular_size = np.random.permutation(angular_size)  # randomize in time

        # time-modulated trajectory
        r_traj = Trajectory(list(zip(time_steps, angular_size)), kind='previous').to_dict()

        self.epoch_parameters = {'name': 'MovingSpot',
                                 'radius': r_traj,
                                 'sphere_radius': 1,
                                 'color': self.protocol_parameters['intensity'],
                                 'theta': adj_center[0],
                                 'phi': adj_center[1]}

        self.convenience_parameters = {'current_rv_ratio': current_rv_ratio,
                                       'time_steps': time_steps,
                                       'angular_size': angular_size,
                                       'current_trajectory_type': current_trajectory_type}

    def getParameterDefaults(self):
        self.protocol_parameters = {'intensity': 0.0,
                                    'center': [0, 0],
                                    'start_size': 2.5,
                                    'end_size': 80.0,
                                    'rv_ratio': [5.0, 10.0, 20.0, 40.0, 80.0],
                                    'randomize_order': True,
                                    'include_reversed_loom': False,
                                    'include_randomized_loom': False}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'LoomingPatch',
                               'num_epochs': 75,
                               'pre_time': 0.5,
                               'stim_time': 1.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}
# %%


class MovingRectangle(BaseProtocol):
    def __init__(self, user_name, rig_config):
        super().__init__(user_name, rig_config)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        current_angle = self.selectParametersFromLists(self.protocol_parameters['angle'], randomize_order=self.protocol_parameters['randomize_order'])

        self.epoch_parameters = self.getMovingPatchParameters(angle=current_angle, color=self.protocol_parameters['intensity'])

        self.convenience_parameters = {'current_angle': current_angle}

    def getParameterDefaults(self):
        self.protocol_parameters = {'width': 5.0,
                                    'height': 5.0,
                                    'intensity': 0.0,
                                    'center': [0, 0],
                                    'speed': 80.0,
                                    'angle': [0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0],
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'MovingRectangle',
                               'num_epochs': 40,
                               'pre_time': 0.5,
                               'stim_time': 2.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}
# %%


class MovingSquareMapping(BaseProtocol):
    def __init__(self, user_name, rig_config):
        super().__init__(user_name, rig_config)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        # adjust to screen center
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

        self.epoch_parameters = self.getMovingPatchParameters(height=self.protocol_parameters['square_width'],
                                                              width=self.protocol_parameters['square_width'],
                                                              angle=angle,
                                                              center=center,
                                                              color=self.protocol_parameters['intensity'])

        self.convenience_parameters = {'current_search_axis': current_search_axis,
                                       'current_location': current_location,
                                       'current_angle': angle,
                                       'current_center': center}

    def getParameterDefaults(self):
        self.protocol_parameters = {'square_width': 5.0,
                                    'intensity': 0.0,
                                    'elevation_locations': [-20, -15, -10, -5, 0, 5, 10, 15, 20],
                                    'azimuth_locations': [-20, -15, -10, -5, 0, 5, 10, 15, 20],
                                    'speed': 80.0,
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'MovingSquareMapping',
                               'num_epochs': 100,
                               'pre_time': 0.5,
                               'stim_time': 2.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}

# %%


# TODO: pass params for tree positioning, fly trajectory, and do random seed control for repeated walks
class ForestRandomWalk(BaseProtocol):
    def __init__(self, user_name, rig_config):
        super().__init__(user_name, rig_config)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):

        # random walk trajectory
        tt = np.arange(0, self.run_parameters['stim_time'], 0.01)
        dx = -0.025 + 0.02*np.random.normal(size=len(tt))
        dy = 0.01*np.random.normal(size=len(tt))
        dtheta = 0.25*np.random.normal(size=len(tt))

        fly_x_trajectory = Trajectory(list(zip(tt, np.cumsum(dx)))).to_dict()
        fly_y_trajectory = Trajectory(list(zip(tt, np.cumsum(dy)))).to_dict()
        fly_theta_trajectory = Trajectory(list(zip(tt, np.cumsum(dtheta)))).to_dict()

        tree_x_locations = np.random.uniform(-20, 0, size=int(self.protocol_parameters['n_trees']))
        tree_y_locations = np.random.uniform(-3, 3, size=int(self.protocol_parameters['n_trees']))

        self.epoch_parameters = {'name': 'Composite',
                                 'n_trees': int(self.protocol_parameters['n_trees']),
                                 'tree_height': self.protocol_parameters['tree_height'],
                                 'floor_color': self.protocol_parameters['floor_color'],
                                 'sky_color': self.protocol_parameters['sky_color'],
                                 'tree_color': self.protocol_parameters['tree_color'],
                                 'fly_x_trajectory': fly_x_trajectory,
                                 'fly_y_trajectory': fly_y_trajectory,
                                 'fly_theta_trajectory': fly_theta_trajectory,
                                 'tree_x_locations': tree_x_locations,
                                 'tree_y_locations': tree_y_locations}

    def loadStimuli(self, multicall):
        z_level = -0.2
        passedParameters = self.epoch_parameters.copy()

        multicall.set_fly_trajectory(passedParameters['fly_x_trajectory'],
                                     passedParameters['fly_y_trajectory'],
                                     passedParameters['fly_theta_trajectory'])

        sc = passedParameters['sky_color']
        multicall.load_stim(name='ConstantBackground',
                            color=[sc, sc, sc, 1.0])

        fc = passedParameters['floor_color']
        multicall.load_stim(name='Floor',
                            color=[fc, fc, fc, 1.0],
                            z_level=z_level,
                            hold=True)

        for tree in range(passedParameters['n_trees']):
            multicall.load_stim(name='Tower',
                                color=[0, 0, 0, 1.0],
                                cylinder_height=passedParameters['tree_height'],
                                cylinder_radius=0.1,
                                cylinder_location=[passedParameters['tree_x_locations'][tree], passedParameters['tree_y_locations'][tree], z_level+passedParameters['tree_height']/2],
                                hold=True)

    def getParameterDefaults(self):
        self.protocol_parameters = {'n_trees': 20,
                                    'tree_height': 1.0,
                                    'floor_color': 0.25,
                                    'sky_color': 0.5,
                                    'tree_color': 0.0}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'ForestRandomWalk',
                               'num_epochs': 20,
                               'pre_time': 1.0,
                               'stim_time': 6.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}
# %%


class PanGlomSuite(BaseProtocol):
    def __init__(self, user_name, rig_config):
        super().__init__(user_name, rig_config)
        self.user_name = user_name
        self.rig_config = rig_config
        self.stim_list = ['LoomingSpot', 'DriftingSquareGrating', 'ExpandingMovingSpot',
                          'UniformFlash', 'FlickeringPatch']
        n = [2, 2, 6, 2, 3]  # weight each stim draw by how many trial types it has
        self.stim_p = n / np.sum(n)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        stim_type = str(np.random.choice(self.stim_list, p=self.stim_p))

        self.convenience_parameters = {'component_stim_type': stim_type}
        if stim_type == 'LoomingSpot':
            self.component_class = LoomingSpot(self.user_name, self.rig_config)
            self.component_class.protocol_parameters = {'intensity': 0.0,
                                                        'center': [0, 0],
                                                        'start_size': 2.5,
                                                        'end_size': 80.0,
                                                        'rv_ratio': [10.0, 100.0],
                                                        'randomize_order': True,
                                                        'include_reversed_loom': False,
                                                        'include_randomized_loom': False}

        elif stim_type == 'DriftingSquareGrating':
            self.component_class = DriftingSquareGrating(self.user_name, self.rig_config)
            self.component_class.protocol_parameters = {'period': 20.0,
                                                        'rate': 20.0,
                                                        'contrast': 1.0,
                                                        'mean': 0.5,
                                                        'angle': [0.0, 180.0],
                                                        'center': [0, 0],
                                                        'center_size': 180.0,
                                                        'randomize_order': True}

        elif stim_type == 'ExpandingMovingSpot':
            self.component_class = ExpandingMovingSpot(self.user_name, self.rig_config)
            self.component_class.protocol_parameters = {'diameter': [5.0, 15.0, 50.0],
                                                        'intensity': [0.0, 1.0],
                                                        'center': [0, 0],
                                                        'speed': 80.0,
                                                        'angle': 0.0,
                                                        'randomize_order': True}

        elif stim_type == 'UniformFlash':
            self.component_class = UniformFlash(self.user_name, self.rig_config)
            self.component_class.protocol_parameters = {'height': 120.0,
                                                        'width': 120.0,
                                                        'center': [0, 0],
                                                        'intensity': [1.0, 0.0],
                                                        'randomize_order': True}

        elif stim_type == 'FlickeringPatch':
            self.component_class = FlickeringPatch(self.user_name, self.rig_config)
            self.component_class.protocol_parameters = {'height': 30.0,
                                                        'width': 30.0,
                                                        'center': [0, 0],
                                                        'contrast': 1.0,
                                                        'mean': 0.5,
                                                        'temporal_frequency': [1.0, 4.0, 8.0],
                                                        'randomize_order': True}

        self.component_class.getEpochParameters()
        self.convenience_parameters.update(self.component_class.convenience_parameters)
        self.epoch_parameters = self.component_class.epoch_parameters

    def loadStimuli(self, multicall):
        self.component_class.loadStimuli(multicall)

    def getParameterDefaults(self):
        self.protocol_parameters = {}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'PanGlomSuite',
                               'num_epochs': 75,
                               'pre_time': 0.5,
                               'stim_time': 3.0,
                               'tail_time': 1.5,
                               'idle_color': 0.5}


# %% shared fxns

def getLoomTrajectory(rv_ratio, stim_time, start_size, end_size):
    # rv_ratio in sec
    time_steps = np.arange(0, stim_time-0.001, 0.001)  # time steps of trajectory
    # calculate angular size at each time step for this rv ratio
    angular_size = 2 * np.rad2deg(np.arctan(rv_ratio * (1 / (stim_time - time_steps))))

    # shift curve vertically so it starts at start_size
    min_size = angular_size[0]
    size_adjust = min_size - start_size
    angular_size = angular_size - size_adjust
    # Cap the curve at end_size and have it just hang there
    max_size_ind = np.where(angular_size > end_size)[0][0]
    angular_size[max_size_ind:] = end_size
    # divide by  2 to get spot radius
    angular_size = angular_size / 2

    return time_steps, angular_size
# %%

# TODO update
# class SequentialOrRandomMotion(BaseProtocol):
#     def __init__(self, user_name, rig_config):
#         super().__init__(user_name, rig_config)
#
#         self.getRunParameterDefaults()
#         self.getParameterDefaults()
#
#     def getEpochParameters(self):
#         stimulus_ID = 'MovingPatch'
#
#         #adjust to screen center...
#         adj_az = [x + self.screen_center[0] for x in self.protocol_parameters['azimuth_boundaries']]
#         adj_el = self.screen_center[1] + self.protocol_parameters['elevation']
#
#         stim_time = self.run_parameters['stim_time']
#         no_steps = self.protocol_parameters['no_steps']
#
#         time_steps = np.linspace(0,stim_time,no_steps)
#         x_steps = np.linspace(adj_az[0],adj_az[1],no_steps)
#         y_steps = np.linspace(adj_el,adj_el,no_steps)
#
#         #switch back and forth between sequential and random
#         randomized_order = bool(np.mod(self.num_epochs_completed,2))
#         if randomized_order:
#             x_steps = np.random.permutation(x_steps)
#
#         # time-modulated trajectories
#         x = Trajectory(list(zip(time_steps,x_steps)), kind = 'previous') #note interp kind is previous
#         y = Trajectory(list(zip(time_steps,y_steps)), kind = 'previous')
#         # constant trajectories:
#         w = Trajectory(self.protocol_parameters['square_width'])
#         h = Trajectory(self.protocol_parameters['square_width'])
#         angle = Trajectory(0)
#         color = Trajectory(self.protocol_parameters['color'])
#         trajectory = {'x': x.to_dict(), 'y': y.to_dict(), 'w': w.to_dict(), 'h': h.to_dict(),
#             'angle': angle.to_dict(), 'color': color.to_dict()}
#
#         self.epoch_parameters = {'name':stimulus_ID,
#                             'background':self.run_parameters['idle_color'],
#                             'trajectory':trajectory}
#         self.convenience_parameters = {'randomized_order': randomized_order,
#                                        'x_steps': x_steps}
#
#     def getParameterDefaults(self):
#         self.protocol_parameters = {'square_width':5.0,
#                        'color':0.0,
#                        'elevation': 0.0,
#                        'azimuth_boundaries': [-15.0, 15.0],
#                        'no_steps': 8}
#
#     def getRunParameterDefaults(self):
#         self.run_parameters = {'protocol_ID':'SequentialOrRandomMotion',
#               'num_epochs':20,
#               'pre_time':0.5,
#               'stim_time':0.5,
#               'tail_time':1.0,
#               'idle_color':0.5}

# %%

# TODO update
# class MovingPatchOnDriftingGrating(BaseProtocol):
#     def __init__(self, user_name, rig_config):
#         super().__init__(user_name, rig_config)
#
#         self.getRunParameterDefaults()
#         self.getParameterDefaults()
#
#     def getEpochParameters(self):
#         current_patch_speed, current_grate_rate = self.selectParametersFromLists((self.protocol_parameters['patch_speed'], self.protocol_parameters['grate_rate']),
#                                                                                              all_combinations = True,
#                                                                                              randomize_order = self.protocol_parameters['randomize_order'])
#
#         patch_parameters = self.getMovingPatchParameters(center = self.adjustCenter(self.protocol_parameters['center']),
#                                                          angle = self.protocol_parameters['angle'],
#                                                          speed = current_patch_speed,
#                                                          width = self.protocol_parameters['patch_size'],
#                                                          height = self.protocol_parameters['patch_size'],
#                                                          color = self.protocol_parameters['patch_color'],
#                                                          distance_to_travel = 140)
#         patch_parameters['background'] = None #transparent background
#
#         grate_color, grate_background = self.getColorAndBackgroundFromContrast(self.protocol_parameters['grate_contrast'])
#         grate_parameters = self.getRotatingGratingParameters(angle = self.protocol_parameters['angle'],
#                                                     rate = current_grate_rate,
#                                                     period = self.protocol_parameters['grate_period'],
#                                                     color = grate_color,
#                                                     background = grate_background)
#
#         self.epoch_parameters = (grate_parameters, patch_parameters)
#         self.convenience_parameters = {'current_patch_speed': current_patch_speed,
#                                        'current_grate_rate': current_grate_rate}
#
#     def loadStimuli(self, multicall):
#         grate_parameters = self.epoch_parameters[0].copy()
#         patch_parameters = self.epoch_parameters[1].copy()
#
#         multicall.load_stim(**grate_parameters)
#         multicall.load_stim(**patch_parameters, vary='intensity', hold=True)
#
#     def getParameterDefaults(self):
#         self.protocol_parameters = {'center': [0, 0],
#                                     'patch_size':10.0,
#                                     'patch_color':0.0,
#                        'patch_speed':[20.0, 40.0, 80.0],
#                        'grate_period':10.0,
#                        'grate_rate':[-100.0, -80.0, -40.0, -20.0, -10.0, 0.0,
#                                      10.0, 20.0, 40.0, 80.0, 100.0],
#                        'grate_contrast':0.5,
#                        'angle':0.0,
#                        'randomize_order':True}
#
#     def getRunParameterDefaults(self):
#         self.run_parameters = {'protocol_ID':'MovingPatchOnDriftingGrating',
#               'num_epochs':165,
#               'pre_time':1.0,
#               'stim_time':7.0,
#               'tail_time':1.0,
#               'idle_color':0.5}

# %%

# TODO update
# class SparseNoise(BaseProtocol):
#     def __init__(self, user_name, rig_config):
#         super().__init__(user_name, rig_config)
#
#         self.getRunParameterDefaults()
#         self.getParameterDefaults()
#
#     def getEpochParameters(self):
#         stimulus_ID = 'RandomGrid'
#
#         start_seed = int(np.random.choice(range(int(1e6))))
#
#         distribution_data = {'name':'SparseBinary',
#                                  'args':[],
#                                  'kwargs':{'rand_min':self.protocol_parameters['rand_min'],
#                                            'rand_max':self.protocol_parameters['rand_max'],
#                                            'sparseness':self.protocol_parameters['sparseness']}}
#
#         self.epoch_parameters = {'name': stimulus_ID,
#                             'theta_period': self.protocol_parameters['checker_width'],
#                             'phi_period': self.protocol_parameters['checker_width'],
#                             'start_seed': start_seed,
#                             'update_rate': self.protocol_parameters['update_rate'],
#                             'distribution_data': distribution_data}
#
#         self.convenience_parameters = {'distribution_name': 'SparseBinary',
#                                        'start_seed': start_seed}
#
#     def getParameterDefaults(self):
#         self.protocol_parameters = {'checker_width':5.0,
#                                'update_rate':8.0,
#                                'rand_min': 0.0,
#                                'rand_max':1.0,
#                                'sparseness':0.95}
#
#     def getRunParameterDefaults(self):
#         self.run_parameters = {'protocol_ID':'SparseNoise',
#               'num_epochs':10,
#               'pre_time':1.0,
#               'stim_time':30.0,
#               'tail_time':1.0,
#               'idle_color':0.5}
