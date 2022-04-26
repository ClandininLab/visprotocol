#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 10:20:02 2018

@author: mhturner
"""
import numpy as np
import os
import flyrpc.multicall
import inspect

import visprotocol
from visprotocol.protocol import clandinin_protocol


class BaseProtocol(clandinin_protocol.BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)  # call the parent class init method

# %%


"""
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # FLY-CENTERED STIMS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""


class SphericalCheckerboardWhiteNoise(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        stimulus_ID = 'RandomGridOnSphericalPatch'
        adj_center = self.adjustCenter(self.protocol_parameters['center'])

        start_seed = int(np.random.choice(range(int(1e6))))

        distribution_data = {'name': 'Ternary',
                             'args': [],
                             'kwargs': {'rand_min': self.protocol_parameters['rand_min'],
                                        'rand_max': self.protocol_parameters['rand_max']}}

        self.epoch_parameters = {'name': stimulus_ID,
                                 'patch_width': self.protocol_parameters['patch_size'],
                                 'patch_height': self.protocol_parameters['patch_size'],
                                 'width': self.protocol_parameters['grid_width'],
                                 'height': self.protocol_parameters['grid_height'],
                                 'start_seed': start_seed,
                                 'update_rate': self.protocol_parameters['update_rate'],
                                 'distribution_data': distribution_data,
                                 'theta': adj_center[0],
                                 'phi': adj_center[1]}

        self.convenience_parameters = {'start_seed': start_seed}

    def getParameterDefaults(self):
        self.protocol_parameters = {'patch_size': 5.0,
                                    'update_rate': 20.0,
                                    'rand_min': 0.0,
                                    'rand_max': 1.0,
                                    'grid_width': 60,
                                    'grid_height': 60,
                                    'center': [0.0, 0.0]}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'SphericalCheckerboardWhiteNoise',
                               'num_epochs': 10,
                               'pre_time': 2.0,
                               'stim_time': 30.0,
                               'tail_time': 2.0,
                               'idle_color': 0.5}

# %%


