#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 15 17:18:04 2022

@author: lavonna
"""
import numpy as np
import os
import flyrpc.multicall
import inspect
from time import sleep

import visprotocol
from visprotocol.protocol import clandinin_protocol


class BaseProtocol(clandinin_protocol.BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)  # call the parent class init method

    def getVisualCuedAttentionParameters(self, bar_color=None, cue_mean_color=None, 
                                         cue_contrast=None, cue_on_left=None, delay_period=None, 
                                         ):
        if bar_color is None: bar_color = self.protocol_parameters['bar_color']
        if cue_mean_color is None: cue_mean_color = self.protocol_parameters['cue_mean_color']
        if cue_contrast is None: cue_contrast = self.protocol_parameters['cue_contrast']
        if cue_on_left is None: cue_on_left = self.protocol_parameters['cue_on_left']
        if delay_period is None: delay_period = self.protocol_parameters['delay_period']

        _ = self.adjustCenter(self.protocol_parameters['center'])
        cue_temporal_frequency = self.protocol_parameters['cue_temporal_frequency']
        z_offset = self.protocol_parameters['z_offset']
        displacement_distance = self.protocol_parameters['displacement_distance']
        first_displacement_speed = self.protocol_parameters['first_displacement_speed']
        second_displacement_speed = self.protocol_parameters['second_displacement_speed']
        bar_width_degrees = self.protocol_parameters['bar_width_degrees']
        bar_height_degrees = self.protocol_parameters['bar_height_degrees']
        precue_period = self.protocol_parameters['precue_period']
        cue_period = self.protocol_parameters['cue_period']
        bg = self.run_parameters['idle_color']

        #automatically calculated
        left_bar_start_position=z_offset
        left_bar_displacement_distance=displacement_distance
        right_bar_start_position=-z_offset
        right_bar_displacement_distance=-displacement_distance
        time_at_first_displacement=abs(displacement_distance)/first_displacement_speed
        time_at_second_displacement=time_at_first_displacement+(abs(displacement_distance)/second_displacement_speed)
        test_period=time_at_second_displacement
        left_bar_position_at_first_displacement=left_bar_start_position+left_bar_displacement_distance
        right_bar_position_at_first_displacement=right_bar_start_position+right_bar_displacement_distance

        time_to_test_period = precue_period + cue_period + delay_period
        
        ########### Precue/test bars ##########
        test_color_trajectory  = {'name': 'tv_pairs',
                        'tv_pairs': [(0,             [bar_color, bar_color, bar_color, 1]), 
                                     (precue_period, [bar_color, bar_color, bar_color, 0]),
                                     (time_to_test_period, [bar_color, bar_color, bar_color, 1])],
                        'kind': 'previous'}
        test_l_theta_trajectory  = {'name': 'tv_pairs',
                                'tv_pairs': [(0, left_bar_start_position), 
                                             (time_to_test_period + 0, left_bar_start_position), 
                                             (time_to_test_period + time_at_first_displacement, left_bar_position_at_first_displacement),
                                             (time_to_test_period + time_at_second_displacement, left_bar_start_position)],
                                'kind': 'linear'}
        test_r_theta_trajectory = {'name': 'tv_pairs',
                                'tv_pairs': [(0, right_bar_start_position),
                                             (time_to_test_period + 0, right_bar_start_position),
                                             (time_to_test_period + time_at_first_displacement, right_bar_position_at_first_displacement),
                                             (time_to_test_period + time_at_second_displacement, right_bar_start_position)],
                                'kind': 'linear'}

        test_l_parameters = {'name': 'MovingPatchOnCylinder',
                            'width': bar_width_degrees,
                            'height': bar_height_degrees,
                            'color': test_color_trajectory,
                            'theta': test_l_theta_trajectory,
                            'phi': 0,
                            'cylinder_radius': 1}
        test_r_parameters = {'name': 'MovingPatchOnCylinder',
                            'width': bar_width_degrees,
                            'height': bar_height_degrees,
                            'color': test_color_trajectory,
                            'theta': test_r_theta_trajectory,
                            'phi': 0,
                            'cylinder_radius': 1}
    
        ####################
        


        ########### Cue bar ##########

        # LM's original flickering cue
        # color Trajectory
        cue_amplitude = cue_mean_color * cue_contrast
        cue_max_color = cue_amplitude + cue_amplitude
        cue_min_color = cue_amplitude - cue_amplitude
        print(cue_period)
        cue_timestamps = np.linspace(0, cue_period, int(np.ceil(cue_temporal_frequency*cue_period*2+1)))
        #cue_timestamps = np.linspace(0.0, float(cue_period), cue_temporal_frequency*cue_period*2+1) + float(precue_period)
        cue_colors = np.append(np.tile([cue_min_color,cue_max_color], int(np.ceil(cue_temporal_frequency*cue_period))), cue_min_color)
        
        tv_pairs = np.stack((cue_timestamps, cue_colors), axis=1)
        # tv_pairs = np.insert(tv_pairs, 0, [0.0, float(bg)], axis=0)
        # tv_pairs = np.append(tv_pairs, [float(precue_period+cue_period), float(bg)], axis=0)
        
        
        cue_color_traj = {'name':'tv_pairs','tv_pairs':tv_pairs.tolist(),'kind':'linear'}
        
        # Cue with sinusoidal color modulation
        # cue_color_traj = {'name': 'SinusoidWithDelay',
        #                     'temporal_frequency': cue_temporal_frequency,
        #                     'amplitude': cue_mean_color * cue_contrast,
        #                     'offset': cue_mean_color,
        #                     'stim_start': precue_period,
        #                     'stim_end': precue_period+cue_period}

        cue_parameters = {'name': 'MovingPatchOnCylinder',
                            'width': bar_width_degrees,
                            'height': bar_height_degrees,
                            'color': cue_color_traj,
                            'theta': left_bar_start_position if cue_on_left==1 else right_bar_start_position,
                            'phi': 0,
                            'cylinder_radius': 2}
        
        #####################


        # Compute total stimulus duration
        stim_duration = precue_period + cue_period + delay_period + test_period

        return cue_parameters, test_l_parameters, test_r_parameters, stim_duration


    def getVisualCuedAttentionV1Parameters(self, bar_color=None, cue_mean_color=None, 
                                         cue_contrast=None, cue_on_left=None, delay_period=None, 
                                         ):
        if bar_color is None: bar_color = self.protocol_parameters['bar_color']
        if cue_mean_color is None: cue_mean_color = self.protocol_parameters['cue_mean_color']
        if cue_contrast is None: cue_contrast = self.protocol_parameters['cue_contrast']
        if cue_on_left is None: cue_on_left = self.protocol_parameters['cue_on_left']
        if delay_period is None: delay_period = self.protocol_parameters['delay_period']

        _ = self.adjustCenter(self.protocol_parameters['center'])
        cue_temporal_frequency = self.protocol_parameters['cue_temporal_frequency']
        z_offset = self.protocol_parameters['z_offset']
        displacement_distance = self.protocol_parameters['displacement_distance']
        first_displacement_speed = self.protocol_parameters['first_displacement_speed']
        second_displacement_speed = self.protocol_parameters['second_displacement_speed']
        bar_width_degrees = self.protocol_parameters['bar_width_degrees']
        bar_height_degrees = self.protocol_parameters['bar_height_degrees']
        precue_period = self.protocol_parameters['precue_period']
        cue_period = self.protocol_parameters['cue_period']

        #automatically calculated
        left_bar_start_position=z_offset
        left_bar_displacement_distance=displacement_distance
        right_bar_start_position=-z_offset
        right_bar_displacement_distance=-displacement_distance
        time_at_first_displacement=abs(displacement_distance)/first_displacement_speed
        time_at_second_displacement=time_at_first_displacement+(abs(displacement_distance)/second_displacement_speed)
        test_period=time_at_second_displacement
        left_bar_position_at_first_displacement=left_bar_start_position+left_bar_displacement_distance
        right_bar_position_at_first_displacement=right_bar_start_position+right_bar_displacement_distance

        ########### Precue bars ##########
        precue_l_parameters = {'name': 'MovingPatchOnCylinder',
                            'width': bar_width_degrees,
                            'height': bar_height_degrees,
                            'color': bar_color,
                            'theta': left_bar_start_position,
                            'phi': 0,
                            'cylinder_radius': 1}
        precue_r_parameters = {'name': 'MovingPatchOnCylinder',
                            'width': bar_width_degrees,
                            'height': bar_height_degrees,
                            'color': bar_color,
                            'theta': right_bar_start_position,
                            'phi': 0,
                            'cylinder_radius': 1}
        
        #####################


        ########### Cue bar ##########

        # LM's original flickering cue
        # color Trajectory
        # cue_amplitude = cue_mean_color * cue_contrast
        # cue_max_color = cue_amplitude + cue_amplitude
        # cue_min_color = cue_amplitude - cue_amplitude
        # cue_timestamps = np.linspace(0, cue_period, cue_temporal_frequency*cue_period*2+1)
        # cue_colors = np.append(np.tile([cue_min_color,cue_max_color], cue_temporal_frequency*cue_period), cue_min_color)
        # cue_color_traj = {'name':'tv_pairs','tv_pairs':np.stack((cue_timestamps, cue_colors), axis=1).tolist(),'kind':'linear'}
        
        # Cue with sinusoidal color modulation
        cue_color_traj = {'name': 'Sinusoid',
                            'temporal_frequency': cue_temporal_frequency,
                            'amplitude': cue_mean_color * cue_contrast,
                            'offset': cue_mean_color}

        cue_parameters = {'name': 'MovingPatchOnCylinder',
                            'width': bar_width_degrees,
                            'height': bar_height_degrees,
                            'color': cue_color_traj,
                            'theta': left_bar_start_position if cue_on_left==1 else right_bar_start_position,
                            'phi': 0,
                            'cylinder_radius': 1}
        
        #####################


        ########### Test bars ##########
        # test left bar
        theta_trajectory_test_left  = {'name': 'tv_pairs',
                                'tv_pairs': [(0, left_bar_start_position), 
                                             (time_at_first_displacement, left_bar_position_at_first_displacement),
                                             (time_at_second_displacement, left_bar_start_position)],
                                'kind': 'linear'}
        test_l_parameters = {'name': 'MovingPatchOnCylinder',
                            'width': bar_width_degrees,
                            'height': bar_height_degrees,
                            'color': bar_color,
                            'theta': theta_trajectory_test_left,
                            'phi': 0,
                            'cylinder_radius': 1}
        # test right bar
        theta_trajectory_test_right = {'name': 'tv_pairs',
                                'tv_pairs': [(0, right_bar_start_position),
                                             (time_at_first_displacement, right_bar_position_at_first_displacement),
                                             (time_at_second_displacement, right_bar_start_position)],
                                'kind': 'linear'}
        test_r_parameters = {'name': 'MovingPatchOnCylinder',
                            'width': bar_width_degrees,
                            'height': bar_height_degrees,
                            'color': bar_color,
                            'theta': theta_trajectory_test_right,
                            'phi': 0,
                            'cylinder_radius': 1}
        ####################
        
        # Compute total stimulus duration
        stim_duration = precue_period + cue_period + delay_period + test_period

        return precue_l_parameters, precue_r_parameters, cue_parameters, test_l_parameters, test_r_parameters, stim_duration


# %%

"""
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # FLY-CENTERED STIMS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""

