#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 10:20:02 2018

@author: mhturner
"""
import numpy as np
import pandas as pd
import os
import flyrpc.multicall
from copy import deepcopy
from scipy.interpolate import interp1d
import inspect

import visprotocol
from visprotocol.protocol import clandinin_protocol
from flystim.trajectory import Trajectory


class BaseProtocol(clandinin_protocol.BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)  # call the parent class init method

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

        x_trajectory = {'name': 'tv_pairs',
                        'tv_pairs': x,
                        'kind': 'linear'}
        y_trajectory = {'name': 'tv_pairs',
                        'tv_pairs': y,
                        'kind': 'linear'}

        patch_parameters = {'name': 'MovingPatch',
                            'width': width,
                            'height': height,
                            'color': color,
                            'theta': x_trajectory,
                            'phi': y_trajectory,
                            'angle': angle}
        return patch_parameters


    def getMovingSpotParameters(self, center=None, angle=None, speed=None, radius=None, color=None, distance_to_travel=None):
        if center is None: center = self.protocol_parameters['center']
        if angle is None: angle = self.protocol_parameters['angle']
        if speed is None: speed = self.protocol_parameters['speed']
        if radius is None: radius = self.protocol_parameters['radius']
        if color is None: color = self.protocol_parameters['color']

        center = self.adjustCenter(center)

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

        x_trajectory = {'name': 'tv_pairs',
                        'tv_pairs': x,
                        'kind': 'linear'}
        y_trajectory = {'name': 'tv_pairs',
                        'tv_pairs': y,
                        'kind': 'linear'}

        spot_parameters = {'name': 'MovingSpot',
                           'radius': radius,
                           'color': color,
                           'theta': x_trajectory,
                           'phi': y_trajectory}
        return spot_parameters

# %%
"""
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # FLY-CENTERED STIMS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""
# TODO update
# class CheckerboardWhiteNoise(BaseProtocol):
#     def __init__(self, cfg):
#         super().__init__(cfg)
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
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        # TODO: center size with aperture (center and center_size): maybe parent class aperture method?
        current_temporal_frequency = self.selectParametersFromLists(self.protocol_parameters['temporal_frequency'], randomize_order=self.protocol_parameters['randomize_order'])

        # Make the contrast trajectory
        contrast_traj = {'name': 'Sinusoid',
                         'temporal_frequency': current_temporal_frequency,
                         'amplitude': self.protocol_parameters['contrast'],
                         'offset': 0}

        self.epoch_parameters = {'name': 'CylindricalGrating',
                                 'period': self.protocol_parameters['spatial_period'],
                                 'color': [1, 1, 1, 1],
                                 'mean': self.protocol_parameters['mean'],
                                 'contrast': contrast_traj,
                                 'angle': self.protocol_parameters['angle'],
                                 'offset': 0.0,
                                 'cylinder_radius': 1.0,
                                 'cylinder_height': 10.0,
                                 'profile': 'square',
                                 'theta': self.screen_center[0]}

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
    def __init__(self, cfg):
        super().__init__(cfg)

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
                                 'profile': 'square',
                                 'theta': self.screen_center[0]}

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