# class ContrastReversingGrating(BaseProtocol):
#     def __init__(self, cfg):
#         super().__init__(cfg)
#
#         self.getRunParameterDefaults()
#         self.getParameterDefaults()
#
#     def getEpochParameters(self):
#         # TODO: center size with aperture (center and center_size): maybe parent class aperture method?
#         current_temporal_frequency = self.selectParametersFromLists(self.protocol_parameters['temporal_frequency'], randomize_order=self.protocol_parameters['randomize_order'])
#
#         # Make the contrast trajectory
#         contrast_traj = {'name': 'Sinusoid',
#                          'temporal_frequency': current_temporal_frequency,
#                          'amplitude': self.protocol_parameters['contrast'],
#                          'offset': 0}
#
#         self.epoch_parameters = {'name': 'CylindricalGrating',
#                                  'period': self.protocol_parameters['spatial_period'],
#                                  'color': [1, 1, 1, 1],
#                                  'mean': self.protocol_parameters['mean'],
#                                  'contrast': contrast_traj,
#                                  'angle': self.protocol_parameters['angle'],
#                                  'offset': 0.0,
#                                  'cylinder_radius': 1.0,
#                                  'cylinder_height': 10.0,
#                                  'profile': 'square',
#                                  'theta': self.screen_center[0]}
#
#         self.convenience_parameters = {'current_temporal_frequency': current_temporal_frequency}
#
#         self.meta_parameters = {'center_size': self.protocol_parameters['center_size'],
#                                 'center': self.adjustCenter(self.protocol_parameters['center'])}
#
#     def getParameterDefaults(self):
#         self.protocol_parameters = {'spatial_period': 20.0,
#                                     'contrast': 1.0,
#                                     'mean': 0.5,
#                                     'temporal_frequency': [0.5, 1.0, 2.0, 4.0, 8.0, 16.0],
#                                     'center': [0, 0],
#                                     'center_size': 40.0,
#                                     'angle': 0.0,
#                                     'randomize_order': True}
#
#     def getRunParameterDefaults(self):
#         self.run_parameters = {'protocol_ID': 'ContrastReversingGrating',
#                                'num_epochs': 40,
#                                'pre_time': 1.0,
#                                'stim_time': 4.0,
#                                'tail_time': 1.0,
#                                'idle_color': 0.5}

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
        self.protocol_parameters = {'diameter': [5, 10, 15, 20, 25, 30],
                                    'intensity': [0.0, 1.0],
                                    'center': [0, 0],
                                    'speed': [80.0],
                                    'angle': 0.0,
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'ExpandingMovingSpot',
                               'num_epochs': 70,
                               'pre_time': 0.5,
                               'stim_time': 3.0,
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
        current_rv_ratio, current_intensity = self.selectParametersFromLists((rv_ratio, self.protocol_parameters['intensity']),
                                                                             randomize_order=self.protocol_parameters['randomize_order'])

        current_rv_ratio = current_rv_ratio / 1e3  # msec -> sec
        r_traj = {'name': 'Loom',
                  'rv_ratio': current_rv_ratio,
                  'stim_time': stim_time,
                  'start_size': start_size,
                  'end_size': end_size}

        self.epoch_parameters = {'name': 'MovingSpot',
                                 'radius': r_traj,
                                 'sphere_radius': 1,
                                 'color': current_intensity,
                                 'theta': adj_center[0],
                                 'phi': adj_center[1]}

        self.convenience_parameters = {'current_rv_ratio': current_rv_ratio, 'current_intensity': current_intensity}

    def getParameterDefaults(self):
        self.protocol_parameters = {'intensity': [0.0, 1.0],
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
        current_spot_speed, current_grate_rate = self.selectParametersFromLists((self.protocol_parameters['spot_speed'], self.protocol_parameters['grate_rate']),
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
        self.run_parameters = {'protocol_ID': 'MovingSpotOnDriftingGrating',
                               'num_epochs': 165,
                               'pre_time': 1.0,
                               'stim_time': 6.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}

# %%


class SurroundGratingTuning(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        current_spot_speed, current_grate_rate, current_grate_period = self.selectParametersFromLists((self.protocol_parameters['spot_speed'], self.protocol_parameters['grate_rate'], self.protocol_parameters['grate_period']),
                                                                                                      all_combinations=True,
                                                                                                      randomize_order=self.protocol_parameters['randomize_order'])

        patch_parameters = self.getMovingSpotParameters(speed=current_spot_speed,
                                                        radius=self.protocol_parameters['spot_radius'],
                                                        color=self.protocol_parameters['spot_color'],
                                                        distance_to_travel=220)

        grate_parameters = {'name': 'RotatingGrating',
                            'period': current_grate_period,
                            'rate': current_grate_rate,
                            'color': [1, 1, 1, 1],
                            'mean': self.run_parameters['idle_color'],
                            'contrast': self.protocol_parameters['grate_contrast'],
                            'angle': self.protocol_parameters['angle'],
                            'offset': 0.0,
                            'cylinder_radius': 1.1,
                            'cylinder_height': 20,
                            'profile': 'sine',
                            'theta': self.screen_center[0]}

        self.epoch_parameters = (grate_parameters, patch_parameters)
        self.convenience_parameters = {'current_spot_speed': current_spot_speed,
                                       'current_grate_rate': current_grate_rate,
                                       'current_grate_period': current_grate_period}

    def loadStimuli(self, client):
        grate_parameters = self.epoch_parameters[0].copy()
        patch_parameters = self.epoch_parameters[1].copy()

        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        multicall.load_stim(**grate_parameters, hold=True)
        multicall.load_stim(**patch_parameters, hold=True)
        multicall()

    def getParameterDefaults(self):
        self.protocol_parameters = {'center': [0, 0],
                                    'spot_radius': 7.5,
                                    'spot_color': 0.0,
                                    'spot_speed': [-100, 100],
                                    'grate_period': [5, 10, 20, 40],
                                    'grate_rate': [20, 40, 80, 160, 320],
                                    'grate_contrast': 0.5,
                                    'angle': 0.0,
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'SurroundGratingTuning',
                               'num_epochs': 200,  # 2 x 4 x 5 = 40; 5 averages each
                               'pre_time': 1.0,
                               'stim_time': 3.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}


# %%

class MovingRectangle(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        current_intensity, current_angle = self.selectParametersFromLists((self.protocol_parameters['intensity'], self.protocol_parameters['angle']), randomize_order=self.protocol_parameters['randomize_order'])

        self.epoch_parameters = self.getMovingPatchParameters(angle=current_angle, color=current_intensity)

        self.convenience_parameters = {'current_angle': current_angle,
                                       'current_intensity': current_intensity}

    def getParameterDefaults(self):
        self.protocol_parameters = {'width': 5.0,
                                    'height': 50.0,
                                    'intensity': [0.0, 1.0],
                                    'center': [0, 0],
                                    'speed': 80.0,
                                    'angle': [0.0, 180.0],
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'MovingRectangle',
                               'num_epochs': 40,
                               'pre_time': 0.5,
                               'stim_time': 3.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}
# %%


# class MovingSquareMapping(BaseProtocol):
#     def __init__(self, cfg):
#         super().__init__(cfg)
#
#         self.getRunParameterDefaults()
#         self.getParameterDefaults()
#
#     def getEpochParameters(self):
#         # adjust to screen center
#         az_loc = [x + self.screen_center[0] for x in self.protocol_parameters['azimuth_locations']]
#         el_loc = [x + self.screen_center[1] for x in self.protocol_parameters['elevation_locations']]
#
#         if type(az_loc) is not list:
#             az_loc = [az_loc]
#         if type(el_loc) is not list:
#             el_loc = [el_loc]
#
#         center_el = np.median(el_loc)
#         center_az = np.median(az_loc)
#
#         location_list = np.concatenate((az_loc, el_loc))
#         movement_axis_list = np.concatenate((np.ones(len(az_loc)), 2*np.ones(len(el_loc))))
#
#         current_search_axis_code, current_location = self.selectParametersFromLists((movement_axis_list, location_list),
#                                                                                               all_combinations = False,
#                                                                                               randomize_order = self.protocol_parameters['randomize_order'])
#
#         if current_search_axis_code == 1:
#             current_search_axis = 'azimuth'
#             angle = 90
#             center = [current_location, center_el]
#         elif current_search_axis_code == 2:
#             current_search_axis = 'elevation'
#             angle = 0
#             center = [center_az, current_location]
#
#         self.epoch_parameters = self.getMovingPatchParameters(height=self.protocol_parameters['square_width'],
#                                                               width=self.protocol_parameters['square_width'],
#                                                               angle=angle,
#                                                               center=center,
#                                                               color=self.protocol_parameters['intensity'])
#
#         self.convenience_parameters = {'current_search_axis': current_search_axis,
#                                        'current_location': current_location,
#                                        'current_angle': angle,
#                                        'current_center': center}
#
#     def getParameterDefaults(self):
#         self.protocol_parameters = {'square_width': 5.0,
#                                     'intensity': 0.0,
#                                     'elevation_locations': [-20, -15, -10, -5, 0, 5, 10, 15, 20],
#                                     'azimuth_locations': [-20, -15, -10, -5, 0, 5, 10, 15, 20],
#                                     'speed': 80.0,
#                                     'randomize_order': True}
#
#     def getRunParameterDefaults(self):
#         self.run_parameters = {'protocol_ID': 'MovingSquareMapping',
#                                'num_epochs': 100,
#                                'pre_time': 0.5,
#                                'stim_time': 2.0,
#                                'tail_time': 1.0,
#                                'idle_color': 0.5}


# %%

# class PeriodicVelocityNoise(BaseProtocol):
#     def __init__(self, cfg):
#         super().__init__(cfg)
#
#         self.getRunParameterDefaults()
#         self.getParameterDefaults()
#
#     def getEpochParameters(self):
#         if self.protocol_parameters['start_seed'] == -1:
#             current_seed = np.random.randint(0, 10000)
#         else:
#             current_seed = self.protocol_parameters['start_seed'] + self.num_epochs_completed
#
#         np.random.seed(int(current_seed))
#         n_updates = int(np.ceil(self.run_parameters['stim_time'] * self.protocol_parameters['velocity_update_rate']))
#         velocity = np.random.normal(size=n_updates, scale=self.protocol_parameters['velocity_std']) / self.protocol_parameters['velocity_update_rate'] # deg/sec -> deg/update
#
#         time_steps = np.linspace(0, self.run_parameters['stim_time'], n_updates)  # time steps of update trajectory
#
#         position = np.cumsum(velocity) # position at each update time point, according to new velocity value
#
#         theta_traj = {'name': 'tv_pairs',
#                       'tv_pairs': list(zip(time_steps, position)),
#                       'kind': 'linear'}
#
#         distribution_data = {'name': 'Binary',
#                              'args': [],
#                              'kwargs': {'rand_min': self.protocol_parameters['intensity'],
#                                         'rand_max': self.protocol_parameters['intensity']}}
#
#         self.epoch_parameters = {'name': 'RandomBars',
#                                  'distribution_data': distribution_data,
#                                  'period': self.protocol_parameters['period'],
#                                  'width': self.protocol_parameters['width'],
#                                  'vert_extent': self.protocol_parameters['height'],
#                                  'background': 0.5,
#                                  'color': [1, 1, 1, 1],
#                                  'theta': theta_traj,
#                                  'cylinder_location': (0, 0, self.protocol_parameters['z_offset'])}
#
#         self.convenience_parameters = {'current_seed': current_seed,
#                                        'time_steps': time_steps,
#                                        'velocity': velocity,
#                                        'position': position}
#
#     def getParameterDefaults(self):
#         self.protocol_parameters = {'height': 120.0,
#                                     'width': 5.0,
#                                     'period': 40.0, # deg spacing between bars
#                                     'z_offset': 0.0, #meters, offset of cylinder
#                                     'velocity_std': 80.0, # deg/sec
#                                     'velocity_update_rate': 8, # Hz
#                                     'start_seed': -1,
#                                     'intensity': 0.0}
#
#     def getRunParameterDefaults(self):
#         self.run_parameters = {'protocol_ID': 'PeriodicVelocityNoise',
#                                'num_epochs': 40,
#                                'pre_time': 1.0,
#                                'stim_time': 30.0,
#                                'tail_time': 1.0,
#                                'idle_color': 0.5}

# %%

# class VelocityNoise(BaseProtocol):
#     def __init__(self, cfg):
#         super().__init__(cfg)
#
#         self.getRunParameterDefaults()
#         self.getParameterDefaults()
#
#     def getEpochParameters(self):
#         adj_center = self.adjustCenter(self.protocol_parameters['center'])
#
#         if self.protocol_parameters['start_seed'] == -1:
#             current_seed = np.random.randint(0, 10000)
#         else:
#             current_seed = self.protocol_parameters['start_seed'] + self.num_epochs_completed
#
#         # partition velocity trace up into splits, and follow each split with a reversed version of itself:
#         #   ensures that position keeps coming back to center
#         np.random.seed(int(current_seed))
#         n_updates = int(np.ceil(self.run_parameters['stim_time'] * self.protocol_parameters['velocity_update_rate'])/2)
#         out = np.random.normal(size=n_updates, scale=self.protocol_parameters['velocity_std']) / self.protocol_parameters['velocity_update_rate'] # deg/sec -> deg/update
#         back = -out
#
#         split_size = 6 #sec
#         splits = int(self.run_parameters['stim_time'] / split_size)
#
#         out = np.reshape(out, [splits, -1])
#         back = np.reshape(back, [splits, -1])
#         v_comb = np.concatenate([out, back], axis=1)
#         velocity = np.ravel(v_comb)
#
#         time_steps = np.linspace(0, self.run_parameters['stim_time'], len(velocity))  # time steps of update trajectory
#
#         position = adj_center[0] + np.cumsum(velocity) #position at each update time point, according to new velocity value
#
#         theta_traj = {'name': 'tv_pairs',
#                       'tv_pairs': list(zip(time_steps, position)),
#                       'kind': 'linear'}
#
#         self.epoch_parameters = {'name': 'MovingPatch',
#                                  'width': self.protocol_parameters['width'],
#                                  'height': self.protocol_parameters['height'],
#                                  'sphere_radius': 1,
#                                  'color': self.protocol_parameters['intensity'],
#                                  'theta': theta_traj,
#                                  'phi': adj_center[1],
#                                  'angle': 0}
#         self.convenience_parameters = {'current_seed': current_seed,
#                                        'time_steps': time_steps,
#                                        'velocity': velocity,
#                                        'position': position}
#
#     def getParameterDefaults(self):
#         self.protocol_parameters = {'height': 10.0,
#                                     'width': 5.0,
#                                     'center': [0, 0],
#                                     'velocity_std': 80, # deg/sec
#                                     'velocity_update_rate': 8, # Hz
#                                     'start_seed': -1,
#                                     'intensity': 0.0}
#
#     def getRunParameterDefaults(self):
#         self.run_parameters = {'protocol_ID': 'VelocityNoise',
#                                'num_epochs': 20,
#                                'pre_time': 1.0,
#                                'stim_time': 36.0,
#                                'tail_time': 1.0,
#                                'idle_color': 0.5}

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
# class SpotPair(BaseProtocol):
#     def __init__(self, cfg):
#         super().__init__(cfg)
#
#         self.getRunParameterDefaults()
#         self.getParameterDefaults()
#
#     def getEpochParameters(self):
#         current_speed_2 = self.selectParametersFromLists(self.protocol_parameters['speed_2'], randomize_order=self.protocol_parameters['randomize_order'])
#
#         center = self.protocol_parameters['center']
#         center_1 = [center[0], center[1] + self.protocol_parameters['y_separation']/2]
#         spot_1_parameters =  self.getMovingSpotParameters(color=self.protocol_parameters['intensity'][0],
#                                                           radius=self.protocol_parameters['diameter'][0]/2,
#                                                           center=center_1,
#                                                           speed=self.protocol_parameters['speed_1'],
#                                                           angle=0)
#         center_2 = [center[0], center[1] - self.protocol_parameters['y_separation']/2]
#         spot_2_parameters =  self.getMovingSpotParameters(color=self.protocol_parameters['intensity'][1],
#                                                           radius=self.protocol_parameters['diameter'][1]/2,
#                                                           center=center_2,
#                                                           speed=current_speed_2,
#                                                           angle=0)
#
#
#         self.epoch_parameters = (spot_1_parameters, spot_2_parameters)
#
#         self.convenience_parameters = {'current_speed_2': current_speed_2}
#
#     def loadStimuli(self, client):
#         spot_1_parameters = self.epoch_parameters[0].copy()
#         spot_2_parameters = self.epoch_parameters[1].copy()
#
#         multicall = flyrpc.multicall.MyMultiCall(client.manager)
#         bg = self.run_parameters.get('idle_color')
#         multicall.load_stim('ConstantBackground', color=[bg, bg, bg, 1.0])
#         multicall.load_stim(**spot_1_parameters, hold=True)
#         multicall.load_stim(**spot_2_parameters, hold=True)
#
#         multicall()
#
#     def getParameterDefaults(self):
#         self.protocol_parameters = {'diameter': [5.0, 5.0],
#                                     'intensity': [0.0, 0.0],
#                                     'center': [0, 0],
#                                     'y_separation': 7.0,
#                                     'speed_1': 80.0,
#                                     'speed_2': [-80.0, -40.0, 0.0, 40.0, 80.0],
#                                     'randomize_order': True}
#
#     def getRunParameterDefaults(self):
#         self.run_parameters = {'protocol_ID': 'SpotPair',
#                                'num_epochs': 40,
#                                'pre_time': 0.5,
#                                'stim_time': 4.0,
#                                'tail_time': 1.0,
#                                'idle_color': 0.5}


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
        current_params = self.selectParametersFromLists((self.protocol_parameters['trajectory_range'],
                                                         self.protocol_parameters['n_trees'],
                                                         self.protocol_parameters['include_ground']
                                                         ), randomize_order=True)

        current_trajectory_index, current_n_trees, current_include_ground = current_params

        # load walk trajectory
        trajectory_dir = os.path.join(inspect.getfile(visprotocol).split('visprotocol')[0], 'visprotocol', 'resources', self.user_name, 'walking_trajectories')
        file_name = 'walking_traj_20200728.npy'
        snippets = np.load(os.path.join(trajectory_dir, file_name), allow_pickle=True)
        snippet = snippets[int(current_trajectory_index)]
        t = snippet['t']
        x = snippet['x']
        y = snippet['y']
        heading = snippet['a']-90  # angle in degrees. Rotate by -90 to align with heading 0 being down +y axis

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
        for tree in range(int(current_n_trees)):
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
                                       'current_trajectory_library': file_name,
                                       'current_n_trees': current_n_trees,
                                       'current_include_ground': current_include_ground}

    def loadStimuli(self, client):
        passedParameters = self.epoch_parameters.copy()

        multicall = flyrpc.multicall.MyMultiCall(client.manager)

        multicall.set_fly_trajectory(passedParameters['fly_x_trajectory'],
                                     passedParameters['fly_y_trajectory'],
                                     passedParameters['fly_theta_trajectory'])

        sc = passedParameters['sky_color']
        multicall.load_stim(name='ConstantBackground',
                            color=[sc, sc, sc, 1.0])

        if self.convenience_parameters['current_include_ground'] == 1:
            fc = passedParameters['floor_color']
            multicall.load_stim(name='TexturedGround',
                                color=[fc, fc, fc, 1.0],
                                z_level=passedParameters['z_level'],
                                hold=True)

        multicall.load_stim(name='Forest',
                            color=passedParameters['tree_color'],
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
                                    'trajectory_range': [0, 1, 2],
                                    'include_ground': [0, 1]}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'RealWalkThroughFakeForest',
                               'num_epochs': 30,
                               'pre_time': 2.0,
                               'stim_time': 20.0,
                               'tail_time': 2.0,
                               'idle_color': 0.5}
# %%


class NaturalImageSuppression(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        current_params = self.selectParametersFromLists((
                                                         self.protocol_parameters['image_index'],
                                                         self.protocol_parameters['filter_flag'],
                                                         self.protocol_parameters['image_speed'],
                                                         ), randomize_order=True)

        current_image_index, current_filter_flag, current_image_speed = current_params
        image_names = ['imk00152.tif', 'imk00377.tif', 'imk00405.tif', 'imk00459.tif',
                       'imk00657.tif', 'imk01151.tif', 'imk01154.tif', 'imk01192.tif',
                       'imk01769.tif', 'imk01829.tif', 'imk02265.tif', 'imk02281.tif',
                       'imk02733.tif', 'imk02999.tif', 'imk03093.tif', 'imk03347.tif',
                       'imk03447.tif', 'imk03584.tif', 'imk03758.tif', 'imk03760.tif']

        current_image = np.array(image_names)[int(current_image_index)]

        if current_filter_flag == 0:  # RAW image
            current_image = current_image
            filter_name = None
            filter_kwargs = None
        elif current_filter_flag == 1:  # WHITENED. pre-computed whitened image. Whitening takes a few seconds.
            current_image = 'whitened_' + current_image
            filter_name = None
            filter_kwargs = None
        elif current_filter_flag == 2:  # DIFFERENCE OF GAUSSIANS
            # Sigmas are in degrees, need to be in image pixels
            # scale = 1536 / 360 pixels per degree
            current_image = current_image
            pixels_per_degree = 1536 / 360
            filter_name = 'difference_of_gaussians'
            filter_kwargs = {'low_sigma': 1 * pixels_per_degree,  # degrees -> pixels
                             'high_sigma': 4 * pixels_per_degree}  # degrees -> pixels
        elif current_filter_flag == 3:  # HIGHPASS
            current_image = current_image
            pixels_per_degree = 1536 / 360
            filter_name = 'butterworth'
            filter_kwargs = {'cutoff_frequency_ratio': 0.1,
                             'order': 2,
                             'high_pass': True}
        elif current_filter_flag == 4:  # LOWPASS
            current_image = current_image
            pixels_per_degree = 1536 / 360
            filter_name = 'butterworth'
            filter_kwargs = {'cutoff_frequency_ratio': 0.1,
                             'order': 2,
                             'high_pass': False}

        # Stim params for horizon cylinder
        centerX = self.adjustCenter([0, 0])[0]
        distance_to_travel = current_image_speed * self.run_parameters['stim_time']
        startX = (0, centerX - distance_to_travel/2)
        endX = (self.run_parameters['stim_time'], centerX + distance_to_travel/2)
        x = [startX, endX]

        rotation_trajectory = {'name': 'tv_pairs',
                               'tv_pairs': x,
                               'kind': 'linear'}

        # VH images are trimmed to [512, 1536] pixels (3:1 aspect ratio)
        #   For w & h to have equal pixels_per_degree, cylinder needs to have radius = 1, height = 3.464...
        #   Entire height subtends 120 deg (1/3 of the width)
        #   tan(60) = (h/2) / r
        #   h = 2 * r * tan(60) = 3.464
        image_parameters = {'name': 'HorizonCylinder',
                            'cylinder_radius': 1,
                            'cylinder_height': 3.464,
                            'image_name': current_image,
                            'filter_name': filter_name,
                            'filter_kwargs': filter_kwargs,
                            'theta': rotation_trajectory}

        # Stim params for probe (spot) stimulus
        spot_parameters = self.getMovingSpotParameters(radius=self.protocol_parameters['spot_radius'],
                                                       color=self.protocol_parameters['spot_color'],
                                                       speed=self.protocol_parameters['spot_speed'],
                                                       angle=0)
        spot_parameters['sphere_radius'] = 0.5  # Render inside the image cylinder

        self.epoch_parameters = (image_parameters, spot_parameters)
        self.convenience_parameters = {'current_image': current_image,
                                       'current_filter_name': filter_name,
                                       'current_filter_kwargs': filter_kwargs,
                                       'current_filter_flag': current_filter_flag,
                                       'current_image_speed': current_image_speed}

    def loadStimuli(self, client):
        bg = self.run_parameters.get('idle_color')
        image_parameters = self.epoch_parameters[0].copy()
        spot_parameters = self.epoch_parameters[1].copy()

        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        multicall.load_stim('ConstantBackground', color=[bg, bg, bg, 1.0])
        multicall.load_stim(**image_parameters, hold=True)
        multicall.load_stim(**spot_parameters, hold=True)
        multicall()

    def getParameterDefaults(self):
        self.protocol_parameters = {'center': [0, 0],
                                    'spot_radius': 7.5,
                                    'spot_color': 0.0,
                                    'spot_speed': 100,  # Deg./sec
                                    'image_speed': [0, 40, 160, 320],  # Deg./sec
                                    'image_index': [0, 5, 15],
                                    'filter_flag': [0, 1, 3, 4]}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'NaturalImageSuppression',
                               'num_epochs': 240,  # 4 x 3 x 4 = 48; 5 trials each = 240
                               'pre_time': 1.0,
                               'stim_time': 3.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}


# %%
class ApproachTuning(BaseProtocol):
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

        n_updates = int(np.ceil(self.run_parameters['stim_time'] * self.protocol_parameters['velocity_update_rate'])/2)
        velocity = np.random.normal(size=n_updates, scale=self.protocol_parameters['velocity_std']) / self.protocol_parameters['velocity_update_rate'] # m/sec -> m/update

        time_steps = np.linspace(0, self.run_parameters['stim_time'], len(velocity))  # time steps of update trajectory
        # distance away from fly
        distance = np.cumsum(velocity)  # position at each update time point, according to new velocity value. Centered around 0

        position_x = np.sin(np.deg2rad(self.protocol_parameters['tower_azimuth'])) * distance
        position_y = np.cos(np.deg2rad(self.protocol_parameters['tower_azimuth'])) * distance

        fly_x_trajectory = {'name': 'tv_pairs',
                            'tv_pairs': list(zip(time_steps, position_x)),
                            'kind': 'linear'}

        fly_y_trajectory = {'name': 'tv_pairs',
                            'tv_pairs': list(zip(time_steps, position_y)),
                            'kind': 'linear'}

        # tower location: along azimuth line
        tower_location = [np.sin(np.deg2rad(self.protocol_parameters['tower_azimuth'])) * self.protocol_parameters['tower_distance'],
                          np.cos(np.deg2rad(self.protocol_parameters['tower_azimuth'])) * self.protocol_parameters['tower_distance'],
                          0]

        self.epoch_parameters = {'name': 'Composite',
                                 'tower_height': self.protocol_parameters['tower_height'],
                                 'tower_diameter': self.protocol_parameters['tower_diameter'],
                                 'tower_color': self.protocol_parameters['tower_color'],
                                 'tower_location': tower_location,
                                 'fly_x_trajectory': fly_x_trajectory,
                                 'fly_y_trajectory': fly_y_trajectory}

        self.convenience_parameters = {'current_seed': current_seed}

    def loadStimuli(self, client):
        passedParameters = self.epoch_parameters.copy()

        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        multicall.set_fly_trajectory(passedParameters['fly_x_trajectory'], passedParameters['fly_y_trajectory'], 0)

        bg = self.run_parameters.get('idle_color')
        multicall.load_stim(name='ConstantBackground',
                            color=[bg, bg, bg, 1.0],
                            hold=True)

        multicall.load_stim(name='Tower',
                            color=passedParameters['tower_color'],
                            cylinder_height=passedParameters['tower_height'],
                            cylinder_radius=passedParameters['tower_diameter']/2,
                            cylinder_location=passedParameters['tower_location'],
                            n_faces=4,
                            hold=True)

        multicall()

    def getParameterDefaults(self):
        self.protocol_parameters = {'start_seed': -1,
                                    'velocity_update_rate': 10,
                                    'velocity_std': 0.03,
                                    'tower_color': 0,
                                    'tower_height': 1.0,
                                    'tower_diameter': 0.01,
                                    'tower_distance': 0.05,
                                    'tower_azimuth': 45}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'ApproachTuning',
                               'num_epochs': 25,
                               'pre_time': 2.0,
                               'stim_time': 20.0,
                               'tail_time': 2.0,
                               'idle_color': 0.5}


# %%

class TowerDistanceWalk(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        current_forward_velocity, current_tower_diameter, current_tower_xoffset = self.selectParametersFromLists((self.protocol_parameters['forward_velocity'],
                                                                                                                  self.protocol_parameters['tower_diameter'],
                                                                                                                  self.protocol_parameters['tower_xoffset']), randomize_order=True)

        # make walk trajectory
        t = np.arange(0, self.run_parameters.get('stim_time'), 0.01) # sec

        velocity_x = 0.0 # meters per sec
        velocity_y = current_forward_velocity # meters per sec

        x = velocity_x * t
        y = velocity_y * t
        heading = 0 * t

        fly_x_trajectory = {'name': 'tv_pairs',
                            'tv_pairs': list(zip(t, x)),
                            'kind': 'linear'}
        fly_y_trajectory = {'name': 'tv_pairs',
                            'tv_pairs': list(zip(t, y)),
                            'kind': 'linear'}
        fly_theta_trajectory = {'name': 'tv_pairs',
                                'tv_pairs': list(zip(t, heading)),
                                'kind': 'linear'}

        z_level = -0.05
        tower_locations = []
        for tree in range(int(self.protocol_parameters['n_towers'])):
            tower_locations.append([current_tower_xoffset, # x
                                   (tree+1) * self.protocol_parameters['tower_spacing'], # y
                                   z_level+self.protocol_parameters['tower_height']/2]) # z

        self.epoch_parameters = {'name': 'Composite',
                                 'tower_height': self.protocol_parameters['tower_height'],
                                 'tower_diameter': current_tower_diameter,
                                 'floor_color': self.protocol_parameters['floor_color'],
                                 'sky_color': self.protocol_parameters['sky_color'],
                                 'tower_color': self.protocol_parameters['tower_color'],
                                 'fly_x_trajectory': fly_x_trajectory,
                                 'fly_y_trajectory': fly_y_trajectory,
                                 'fly_theta_trajectory': fly_theta_trajectory,
                                 'tower_locations': tower_locations,
                                 'z_level': z_level}

        self.convenience_parameters = {'current_forward_velocity': current_forward_velocity,
                                       'current_tower_diameter': current_tower_diameter,
                                       'current_tower_xoffset': current_tower_xoffset}


    def loadStimuli(self, client):
        passedParameters = self.epoch_parameters.copy()

        multicall = flyrpc.multicall.MyMultiCall(client.manager)

        multicall.set_fly_trajectory(passedParameters['fly_x_trajectory'],
                                     passedParameters['fly_y_trajectory'],
                                     passedParameters['fly_theta_trajectory'])

        sc = passedParameters['sky_color']
        multicall.load_stim(name='ConstantBackground',
                            color=[sc, sc, sc, 1.0])

        fc = passedParameters['floor_color']
        multicall.load_stim(name='TexturedGround',
                            color=[fc, fc, fc, 1.0],
                            z_level=passedParameters['z_level'],
                            hold=True)

        multicall.load_stim(name='Forest',
                            color=passedParameters['tower_color'],
                            cylinder_height=passedParameters['tower_height'],
                            cylinder_radius=passedParameters['tower_diameter']/2,
                            cylinder_locations=passedParameters['tower_locations'],
                            n_faces=8,
                            hold=True)

        multicall()

    def getParameterDefaults(self):
        self.protocol_parameters = {'forward_velocity': [0.02],
                                    'n_towers': 5,
                                    'tower_height': 1.0,
                                    'tower_diameter': [0.01, 0.02, 0.03],
                                    'tower_spacing': 0.08,
                                    'tower_xoffset': [-0.01, -0.02, -0.04, -0.06],
                                    'tower_color': 0.0,
                                    'floor_color': 0.40,
                                    'sky_color': 0.75}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'TowerDistanceWalk',
                               'num_epochs': 40,
                               'pre_time': 2.0,
                               'stim_time': 20.0,
                               'tail_time': 2.0,
                               'idle_color': 0.5}

# %%


class MovingSpotOnVR(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        adj_center = self.adjustCenter(self.protocol_parameters['center'])

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

        vr_parameters = {'name': 'Composite',
                         'tree_height': self.protocol_parameters['tree_height'],
                         'floor_color': self.protocol_parameters['floor_color'],
                         'sky_color': self.protocol_parameters['sky_color'],
                         'tree_color': self.protocol_parameters['tree_color'],
                         'fly_x_trajectory': fly_x_trajectory,
                         'fly_y_trajectory': fly_y_trajectory,
                         'fly_theta_trajectory': fly_theta_trajectory,
                         'tree_locations': tree_locations,
                         'z_level': z_level}

        position_traj = {'name': 'Sinusoid',
                         'temporal_frequency': self.protocol_parameters['spot_traj_frequency'],
                         'amplitude': self.protocol_parameters['spot_traj_amplitude'],
                         'offset': adj_center[0]}

        patch_parameters = {'name': 'MovingSpot',
                            'radius': self.protocol_parameters['spot_radius'],
                            'color': self.protocol_parameters['spot_color'],
                            'theta': position_traj,
                            'phi': adj_center[1],
                            'sphere_radius': 0.05}

        self.epoch_parameters = (vr_parameters, patch_parameters)
        self.convenience_parameters = {'current_trajectory_index': current_trajectory_index,
                                       'current_trajectory_library': file_name}

    def loadStimuli(self, client):
        vr_parameters = self.epoch_parameters[0].copy()
        patch_parameters = self.epoch_parameters[1].copy()

        multicall = flyrpc.multicall.MyMultiCall(client.manager)

        multicall.set_fly_trajectory(vr_parameters['fly_x_trajectory'],
                                     vr_parameters['fly_y_trajectory'],
                                     vr_parameters['fly_theta_trajectory'])

        sc = vr_parameters['sky_color']
        multicall.load_stim(name='ConstantBackground',
                            color=[sc, sc, sc, 1.0])

        fc = vr_parameters['floor_color']
        multicall.load_stim(name='TexturedGround',
                            color=[fc, fc, fc, 1.0],
                            z_level=vr_parameters['z_level'],
                            hold=True)

        multicall.load_stim(name='Forest',
                            color=[0.1, 0.1, 0.1, 1],
                            cylinder_height=vr_parameters['tree_height'],
                            cylinder_radius=0.01,
                            cylinder_locations=vr_parameters['tree_locations'],
                            n_faces=4,
                            hold=True)

        multicall.load_stim(**patch_parameters, hold=True)

        multicall()


    def getParameterDefaults(self):
        self.protocol_parameters = {'n_trees': 40,
                                    'tree_height': 1.0,
                                    'floor_color': 0.40,
                                    'sky_color': 0.5,
                                    'tree_color': 0.0,
                                    'rand_seed': 1,
                                    'trajectory_range': [0, 1, 2, 3, 4],
                                    'spot_radius': 7.5,
                                    'spot_color': 0.0,
                                    'spot_traj_frequency': 0.5,
                                    'spot_traj_amplitude': 60.0, # amp of sinusoid (1/2 of peak to trough total distance)
                                    'center': [0.0, 0.0]}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'MovingSpotOnVR',
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
        n = [3, 2, 3, 12, 6, 4, 2]  # weight each stim draw by how many trial types it has. Total = 32
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
                                                           'rv_ratio': [5.0, 20.0, 100.0],
                                                           'randomize_order': True}

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
                new_component_class.protocol_parameters = {'diameter': [5.0, 15.0, 50.0],
                                                           'intensity': [0.0, 1.0],
                                                           'center': [0, 0],
                                                           'speed': [-80.0, 80.0],
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
                                                           'grate_rate': [-120.0, -90.0, -30.0, 30.0, 90.0, 120.0],
                                                           'grate_contrast': 0.5,
                                                           'angle': 0.0,
                                                           'randomize_order': True}

            elif stim_type == 'MovingRectangle':
                new_component_class = MovingRectangle(self.cfg)
                new_component_class.protocol_parameters = {'width': 10.0,
                                                           'height': 120.0,
                                                           'intensity': [0.0, 1.0],
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
                               'num_epochs': 160, # 160 = 32 * 5 averages each
                               'pre_time': 1.5,
                               'stim_time': 3.0,
                               'tail_time': 1.5,
                               'idle_color': 0.5}


# %%

class PGS_Reduced(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.cfg = cfg
        self.stim_list = ['LoomingSpot', 'DriftingSquareGrating', 'ExpandingMovingSpot',
                          'MovingRectangle']
        n = [1, 1, 3, 1]  # weight each stim draw by how many trial types it has. Total = 6
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
                                                           'rv_ratio': 100.0,
                                                           'randomize_order': True}

            elif stim_type == 'DriftingSquareGrating':
                new_component_class = DriftingSquareGrating(self.cfg)
                new_component_class.protocol_parameters = {'period': 20.0,
                                                           'rate': 20.0,
                                                           'contrast': 1.0,
                                                           'mean': 0.5,
                                                           'angle': 0.0,
                                                           'center': [0, 0],
                                                           'center_size': 180.0,
                                                           'randomize_order': True}

            elif stim_type == 'ExpandingMovingSpot':
                new_component_class = ExpandingMovingSpot(self.cfg)
                new_component_class.protocol_parameters = {'diameter': [5.0, 15.0, 50.0],
                                                           'intensity': 0.0,
                                                           'center': [0, 0],
                                                           'speed': 80.0,
                                                           'angle': 0.0,
                                                           'randomize_order': True}

            elif stim_type == 'MovingRectangle':
                new_component_class = MovingRectangle(self.cfg)
                new_component_class.protocol_parameters = {'width': 10.0,
                                                           'height': 120.0,
                                                           'intensity': 0.0,
                                                           'center': [0, 0],
                                                           'speed': 80.0,
                                                           'angle': 0.0,
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
        self.run_parameters = {'protocol_ID': 'PGS_Reduced',
                               'num_epochs': 180,  # 180 = 6 * 30 averages each
                               'pre_time': 1.5,
                               'stim_time': 3.0,
                               'tail_time': 1.5,
                               'idle_color': 0.5}

    # %%

"""
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # DOTS STIMS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""


class CoherentDots(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        current_coherence, current_speed = self.selectParametersFromLists((self.protocol_parameters['coherence'], self.protocol_parameters['speed']),
                                                                          randomize_order=self.protocol_parameters['randomize_order'])

        current_seed = np.random.randint(0, 10000)

        self.epoch_parameters = {'name': 'MovingDotField',
                                 'n_points': int(self.protocol_parameters['n_points']),
                                 'point_size': int(self.protocol_parameters['point_size']),
                                 'sphere_radius': 1.0,
                                 'color': self.protocol_parameters['intensity'],
                                 'speed': current_speed,
                                 'signal_direction': self.protocol_parameters['signal_direction'],
                                 'coherence': current_coherence,
                                 'random_seed': current_seed}

        self.convenience_parameters = {'current_coherence': current_coherence,
                                       'current_speed': current_speed,
                                       'current_seed': current_seed}

    def getParameterDefaults(self):
        self.protocol_parameters = {'n_points': 125,  # More than ~200 causes frame drops on bruker
                                    'point_size': 80,  # width = about 15 deg in center of bruker screen
                                    'intensity': 0.0,
                                    'speed': [80.0, -80.0],
                                    'signal_direction': 0.0,
                                    'coherence': [0.0, 0.125, 0.25, 0.5, 0.75, 0.875, 1.0],
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'CoherentDots',
                               'num_epochs': 140,
                               'pre_time': 1.0,
                               'stim_time': 4.0,
                               'tail_time': 1.5,
                               'idle_color': 0.5}

# %%


class SelfMotionDots(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        current_coherence, current_speed = self.selectParametersFromLists((self.protocol_parameters['coherence'], self.protocol_parameters['speed']),
                                                                          randomize_order=self.protocol_parameters['randomize_order'])

        current_seed = np.random.randint(0, 10000)

        self.epoch_parameters = {'name': 'MovingDotField',
                                 'n_points': int(self.protocol_parameters['n_points']),
                                 'point_size': int(self.protocol_parameters['point_size']),
                                 'sphere_radius': 1.0,
                                 'color': self.protocol_parameters['intensity'],
                                 'speed': current_speed,
                                 'signal_direction': self.protocol_parameters['signal_direction'],
                                 'coherence': current_coherence,
                                 'random_seed': current_seed}

        self.convenience_parameters = {'current_coherence': current_coherence,
                                       'current_speed': current_speed,
                                       'current_seed': current_seed}

    def getParameterDefaults(self):
        self.protocol_parameters = {'n_points': 125,  # More than ~200 causes frame drops on bruker
                                    'point_size': 80,  # width = about 15 deg in center of bruker screen
                                    'intensity': 0.0,
                                    'speed': [80.0, -80.0],
                                    'signal_direction': 0.0,
                                    'coherence': [0.0, 0.125, 0.25, 0.5, 0.75, 0.875, 1.0],
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'CoherentDots',
                               'num_epochs': 140,
                               'pre_time': 1.0,
                               'stim_time': 4.0,
                               'tail_time': 1.5,
                               'idle_color': 0.5}