class VisualCuedAttention(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        current_bar_color, current_cue_contrast, current_cue_on_left, current_delay_period = self.selectParametersFromLists((self.protocol_parameters['bar_color'], 
                                                                                                                             self.protocol_parameters['cue_contrast'], 
                                                                                                                             self.protocol_parameters['cue_on_left'], 
                                                                                                                             self.protocol_parameters['delay_period']), 
                                                                                                                            randomize_order=self.protocol_parameters['randomize_order'])

        cue_parameters, test_l_parameters, test_r_parameters, stim_duration = self.getVisualCuedAttentionParameters(bar_color=current_bar_color, cue_contrast=current_cue_contrast, cue_on_left=current_cue_on_left, delay_period=current_delay_period)
        self.epoch_parameters = (cue_parameters, test_l_parameters, test_r_parameters)

        self.convenience_parameters = {'current_bar_color': current_bar_color,
                                       'current_cue_contrast': current_cue_contrast,
                                       'current_cue_on_left': current_cue_on_left,
                                       'current_delay_period': current_delay_period,
                                       'current_stim_duration': stim_duration
                                      }

    def loadStimuli(self, client):
        cue_parameters = self.epoch_parameters[0]
        test_l_parameters = self.epoch_parameters[1]
        test_r_parameters = self.epoch_parameters[2]
        self.run_parameters['stim_time'] = self.convenience_parameters['current_stim_duration']
    
        bg = self.run_parameters.get('idle_color')
        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        multicall.load_stim(name='ConstantBackground', color=[bg,bg,bg,1], side_length=200)
        multicall.load_stim(**test_l_parameters, hold=True)
        multicall.load_stim(**test_r_parameters, hold=True)
        multicall.load_stim(**cue_parameters, hold=True)
        multicall()

    def startStimuli(self, client, append_stim_frames=False, print_profile=True):
        sleep(self.run_parameters['pre_time'])
        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        # stim time
        multicall.start_stim(append_stim_frames=append_stim_frames)
        multicall.start_corner_square()
        multicall()
        sleep(self.convenience_parameters['current_stim_duration'])

        # tail time
        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        multicall.stop_stim(print_profile=print_profile)
        multicall.black_corner_square()
        multicall()

        sleep(self.run_parameters['tail_time'])

    def getParameterDefaults(self):
        self.protocol_parameters = {'center': [0, 0],
                                    'z_offset': 32.0,
                                    'displacement_distance': 100.0,
                                    'first_displacement_speed': 50.0,
                                    'second_displacement_speed': 50.0,
                                    'bar_width_degrees': 15.0,
                                    'bar_height_degrees': 150.0,
                                    'bar_color': [0.0, 0.5],
                                    'cue_temporal_frequency': 5.0,
                                    'cue_mean_color': 0.25,
                                    'cue_contrast': [1.0],
                                    'cue_on_left': [0,1], #0: right, 1: left
                                    'precue_period': 5.0,
                                    'cue_period': 2.0,
                                    'delay_period': [0.0, 1.0],
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'VisualCuedAttention',
                               'num_epochs': 80, # 12 x 20 each
                               'pre_time': 1.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5,
                               'stim_time': 5.5}


class VisualCuedAttentionV1(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        current_bar_color, current_cue_contrast, current_cue_on_left, current_delay_period = self.selectParametersFromLists((self.protocol_parameters['bar_color'], 
                                                                                                                             self.protocol_parameters['cue_contrast'], 
                                                                                                                             self.protocol_parameters['cue_on_left'], 
                                                                                                                             self.protocol_parameters['delay_period']), 
                                                                                                                            randomize_order=self.protocol_parameters['randomize_order'])

        precue_l_parameters, precue_r_parameters, cue_parameters, test_l_parameters, test_r_parameters, stim_duration = self.getVisualCuedAttentionV1Parameters(bar_color=current_bar_color, cue_contrast=current_cue_contrast, cue_on_left=current_cue_on_left, delay_period=current_delay_period)
        self.epoch_parameters = (precue_l_parameters, precue_r_parameters, cue_parameters, test_l_parameters, test_r_parameters)

        self.convenience_parameters = {'current_bar_color': current_bar_color,
                                       'current_cue_contrast': current_cue_contrast,
                                       'current_cue_on_left': current_cue_on_left,
                                       'current_delay_period': current_delay_period,
                                       'current_stim_duration': stim_duration
                                      }

    def loadStimuli(self, client):
        precue_l_parameters = self.epoch_parameters[0]
        precue_r_parameters = self.epoch_parameters[1]
        self.run_parameters['stim_time'] = self.convenience_parameters['current_stim_duration']
    
        bg = self.run_parameters.get('idle_color')
        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        multicall.load_stim(name='ConstantBackground', color=[bg,bg,bg,1], side_length=200)
        multicall.load_stim(**precue_l_parameters, hold=True)
        multicall.load_stim(**precue_r_parameters, hold=True)
        multicall()

    def startStimuli(self, client, append_stim_frames=False, print_profile=True):
        bg = self.run_parameters.get('idle_color')
        cue_parameters = self.epoch_parameters[2]
        test_l_parameters = self.epoch_parameters[3]
        test_r_parameters = self.epoch_parameters[4]

        sleep(self.run_parameters['pre_time'])
        
        # precue
        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        multicall.start_stim(append_stim_frames=append_stim_frames)
        multicall.start_corner_square()
        multicall()
        sleep(self.protocol_parameters['precue_period'])
        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        multicall.stop_stim(print_profile=print_profile)
        #multicall.black_corner_square()
        multicall()

        # cue
        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        multicall.load_stim(name='ConstantBackground', color=[bg,bg,bg,1], side_length=200)
        multicall.load_stim(**cue_parameters, hold=True)
        multicall.start_stim(append_stim_frames=append_stim_frames)
        #multicall.start_corner_square()
        multicall()
        sleep(self.protocol_parameters['cue_period'])
        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        multicall.stop_stim(print_profile=print_profile)
        #multicall.black_corner_square()
        multicall()
        
        # delay
        sleep(self.convenience_parameters['current_delay_period'])

        # test
        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        multicall.load_stim(name='ConstantBackground', color=[bg,bg,bg,1], side_length=200)
        multicall.load_stim(**test_l_parameters, hold=True)
        multicall.load_stim(**test_r_parameters, hold=True)
        multicall.start_stim(append_stim_frames=append_stim_frames)
        #multicall.start_corner_square()
        multicall()
        sleep(self.convenience_parameters['current_stim_duration'] - self.convenience_parameters['current_delay_period'] 
              - self.protocol_parameters['cue_period'] - self.protocol_parameters['precue_period'])

        # tail time
        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        multicall.stop_stim(print_profile=print_profile)
        multicall.black_corner_square()
        multicall()

        sleep(self.run_parameters['tail_time'])

    def getParameterDefaults(self):
        self.protocol_parameters = {'center': [0, 0],
                                    'z_offset': 32.0,
                                    'displacement_distance': 100.0,
                                    'first_displacement_speed': 50.0,
                                    'second_displacement_speed': 50.0,
                                    'bar_width_degrees': 15.0,
                                    'bar_height_degrees': 150.0,
                                    'bar_color': [0.0, 0.5],
                                    'cue_temporal_frequency': 5.0,
                                    'cue_mean_color': 0.25,
                                    'cue_contrast': [1.0],
                                    'cue_on_left': [0,1], #0: right, 1: left
                                    'precue_period': 5.0,
                                    'cue_period': 2.0,
                                    'delay_period': [0.0, 1.0],
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'VisualCuedAttention',
                               'num_epochs': 80, # 12 x 20 each
                               'pre_time': 1.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5,
                               'stim_time': 5.5}

#%%

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