class ExpandingMovingSpot(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        current_diameter, current_intensity, current_speed = self.selectParametersFromLists((self.protocol_parameters['diameter'], self.protocol_parameters['intensity'], self.protocol_parameters['speed']), randomize_order=self.protocol_parameters['randomize_order'])

        self.epoch_parameters = self.getMovingSpotParameters(radius=current_diameter/2,
                                                             color=current_intensity,
                                                             speed=current_speed)

        self.convenience_parameters = {'current_diameter': current_diameter,
                                       'current_intensity': current_intensity,
                                       'current_speed': current_speed}

    def getParameterDefaults(self):
        self.protocol_parameters = {'diameter': [2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0],
                                    'intensity': [0.0, 1.0],
                                    'center': [0, 0],
                                    'speed': [80.0],
                                    'angle': 0.0,
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'ExpandingMovingSpot',
                               'num_epochs': 70,
                               'pre_time': 0.5,
                               'stim_time': 2.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}

# %%


class FlickeringPatch(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        adj_center = self.adjustCenter(self.protocol_parameters['center'])

        current_temporal_frequency = self.selectParametersFromLists(self.protocol_parameters['temporal_frequency'], randomize_order=self.protocol_parameters['randomize_order'])

        # make color trajectory
        color_traj = {'name': 'Sinusoid',
                      'temporal_frequency': current_temporal_frequency,
                      'amplitude': self.protocol_parameters['mean'] * self.protocol_parameters['contrast'],
                      'offset': self.protocol_parameters['mean']}

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


class LoomingSpot(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        stim_time = self.run_parameters['stim_time']
        start_size = self.protocol_parameters['start_size']
        end_size = self.protocol_parameters['end_size']

        # adjust center to screen center
        adj_center = self.adjustCenter(self.protocol_parameters['center'])

        rv_ratio = self.protocol_parameters['rv_ratio']  # msec
        current_rv_ratio = self.selectParametersFromLists(rv_ratio, randomize_order=self.protocol_parameters['randomize_order'])

        current_rv_ratio = current_rv_ratio / 1e3  # msec -> sec
        r_traj = {'name': 'Loom',
                  'rv_ratio': current_rv_ratio,
                  'stim_time': stim_time,
                  'start_size': start_size,
                  'end_size': end_size}

        self.epoch_parameters = {'name': 'MovingSpot',
                                 'radius': r_traj,
                                 'sphere_radius': 1,
                                 'color': self.protocol_parameters['intensity'],
                                 'theta': adj_center[0],
                                 'phi': adj_center[1]}

        self.convenience_parameters = {'current_rv_ratio': current_rv_ratio}

    def getParameterDefaults(self):
        self.protocol_parameters = {'intensity': 0.0,
                                    'center': [0, 0],
                                    'start_size': 2.5,
                                    'end_size': 80.0,
                                    'rv_ratio': [5.0, 10.0, 20.0, 40.0, 80.0],
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'LoomingSpot',
                               'num_epochs': 75,
                               'pre_time': 0.5,
                               'stim_time': 1.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}


# %%

class MovingSpotOnDriftingGrating(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        current_spot_speed, current_grate_rate = self.selectParametersFromLists((self.protocol_parameters['spot_speed'],self.protocol_parameters['grate_rate']),
                                                                                 all_combinations = True,
                                                                                 randomize_order = self.protocol_parameters['randomize_order'])

        patch_parameters = self.getMovingSpotParameters(speed = current_spot_speed,
                                                        radius = self.protocol_parameters['spot_radius'],
                                                        color = self.protocol_parameters['spot_color'],
                                                        distance_to_travel = 180)

        grate_parameters = {'name': 'RotatingGrating',
                            'period': self.protocol_parameters['grate_period'],
                            'rate': current_grate_rate,
                            'color': [1, 1, 1, 1],
                            'mean': self.run_parameters['idle_color'],
                            'contrast': self.protocol_parameters['grate_contrast'],
                            'angle': self.protocol_parameters['angle'],
                            'offset': 0.0,
                            'cylinder_radius': 1.1,
                            'cylinder_height': 20,
                            'profile': 'square',
                            'theta': self.screen_center[0]}

        self.epoch_parameters = (grate_parameters, patch_parameters)
        self.convenience_parameters = {'current_spot_speed': current_spot_speed,
                                       'current_grate_rate': current_grate_rate}

    def loadStimuli(self, client):
        grate_parameters = self.epoch_parameters[0].copy()
        patch_parameters = self.epoch_parameters[1].copy()

        bg = self.run_parameters.get('idle_color')
        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        multicall.load_stim(**grate_parameters, hold=True)
        multicall.load_stim(**patch_parameters, hold=True)
        multicall()

    def getParameterDefaults(self):
        self.protocol_parameters = {'center': [0, 0],
                                    'spot_radius': 10.0,
                                    'spot_color': 0.0,
                                    'spot_speed': [30.0, 60.0, 90.0],
                                    'grate_period': 10.0,
                                    'grate_rate': [-120.0, -90.0, -60.0, -30.0, -15.0, 0.0,
                                                  15.0, 30.0, 60.0, 90.0, 120.0],
                                    'grate_contrast': 0.5,
                                    'angle': 0.0,
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'MovingSpotOnDriftingGrating',
                               'num_epochs':165,
                               'pre_time':1.0,
                               'stim_time':6.0,
                               'tail_time':1.0,
                               'idle_color':0.5}

# %%


class MovingRectangle(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

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
    def __init__(self, cfg):
        super().__init__(cfg)

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

class PeriodicVelocityNoise(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        if self.protocol_parameters['start_seed'] == -1:
            current_seed = np.random.randint(0, 10000)
        else:
            current_seed = self.protocol_parameters['start_seed'] + self.num_epochs_completed

        np.random.seed(int(current_seed))
        n_updates = int(np.ceil(self.run_parameters['stim_time'] * self.protocol_parameters['velocity_update_rate']))
        velocity = np.random.normal(size=n_updates, scale=self.protocol_parameters['velocity_std']) / self.protocol_parameters['velocity_update_rate'] # deg/sec -> deg/update

        time_steps = np.linspace(0, self.run_parameters['stim_time'], n_updates)  # time steps of update trajectory

        position = np.cumsum(velocity) # position at each update time point, according to new velocity value

        theta_traj = {'name': 'tv_pairs',
                      'tv_pairs': list(zip(time_steps, position)),
                      'kind': 'linear'}

        distribution_data = {'name': 'Binary',
                             'args': [],
                             'kwargs': {'rand_min': self.protocol_parameters['intensity'],
                                        'rand_max': self.protocol_parameters['intensity']}}

        self.epoch_parameters = {'name': 'RandomBars',
                                 'distribution_data': distribution_data,
                                 'period': self.protocol_parameters['period'],
                                 'width': self.protocol_parameters['width'],
                                 'vert_extent': self.protocol_parameters['height'],
                                 'background': 0.5,
                                 'color': [1, 1, 1, 1],
                                 'theta': theta_traj,
                                 'cylinder_location': (0, 0, self.protocol_parameters['z_offset'])}

        self.convenience_parameters = {'current_seed': current_seed,
                                       'time_steps': time_steps,
                                       'velocity': velocity,
                                       'position': position}

    def getParameterDefaults(self):
        self.protocol_parameters = {'height': 120.0,
                                    'width': 5.0,
                                    'period': 40.0, # deg spacing between bars
                                    'z_offset': 0, #meters, offset of cylinder
                                    'velocity_std': 80, # deg/sec
                                    'velocity_update_rate': 8, # Hz
                                    'start_seed': -1,
                                    'intensity': 0.0}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'PeriodicVelocityNoise',
                               'num_epochs': 40,
                               'pre_time': 1.0,
                               'stim_time': 30.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}

# %%

class VelocityNoise(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        adj_center = self.adjustCenter(self.protocol_parameters['center'])

        if self.protocol_parameters['start_seed'] == -1:
            current_seed = np.random.randint(0, 10000)
        else:
            current_seed = self.protocol_parameters['start_seed'] + self.num_epochs_completed

        # partition velocity trace up into splits, and follow each split with a reversed version of itself:
        #   ensures that position keeps coming back to center
        np.random.seed(int(current_seed))
        n_updates = int(np.ceil(self.run_parameters['stim_time'] * self.protocol_parameters['velocity_update_rate'])/2)
        out = np.random.normal(size=n_updates, scale=self.protocol_parameters['velocity_std']) / self.protocol_parameters['velocity_update_rate'] # deg/sec -> deg/update
        back = -out

        split_size = 6 #sec
        splits = int(self.run_parameters['stim_time'] / split_size)

        out = np.reshape(out, [splits, -1])
        back = np.reshape(back, [splits, -1])
        v_comb = np.concatenate([out, back], axis=1)
        velocity = np.ravel(v_comb)

        time_steps = np.linspace(0, self.run_parameters['stim_time'], len(velocity))  # time steps of update trajectory

        position = adj_center[0] + np.cumsum(velocity) #position at each update time point, according to new velocity value

        theta_traj = {'name': 'tv_pairs',
                      'tv_pairs': list(zip(time_steps, position)),
                      'kind': 'linear'}

        self.epoch_parameters = {'name': 'MovingPatch',
                                 'width': self.protocol_parameters['width'],
                                 'height': self.protocol_parameters['height'],
                                 'sphere_radius': 1,
                                 'color': self.protocol_parameters['intensity'],
                                 'theta': theta_traj,
                                 'phi': adj_center[1],
                                 'angle': 0}
        self.convenience_parameters = {'current_seed': current_seed,
                                       'time_steps': time_steps,
                                       'velocity': velocity,
                                       'position': position}

    def getParameterDefaults(self):
        self.protocol_parameters = {'height': 10.0,
                                    'width': 5.0,
                                    'center': [0, 0],
                                    'velocity_std': 80, # deg/sec
                                    'velocity_update_rate': 8, # Hz
                                    'start_seed': -1,
                                    'intensity': 0.0}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'VelocityNoise',
                               'num_epochs': 20,
                               'pre_time': 1.0,
                               'stim_time': 36.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}

# %%

class UniformFlash(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

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
class SpotPair(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        current_speed_2 = self.selectParametersFromLists(self.protocol_parameters['speed_2'], randomize_order=self.protocol_parameters['randomize_order'])

        center = self.protocol_parameters['center']
        center_1 = [center[0], center[1] + self.protocol_parameters['y_separation']/2]
        spot_1_parameters =  self.getMovingSpotParameters(color=self.protocol_parameters['intensity'][0],
                                                          radius=self.protocol_parameters['diameter'][0]/2,
                                                          center=center_1,
                                                          speed=self.protocol_parameters['speed_1'],
                                                          angle=0)
        center_2 = [center[0], center[1] - self.protocol_parameters['y_separation']/2]
        spot_2_parameters =  self.getMovingSpotParameters(color=self.protocol_parameters['intensity'][1],
                                                          radius=self.protocol_parameters['diameter'][1]/2,
                                                          center=center_2,
                                                          speed=current_speed_2,
                                                          angle=0)


        self.epoch_parameters = (spot_1_parameters, spot_2_parameters)

        self.convenience_parameters = {'current_speed_2': current_speed_2}

    def loadStimuli(self, client):
        spot_1_parameters = self.epoch_parameters[0].copy()
        spot_2_parameters = self.epoch_parameters[1].copy()

        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        bg = self.run_parameters.get('idle_color')
        multicall.load_stim('ConstantBackground', color=[bg, bg, bg, 1.0])
        multicall.load_stim(**spot_1_parameters, hold=True)
        multicall.load_stim(**spot_2_parameters, hold=True)

        multicall()

    def getParameterDefaults(self):
        self.protocol_parameters = {'diameter': [5.0, 5.0],
                                    'intensity': [0.0, 0.0],
                                    'center': [0, 0],
                                    'y_separation': 7.0,
                                    'speed_1': 80.0,
                                    'speed_2': [-80.0, -40.0, 0.0, 40.0, 80.0],
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'SpotPair',
                               'num_epochs': 40,
                               'pre_time': 0.5,
                               'stim_time': 4.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}


# %%

"""
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # VR WORLD STIMS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""

class RealWalkThroughFakeForest(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        current_trajectory_index = int(self.selectParametersFromLists(self.protocol_parameters['trajectory_range'], randomize_order=True))

        # load walk trajectory
        trajectory_dir = os.path.join(inspect.getfile(visprotocol).split('visprotocol')[0], 'visprotocol', 'resources', self.user_name, 'walking_trajectories')
        file_name = 'walking_traj_20200728.npy'
        snippets = np.load(os.path.join(trajectory_dir, file_name), allow_pickle=True)
        snippet = snippets[current_trajectory_index]
        t = snippet['t']
        x = snippet['x']
        y = snippet['y']
        heading = snippet['a']-90 # angle in degrees. Rotate by -90 to align with heading 0 being down +y axis

        fly_x_trajectory = {'name': 'tv_pairs',
                            'tv_pairs': list(zip(t, x)),
                            'kind': 'linear'}
        fly_y_trajectory = {'name': 'tv_pairs',
                            'tv_pairs': list(zip(t, y)),
                            'kind': 'linear'}
        fly_theta_trajectory = {'name': 'tv_pairs',
                                'tv_pairs': list(zip(t, heading)),
                                'kind': 'linear'}

        z_level = -0.20
        tree_locations = []
        np.random.seed(int(self.protocol_parameters['rand_seed']))
        for tree in range(int(self.protocol_parameters['n_trees'])):
            tree_locations.append([np.random.uniform(-0.5, 0.5), np.random.uniform(-0.5, 0.5), z_level+self.protocol_parameters['tree_height']/2])

        self.epoch_parameters = {'name': 'Composite',
                                 'tree_height': self.protocol_parameters['tree_height'],
                                 'floor_color': self.protocol_parameters['floor_color'],
                                 'sky_color': self.protocol_parameters['sky_color'],
                                 'tree_color': self.protocol_parameters['tree_color'],
                                 'fly_x_trajectory': fly_x_trajectory,
                                 'fly_y_trajectory': fly_y_trajectory,
                                 'fly_theta_trajectory': fly_theta_trajectory,
                                 'tree_locations': tree_locations,
                                 'z_level': z_level}

        self.convenience_parameters = {'current_trajectory_index': current_trajectory_index,
                                        'current_trajectory_library': file_name}

    def loadStimuli(self, client):
        passedParameters = self.epoch_parameters.copy()

        multicall = flyrpc.multicall.MyMultiCall(client.manager)

        multicall.set_fly_trajectory(passedParameters['fly_x_trajectory'],
                                     passedParameters['fly_y_trajectory'],
                                     passedParameters['fly_theta_trajectory'])

        sc = passedParameters['sky_color']
        multicall.load_stim(name='ConstantBackground',
                            color=[sc, sc, sc, 1.0])

        # base_dir = r'C:\Users\mhturner\Documents\GitHub\visprotocol\resources\mht\images\VH_NatImages'
        # fn = 'imk00125.iml'
        # multicall.load_stim(name='HorizonCylinder',
        #                     image_path=os.path.join(base_dir, fn))

        fc = passedParameters['floor_color']
        multicall.load_stim(name='TexturedGround',
                            color=[fc, fc, fc, 1.0],
                            z_level=passedParameters['z_level'],
                            hold=True)

        multicall.load_stim(name='Forest',
                            color = [0, 0, 0, 1],
                            cylinder_height=passedParameters['tree_height'],
                            cylinder_radius=0.01,
                            cylinder_locations=passedParameters['tree_locations'],
                            n_faces=4,
                            hold=True)

        multicall()


    def getParameterDefaults(self):
        self.protocol_parameters = {'n_trees': 40,
                                    'tree_height': 1.0,
                                    'floor_color': 0.40,
                                    'sky_color': 0.5,
                                    'tree_color': 0.0,
                                    'rand_seed': 1,
                                    'trajectory_range': [0, 1, 2, 3, 4]}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'ForestRandomWalk',
                               'num_epochs': 25,
                               'pre_time': 2.0,
                               'stim_time': 20.0,
                               'tail_time': 2.0,
                               'idle_color': 0.5}

# %%
"""
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # MULTI-COMPONENT STIMS # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""

class PanGlomSuite(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.cfg = cfg
        self.stim_list = ['FlickeringPatch', 'DriftingSquareGrating', 'LoomingSpot', 'ExpandingMovingSpot', 'MovingSpotOnDriftingGrating',
                          'MovingRectangle', 'UniformFlash']
        n = [2, 2, 2, 6, 4, 2, 2]  # weight each stim draw by how many trial types it has. Total = 20
        avg_per_stim = int(self.run_parameters['num_epochs'] / np.sum(n))
        all_stims = [[self.stim_list[i]] * n[i] * avg_per_stim for i in range(len(n))]

        self.stim_order = np.random.permutation(np.hstack(all_stims))

        # initialize each component class
        self.initComponentClasses()

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def initComponentClasses(self):
        # pre-populate dict of component classes. Each with its own num_epochs_completed counter etc
        self.component_classes = {}
        for stim_type in self.stim_list:
            if stim_type == 'LoomingSpot':
                new_component_class = LoomingSpot(self.cfg)
                new_component_class.protocol_parameters = {'intensity': 0.0,
                                                            'center': [0, 0],
                                                            'start_size': 2.5,
                                                            'end_size': 80.0,
                                                            'rv_ratio': [20.0, 100.0],
                                                            'randomize_order': True,
                                                            'include_reversed_loom': False,
                                                            'include_randomized_loom': False}

            elif stim_type == 'DriftingSquareGrating':
                new_component_class = DriftingSquareGrating(self.cfg)
                new_component_class.protocol_parameters = {'period': 20.0,
                                                            'rate': 20.0,
                                                            'contrast': 1.0,
                                                            'mean': 0.5,
                                                            'angle': [0.0, 180.0],
                                                            'center': [0, 0],
                                                            'center_size': 180.0,
                                                            'randomize_order': True}

            elif stim_type == 'ExpandingMovingSpot':
                new_component_class = ExpandingMovingSpot(self.cfg)
                new_component_class.protocol_parameters = {'diameter': [5.0, 20.0, 50.0],
                                                            'intensity': [0.0, 1.0],
                                                            'center': [0, 0],
                                                            'speed': 80.0,
                                                            'angle': 0.0,
                                                            'randomize_order': True}

            elif stim_type == 'UniformFlash':
                new_component_class = UniformFlash(self.cfg)
                new_component_class.protocol_parameters = {'height': 240.0,
                                                            'width': 240.0,
                                                            'center': [0, 0],
                                                            'intensity': [1.0, 0.0],
                                                            'randomize_order': True}

            elif stim_type == 'FlickeringPatch':
                new_component_class = FlickeringPatch(self.cfg)
                new_component_class.protocol_parameters = {'height': 30.0,
                                                            'width': 30.0,
                                                            'center': [0, 0],
                                                            'contrast': 1.0,
                                                            'mean': 0.5,
                                                            'temporal_frequency': [1.0, 2.0, 8.0],
                                                            'randomize_order': True}
            elif stim_type == 'MovingSpotOnDriftingGrating':
                new_component_class = MovingSpotOnDriftingGrating(self.cfg)
                new_component_class.protocol_parameters = {'center': [0, 0],
                                                            'spot_radius': 7.5,
                                                            'spot_color': 0.0,
                                                            'spot_speed': 60.0,
                                                            'grate_period': 20.0,
                                                            'grate_rate': [-120.0, -30.0, 30.0, 120.0],
                                                            'grate_contrast': 0.5,
                                                            'angle': 0.0,
                                                            'randomize_order': True}

            elif stim_type == 'MovingRectangle':
                new_component_class = MovingRectangle(self.cfg)
                new_component_class.protocol_parameters = {'width': 20.0,
                                                           'height': 120.0,
                                                            'intensity': 0.0,
                                                            'center': [0, 0],
                                                            'speed': 80.0,
                                                            'angle': [0.0, 180.0],
                                                            'randomize_order': True}

            # Lock component stim timing run params to suite run params
            new_component_class.run_parameters['pre_time'] = self.run_parameters['pre_time']
            new_component_class.run_parameters['stim_time'] = self.run_parameters['stim_time']
            new_component_class.run_parameters['tail_time'] = self.run_parameters['tail_time']
            new_component_class.run_parameters['idle_color'] = self.run_parameters['idle_color']

            self.component_classes[stim_type] = new_component_class

    def getEpochParameters(self):
        stim_type = str(self.stim_order[self.num_epochs_completed]) # note this num_epochs_completed is for the whole suite, not component stim!
        self.convenience_parameters = {'component_stim_type': stim_type}
        self.component_class = self.component_classes[stim_type]

        self.component_class.getEpochParameters()
        self.convenience_parameters.update(self.component_class.convenience_parameters)
        self.epoch_parameters = self.component_class.epoch_parameters

    def loadStimuli(self, client):
        self.component_class.loadStimuli(client)
        self.component_class.advanceEpochCounter() # up the component class epoch counter

    def getParameterDefaults(self):
        self.protocol_parameters = {}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'PanGlomSuite',
                               'num_epochs': 200, #200 = 20 * 10 averages each
                               'pre_time': 1.5,
                               'stim_time': 3.0,
                               'tail_time': 1.5,
                               'idle_color': 0.5}
#
# # %%
# """
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # SHARED FUNCTIONS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# """
#
# def getLoomTrajectory(rv_ratio, stim_time, start_size, end_size):
#     # rv_ratio in sec
#     time_steps = np.arange(0, stim_time-0.001, 0.001)  # time steps of trajectory
#     # calculate angular size at each time step for this rv ratio
#     angular_size = 2 * np.rad2deg(np.arctan(rv_ratio * (1 / (stim_time - time_steps))))
#
#     # shift curve vertically so it starts at start_size
#     min_size = angular_size[0]
#     size_adjust = min_size - start_size
#     angular_size = angular_size - size_adjust
#     # Cap the curve at end_size and have it just hang there
#     max_size_ind = np.where(angular_size > end_size)[0][0]
#     angular_size[max_size_ind:] = end_size
#     # divide by  2 to get spot radius
#     angular_size = angular_size / 2
#
#     return time_steps, angular_size
