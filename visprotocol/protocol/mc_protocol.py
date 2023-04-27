#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 10:20:02 2018

@author: minseung and mhturner
"""
import numpy as np
import flyrpc.multicall
from time import sleep

from visprotocol.protocol import clandinin_protocol


class BaseProtocol(clandinin_protocol.BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)  # call the parent class init method

    def getMovingPatchParameters(self, center=None, angle=None, speed=None, width=None, height=None, color=None, distance_to_travel=None, ellipse=None, render_on_cylinder=None):
        if center is None: center = self.adjustCenter(self.protocol_parameters['center'])
        if angle is None: angle = self.protocol_parameters['angle']
        if speed is None: speed = self.protocol_parameters['speed']
        if width is None: width = self.protocol_parameters['width']
        if height is None: height = self.protocol_parameters['height']
        if color is None: color = self.protocol_parameters['color']
        if ellipse is None: ellipse = self.protocol_parameters['ellipse'] if 'ellipse' in self.protocol_parameters else False
        if render_on_cylinder is None: render_on_cylinder = self.protocol_parameters['render_on_cylinder'] if 'render_on_cylinder' in self.protocol_parameters else False

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
            travel_time = np.abs(distance_to_travel / speed)
            distance_to_travel = np.sign(speed) * distance_to_travel
            if travel_time > stim_time:
                print('Warning: stim_time is too short to show whole trajectory at this speed!')
                hang_time = 0
            else:
                hang_time = (stim_time - travel_time)/2

            # split up hang time in pre and post such that trajectory always hits centerX,centerY at stim_time/2
            x_1 = (0, centerX - np.cos(np.radians(angle)) * distance_to_travel/2)
            x_2 = (hang_time, centerX - np.cos(np.radians(angle)) * distance_to_travel/2)
            x_3 = (stim_time-hang_time, centerX + np.cos(np.radians(angle)) * distance_to_travel/2)
            x_4 = (stim_time, centerX + np.cos(np.radians(angle)) * distance_to_travel/2)

            y_1 = (0, centerY - np.sin(np.radians(angle)) * distance_to_travel/2)
            y_2 = (hang_time, centerY - np.sin(np.radians(angle)) * distance_to_travel/2)
            y_3 = (stim_time-hang_time, centerY + np.sin(np.radians(angle)) * distance_to_travel/2)
            y_4 = (stim_time, centerY + np.sin(np.radians(angle)) * distance_to_travel/2)

            x = [x_1, x_2, x_3, x_4]
            y = [y_1, y_2, y_3, y_4]

        x_trajectory = {'name': 'tv_pairs',
                        'tv_pairs': x,
                        'kind': 'linear'}
        y_trajectory = {'name': 'tv_pairs',
                        'tv_pairs': y,
                        'kind': 'linear'}

        if render_on_cylinder:
            flystim_stim_name = 'MovingEllipseOnCylinder' if ellipse else 'MovingPatchOnCylinder'
        else:
            flystim_stim_name = 'MovingEllipse' if ellipse else 'MovingPatch'
        
        patch_parameters = {'name': flystim_stim_name,
                            'width': width,
                            'height': height,
                            'color': color,
                            'theta': x_trajectory,
                            'phi': y_trajectory,
                            'angle': angle}
        return patch_parameters
    
# %%

"""
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # FLY-CENTERED STIMS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""
# %%

class OcclusionDuration(BaseProtocol):
    '''
    Occluder is defined by the occlusion duration.
    '''
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):

        # Select protocol parameters for this epoch
        self.convenience_parameters = self.selectParametersFromProtocolParameterNames(
            ['obj_width', 'obj_prime_color', 'obj_probe_color', 'obj_speed', 'occluder_color', 'occlusion_duration', 'pause_duration', 'closed_loop', 'opto_pre_time', 'opto_stim_time', 'opto_freq', 'opto_amp', 'opto_pulse_width'], 
            randomize_order = self.protocol_parameters['randomize_order'])

        # Set variables for convenience
        obj_ellipse = self.protocol_parameters['obj_ellipse']
        obj_width = self.convenience_parameters['current_obj_width']
        obj_height = self.protocol_parameters['obj_height']
        obj_prime_color = self.convenience_parameters['current_obj_prime_color']
        obj_probe_color = self.convenience_parameters['current_obj_probe_color']
        obj_start_theta = self.protocol_parameters['obj_start_theta']
        obj_speed = self.convenience_parameters['current_obj_speed']
        obj_surface_radius = self.protocol_parameters['obj_surface_radius']
        
        occluder_ellipse = self.protocol_parameters['occluder_ellipse']
        occluder_height = self.protocol_parameters['occluder_height']
        occluder_color = self.convenience_parameters['current_occluder_color']
        occluder_surface_radius = self.protocol_parameters['occluder_surface_radius']
        
        render_on_cylinder = self.protocol_parameters['render_on_cylinder']
        center = self.protocol_parameters['center']
        centerX = center[0]

        preprime_duration = self.protocol_parameters['preprime_duration']
        prime_duration = self.protocol_parameters['prime_duration']
        occlusion_duration = self.convenience_parameters['current_occlusion_duration']
        pause_duration = self.convenience_parameters['current_pause_duration']
        probe_duration = self.protocol_parameters['probe_duration']

        ### Stimulus construction ###
        
        stim_duration = preprime_duration + prime_duration + occlusion_duration + probe_duration + pause_duration

        # consistent obj trajectory
        obj_start_theta *= np.sign(obj_speed)
        time = [0, preprime_duration]
        x = [obj_start_theta, obj_start_theta]
        obj_color = [obj_prime_color, obj_prime_color]

        prime_movement = obj_speed * (prime_duration + occlusion_duration)
        prime_end_theta = obj_start_theta + prime_movement
        prime_end_time = preprime_duration + prime_duration + occlusion_duration

        time.append(prime_end_time)
        x.append(prime_end_theta)
        obj_color.append(obj_prime_color)

        pause_end_theta = prime_end_theta
        pause_end_time = prime_end_time + pause_duration

        time.append(pause_end_time)
        x.append(pause_end_theta)
        obj_color.append(obj_probe_color)

        probe_movement = obj_speed * probe_duration
        probe_end_theta = pause_end_theta + probe_movement
        probe_end_time = pause_end_time + probe_duration

        time.append(probe_end_time)
        x.append(probe_end_theta)
        obj_color.append(obj_probe_color)

        # Compute location and width of the occluder per specification
        occlusion_start_theta = obj_start_theta + obj_speed * prime_duration
        occluder_width = np.abs(obj_speed) * occlusion_duration + obj_width # the last term ensures that the obj is completely hidden during the occlusion period
        occluder_loc = occlusion_start_theta + np.sign(obj_speed) * (occluder_width/2 - obj_width/2) # the last two terms account for widths of the obj and the occluder, such that the obj is completely hidden during occlusion period
        occluder_time = [0, stim_duration]
        occluder_x = [occluder_loc, occluder_loc]

        ### Create flystim trajectory objects ###
        obj_theta_traj      = {'name': 'tv_pairs', 'tv_pairs': list(zip(time, (centerX + np.array(x)).tolist())), 'kind': 'linear'}
        obj_color_traj      = {'name': 'tv_pairs', 'tv_pairs': list(zip(time, obj_color)), 'kind': 'linear'}
        occluder_theta_traj = {'name': 'tv_pairs', 'tv_pairs': list(zip(occluder_time, (centerX + np.array(occluder_x)).tolist())), 'kind': 'linear'}

        # Create epoch parameters dictionary
        if render_on_cylinder:
            obj_flystim_stim_name = 'MovingEllipseOnCylinder' if obj_ellipse else 'MovingPatchOnCylinder'
            occluder_flystim_stim_name = 'MovingEllipseOnCylinder' if occluder_ellipse else 'MovingPatchOnCylinder'
            surface_dim_name = 'cylinder_radius'
        else:
            obj_flystim_stim_name = 'MovingEllipse' if obj_ellipse else 'MovingPatch'
            occluder_flystim_stim_name = 'MovingEllipse' if occluder_ellipse else 'MovingPatch'
            surface_dim_name = 'sphere_radius'
        
        obj_parameters = {'name': obj_flystim_stim_name,
                            'width': obj_width,
                            'height': obj_height,
                            'color': obj_color_traj,
                            'theta': obj_theta_traj,
                            'phi': 0,
                            'angle': 0,
                            surface_dim_name: obj_surface_radius}
        occluder_parameters = {'name': occluder_flystim_stim_name,
                            'width': occluder_width,
                            'height': occluder_height,
                            'color': occluder_color,
                            'theta': occluder_theta_traj,
                            'phi': 0,
                            'angle': 0,
                            surface_dim_name: occluder_surface_radius}

        self.epoch_parameters = [obj_parameters, occluder_parameters]
        self.convenience_parameters['current_stim_time'] = stim_duration

    def loadStimuli(self, client, multicall=None):
        self.run_parameters['stim_time'] = self.convenience_parameters['current_stim_time']

        if multicall is None:
            multicall = flyrpc.multicall.MyMultiCall(client.manager)
        
        conv_params_to_print = {k[8:]:v for k,v in self.convenience_parameters.items()}
        multicall.print_on_server(f'{conv_params_to_print}')

        # set up opto pulse wave
        multicall.daq_setupPulseWaveStreamOut(output_channel='DAC0', 
                                              freq=self.convenience_parameters['current_opto_freq'], 
                                              amp=self.convenience_parameters['current_opto_amp'], 
                                              pulse_width=self.convenience_parameters['current_opto_pulse_width'], 
                                              pulse_width=self.convenience_parameters['current_opto_pulse_width'],
                                              scanRate=5000)
        multicall.daq_streamWithTiming(pre_time=self.convenience_parameters['current_opto_pre_time'],
                                       stim_time=self.convenience_parameters['current_opto_stim_time'],
                                       scanRate=5000, scansPerRead=1000)


    def getParameterDefaults(self):
        self.protocol_parameters = {'obj_ellipse': True,
                                    'obj_width': 25.0,
                                    'obj_height': 15.0,
                                    'obj_prime_color': [1.0, 0.0],
                                    'obj_probe_color': 1.0,
                                    'obj_start_theta': -90.0,
                                    'obj_speed': [-35.0, -25.0, -15.0, 15.0, 25.0, 35.0],
                                    'obj_surface_radius': 3.0,

                                    'occluder_ellipse': False,
                                    'occluder_height': 170.0,
                                    'occluder_color': 0.0,
                                    'occluder_surface_radius': 2.0,

                                    'render_on_cylinder': False,
                                    'center': [0, 0],
                                    'closed_loop': [0],

                                    'preprime_duration': 0.0,
                                    'prime_duration': 2.0,
                                    'occlusion_duration': [0.5, 2.0],
                                    'pause_duration': [0.0, 1.0],
                                    'probe_duration': 1.5,

                                    'opto_pre_time': [0.0],
                                    'opto_stim_time': [1.0],
                                    'opto_freq': [50.0],
                                    'opto_amp': [2.5],
                                    'opto_pulse_width': [0.01],

                                    'randomize_order': True,}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'OcclusionDuration',
                               'num_epochs': 240, # 12 x 20 each
                               'pre_time': 1.0,
                               'tail_time': 1.0,
                               'idle_color': 0.0}

# %%

class OcclusionShape(BaseProtocol):
    '''
    Occluder is defined by its shape (width and height, ellipse vs rectangle)
    '''

    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):

        # Select protocol parameters for this epoch
        self.convenience_parameters = self.selectParametersFromProtocolParameterNames(
            ['angle', 'obj_start_theta', 'obj_wh', 'obj_prime_color', 'obj_probe_color', 'obj_speed', 'occluder_wh', 'occluder_color', 'pause_duration', 'closed_loop', 'opto_pre_time', 'opto_freq', 'opto_amp', 'opto_pulse_width'],
            randomize_order = self.protocol_parameters['randomize_order'])

        # Set variables for convenience
        obj_ellipse = self.protocol_parameters['obj_ellipse']
        obj_start_theta = self.convenience_parameters['current_obj_start_theta'] #negative value starts from the opposite side of obj direction
        obj_end_theta = self.protocol_parameters['obj_end_theta']
        obj_width = self.convenience_parameters['current_obj_wh'][0]
        obj_height = self.convenience_parameters['current_obj_wh'][1]
        obj_prime_color = self.convenience_parameters['current_obj_prime_color']
        obj_probe_color = self.convenience_parameters['current_obj_probe_color']
        obj_speed = self.convenience_parameters['current_obj_speed']
        obj_surface_radius = self.protocol_parameters['obj_surface_radius']

        occluder_ellipse = self.protocol_parameters['occluder_ellipse']
        occluder_theta = self.protocol_parameters['occluder_theta']
        occluder_width = self.convenience_parameters['current_occluder_wh'][0]
        occluder_height = self.convenience_parameters['current_occluder_wh'][1]
        occluder_color = self.convenience_parameters['current_occluder_color']
        occluder_surface_radius = self.protocol_parameters['occluder_surface_radius']

        preprime_duration = self.protocol_parameters['preprime_duration']
        pause_duration = self.convenience_parameters['current_pause_duration']

        render_on_cylinder = self.protocol_parameters['render_on_cylinder']
        center = self.protocol_parameters['center']
        centerX = center[0]
        angle = self.convenience_parameters['current_angle']

        ### Stimulus construction ###

        obj_start_theta *= np.sign(obj_speed)
        obj_end_theta *= np.sign(obj_speed)
        occluder_theta *= np.sign(obj_speed)

        # Object
        theta_distance = np.abs(obj_end_theta - obj_start_theta)
        prime_distance = np.abs(occluder_theta - obj_start_theta)
        prime_duration = prime_distance / np.abs(obj_speed)
        probe_distance = np.abs(obj_end_theta - occluder_theta)
        probe_duration = probe_distance / np.abs(obj_speed)
        obj_duration_wo_pause = theta_distance / np.abs(obj_speed)
        obj_duration_w_pause = obj_duration_wo_pause + pause_duration
        stim_duration = preprime_duration + obj_duration_w_pause

        # Object trajectory
        time =       [0,
                      preprime_duration,
                      preprime_duration+prime_duration,
                      preprime_duration+prime_duration+pause_duration,
                      stim_duration]
        x =          [obj_start_theta,
                      obj_start_theta,
                      occluder_theta,
                      occluder_theta,
                      obj_end_theta]
        obj_color =  [obj_prime_color,
                      obj_prime_color,
                      obj_prime_color,
                      obj_probe_color,
                      obj_probe_color]

        # Occluder trajectory
        occluder_time = [0, stim_duration]
        occluder_x = [occluder_theta, occluder_theta]

        ### Create flystim trajectory objects ###
        obj_theta_traj      = {'name': 'tv_pairs', 'tv_pairs': list(zip(time, (centerX + np.array(x)).tolist())), 'kind': 'linear'}
        obj_color_traj      = {'name': 'tv_pairs', 'tv_pairs': list(zip(time, obj_color)), 'kind': 'previous'}
        occluder_theta_traj = {'name': 'tv_pairs', 'tv_pairs': list(zip(occluder_time, (centerX + np.array(occluder_x)).tolist())), 'kind': 'linear'}

        # Create epoch parameters dictionary
        if render_on_cylinder:
            obj_flystim_stim_name = 'MovingEllipseOnCylinder' if obj_ellipse else 'MovingPatchOnCylinder'
            occluder_flystim_stim_name = 'MovingEllipseOnCylinder' if occluder_ellipse else 'MovingPatchOnCylinder'
            surface_dim_name = 'cylinder_radius'
        else:
            obj_flystim_stim_name = 'MovingEllipse' if obj_ellipse else 'MovingPatch'
            occluder_flystim_stim_name = 'MovingEllipse' if occluder_ellipse else 'MovingPatch'
            surface_dim_name = 'sphere_radius'

        obj_parameters = {'name': obj_flystim_stim_name,
                            'width': obj_width,
                            'height': obj_height,
                            'color': obj_color_traj,
                            'theta': obj_theta_traj,
                            'phi': 0,
                            'angle': angle,
                            surface_dim_name: obj_surface_radius}
        occluder_parameters = {'name': occluder_flystim_stim_name,
                            'width': occluder_width,
                            'height': occluder_height,
                            'color': occluder_color,
                            'theta': occluder_theta_traj,
                            'phi': 0,
                            'angle': angle,
                            surface_dim_name: occluder_surface_radius}

        self.epoch_parameters = [obj_parameters, occluder_parameters]
        self.convenience_parameters['current_stim_time'] = stim_duration

        # opto
        self.convenience_parameters['current_opto_stim_time'] = stim_duration + self.run_parameters['pre_time'] - self.convenience_parameters['current_opto_pre_time']

    def loadStimuli(self, client, multicall=None):
        self.run_parameters['stim_time'] = self.convenience_parameters['current_stim_time']

        if multicall is None:
            multicall = flyrpc.multicall.MyMultiCall(client.manager)

        conv_params_to_print = {k[8:]:v for k,v in self.convenience_parameters.items()}
        multicall.print_on_server(f'{conv_params_to_print}')

        # set up opto pulse wave
        multicall.daq_setupPulseWaveStreamOut(output_channel='DAC0',
                                              freq=self.convenience_parameters['current_opto_freq'],
                                              amp=self.convenience_parameters['current_opto_amp'],
                                              pulse_width=self.convenience_parameters['current_opto_pulse_width'],
                                              scanRate=5000)
        multicall.daq_streamWithTiming(pre_time=self.convenience_parameters['current_opto_pre_time'],
                                       stim_time=self.convenience_parameters['current_opto_stim_time'],
                                       scanRate=5000, scansPerRead=1000)

        super().loadStimuli(client, multicall)

    def getParameterDefaults(self):
        self.protocol_parameters = {'obj_ellipse': True,
                                    'obj_start_theta': [0.0],
                                    'obj_end_theta': 210.0,
                                    'obj_wh': [[35.0, 25.0]],
                                    'obj_prime_color': [0.3],
                                    'obj_probe_color': 0.3,
                                    'obj_speed': [30.0, -30.0],
                                    'obj_surface_radius': 3.0,

                                    'occluder_ellipse': False,
                                    'occluder_theta': 120.0,
                                    'occluder_wh': [[0.0, 100.0], [60.0, 100.0]],
                                    'occluder_color': [0.0],
                                    'occluder_surface_radius': 2.0,

                                    'render_on_cylinder': True,
                                    'center': [0, 0],
                                    'angle': [0.0],
                                    'closed_loop': [0],

                                    'preprime_duration': 1.0,
                                    'pause_duration': [0.0],

                                    'opto_pre_time': [0.0],
                                    'opto_freq': [50.0],
                                    'opto_amp': [2.5],
                                    'opto_pulse_width': [0.01],

                                    'randomize_order': True,}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'OcclusionShape',
                               'num_epochs': 240, # 12 x 20 each
                               'pre_time': 1.0,
                               'tail_time': 1.0,
                               'idle_color': 1.0}

# %%
class PatchFixation(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):

        # Select protocol parameters for this epoch
        if self.protocol_parameters['theta_random']:

            self.convenience_parameters = self.selectParametersFromProtocolParameterNames(
                ['width', 'height', 'intensity', 'angle', 'closed_loop', 'opto_pre_time', 'opto_stim_time', 'opto_freq', 'opto_amp', 'opto_pulse_width'],
                randomize_order = self.protocol_parameters['randomize_order'])

            self.convenience_parameters['current_theta'] = np.random.uniform(*self.protocol_parameters['theta_random_range'])
        else:
            self.convenience_parameters = self.selectParametersFromProtocolParameterNames(
                ['width', 'height', 'intensity', 'angle', 'theta', 'closed_loop', 'opto_pre_time', 'opto_stim_time', 'opto_freq', 'opto_amp', 'opto_pulse_width'],
                randomize_order = self.protocol_parameters['randomize_order'])

        # Create epoch parameters dictionary
        if self.protocol_parameters['render_on_cylinder']:
            flystim_stim_name = 'MovingEllipseOnCylinder' if self.protocol_parameters['ellipse'] else 'MovingPatchOnCylinder'
            surface_dim_name = 'cylinder_radius'
        else:
            flystim_stim_name = 'MovingEllipse' if self.protocol_parameters['ellipse'] else 'MovingPatch'
            surface_dim_name = 'sphere_radius'
        self.epoch_parameters = {'name': flystim_stim_name,
                                 'width': self.convenience_parameters['current_width'],
                                 'height': self.convenience_parameters['current_height'],
                                 'color': self.convenience_parameters['current_intensity'],
                                 'theta': self.convenience_parameters['current_theta'],
                                 'angle': self.convenience_parameters['current_angle'],
                                 surface_dim_name: 1.0}

    def loadStimuli(self, client, multicall=None):

        if multicall is None:
            multicall = flyrpc.multicall.MyMultiCall(client.manager)

        conv_params_to_print = {k[8:]:v for k,v in self.convenience_parameters.items()}
        multicall.print_on_server(f'{conv_params_to_print}')

        # set up opto pulse wave
        multicall.daq_setupPulseWaveStreamOut(output_channel='DAC0',
                                              freq=self.convenience_parameters['current_opto_freq'],
                                              amp=self.convenience_parameters['current_opto_amp'],
                                              pulse_width=self.convenience_parameters['current_opto_pulse_width'],
                                              scanRate=5000)
        multicall.daq_streamWithTiming(pre_time=self.convenience_parameters['current_opto_pre_time'],
                                       stim_time=self.convenience_parameters['current_opto_stim_time'],
                                       scanRate=5000, scansPerRead=1000)

        super().loadStimuli(client, multicall)

    def getParameterDefaults(self):
        self.protocol_parameters = {'ellipse': True,
                                    'width': [35.0],
                                    'height': [25.0],
                                    'intensity': [0.0],
                                    'angle': [0.0],
                                    'theta': [0.0],
                                    'theta_random': False,
                                    'theta_random_range': [-120.0, 120.0],

                                    'render_on_cylinder': True,
                                    'closed_loop': [0],

                                    'opto_pre_time': [0.0],
                                    'opto_stim_time': [1.0],
                                    'opto_freq': [50.0],
                                    'opto_amp': [2.5],
                                    'opto_pulse_width': [0.01],

                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'PatchFixation',
                               'num_epochs': 40,
                               'pre_time': 0.5,
                               'stim_time': 3.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}

# %%
class PatchFixationOptoPaired(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):

        # Select protocol parameters for this epoch
        self.convenience_parameters = self.selectParametersFromProtocolParameterNames(
            ['width', 'height', 'intensity', 'angle', 'theta', 'closed_loop', 'opto_pre_time', 'opto_stim_time', 'opto_freq', 'opto_amp', 'opto_pulse_width'],
            randomize_order = self.protocol_parameters['randomize_order'])

        # Create epoch parameters dictionary
        if self.protocol_parameters['render_on_cylinder']:
            flystim_stim_name = 'MovingEllipseOnCylinder' if self.protocol_parameters['ellipse'] else 'MovingPatchOnCylinder'
            surface_dim_name = 'cylinder_radius'
        else:
            flystim_stim_name = 'MovingEllipse' if self.protocol_parameters['ellipse'] else 'MovingPatch'
            surface_dim_name = 'sphere_radius'
        self.epoch_parameters = {'name': flystim_stim_name,
                                 'width': self.convenience_parameters['current_width'],
                                 'height': self.convenience_parameters['current_height'],
                                 'color': self.convenience_parameters['current_intensity'],
                                 'theta': self.convenience_parameters['current_theta'],
                                 'angle': self.convenience_parameters['current_angle'],
                                 surface_dim_name: 1.0}

    def loadStimuli(self, client, multicall=None):

        if multicall is None:
            multicall = flyrpc.multicall.MyMultiCall(client.manager)

        conv_params_to_print = {k[8:]:v for k,v in self.convenience_parameters.items()}
        multicall.print_on_server(f'{conv_params_to_print}')

        # set up opto pulse wave
        multicall.daq_setupPulseWaveStreamOut(output_channel='DAC0',
                                              freq=self.convenience_parameters['current_opto_freq'],
                                              amp=self.convenience_parameters['current_opto_amp'],
                                              pulse_width=self.convenience_parameters['current_opto_pulse_width'],
                                              scanRate=5000)
        multicall.daq_streamWithTiming(pre_time=self.convenience_parameters['current_opto_pre_time'],
                                       stim_time=self.convenience_parameters['current_opto_stim_time'],
                                       scanRate=5000, scansPerRead=1000)

        super().loadStimuli(client, multicall)

    def getParameterDefaults(self):
        self.protocol_parameters = {'width': [25.0],
                                    'height': [15.0],
                                    'intensity': [0.0],
                                    'angle': [0.0],
                                    'theta': [-15.0, 15.0],
                                    'ellipse': False,
                                    'render_on_cylinder': True,
                                    'closed_loop': [0],
                                    'opto_pre_time': [0.0],
                                    'opto_stim_time': [1.0],
                                    'opto_freq_amp_pulsewidth_poissrate_': [1.0],
                                    'opto_params': {0: {'freq': 50.0,
                                                        'amp': 2.5,
                                                        'pulse_width': 0.1,
                                                        'prob': 1.0},
                                                    1: {'freq': 50.0,
                                                        'amp': 2.5,
                                                        'pulse_width': 0.1,
                                                        'prob': 1.0}
                                                   },
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'PatchFixation',
                               'num_epochs': 40,
                               'pre_time': 0.5,
                               'stim_time': 3.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}


#%%
class MovingPatch(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):

        # Select protocol parameters for this epoch
        self.convenience_parameters = self.selectParametersFromProtocolParameterNames(
            ['width', 'height', 'intensity', 'speed', 'angle', 'closed_loop'],
            randomize_order = self.protocol_parameters['randomize_order'])

        # Create flystim epoch parameters dictionary
        self.epoch_parameters = self.getMovingPatchParameters(angle=self.convenience_parameters['current_angle'],
                                                              speed=self.convenience_parameters['current_speed'],
                                                              width=self.convenience_parameters['current_width'],
                                                              height=self.convenience_parameters['current_height'],
                                                              color=self.convenience_parameters['current_intensity'])

    def loadStimuli(self, client, multicall=None):

        if multicall is None:
            multicall = flyrpc.multicall.MyMultiCall(client.manager)

        conv_params_to_print = {k[8:]:v for k,v in self.convenience_parameters.items()}
        multicall.print_on_server(f'{conv_params_to_print}')

        super().loadStimuli(client, multicall)

    def getParameterDefaults(self):
        self.protocol_parameters = {'ellipse': True,
                                    'width': [25.0],
                                    'height': [15.0],
                                    'intensity': [0.0],
                                    'center': [0, 0],
                                    'speed': [80.0],
                                    'angle': [0.0],

                                    'render_on_cylinder': True,
                                    'closed_loop': [0],

                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'MovingPatch',
                               'num_epochs': 40,
                               'pre_time': 0.5,
                               'stim_time': 3.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}


# %%
class MovingPatchWithOpto(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):

        # Select protocol parameters for this epoch
        self.convenience_parameters = self.selectParametersFromProtocolParameterNames(
            ['width', 'height', 'intensity', 'speed', 'angle', 'closed_loop', 'opto_pre_time', 'opto_stim_time', 'opto_freq', 'opto_amp', 'opto_pulse_width'],
            randomize_order = self.protocol_parameters['randomize_order'])

        # Create flystim epoch parameters dictionary
        self.epoch_parameters = self.getMovingPatchParameters(angle=self.convenience_parameters['current_angle'],
                                                              speed=self.convenience_parameters['current_speed'],
                                                              width=self.convenience_parameters['current_width'],
                                                              height=self.convenience_parameters['current_height'],
                                                              color=self.convenience_parameters['current_intensity'])

    def loadStimuli(self, client, multicall=None):

        if multicall is None:
            multicall = flyrpc.multicall.MyMultiCall(client.manager)

        conv_params_to_print = {k[8:]:v for k,v in self.convenience_parameters.items()}
        multicall.print_on_server(f'{conv_params_to_print}')

        # set up opto pulse wave
        multicall.daq_setupPulseWaveStreamOut(output_channel='DAC0',
                                              freq=self.convenience_parameters['current_opto_freq'],
                                              amp=self.convenience_parameters['current_opto_amp'],
                                              pulse_width=self.convenience_parameters['current_opto_pulse_width'],
                                              scanRate=5000)
        multicall.daq_streamWithTiming(pre_time=self.convenience_parameters['current_opto_pre_time'],
                                       stim_time=self.convenience_parameters['current_opto_stim_time'],
                                       scanRate=5000, scansPerRead=1000)

        super().loadStimuli(client, multicall)

    def getParameterDefaults(self):
        self.protocol_parameters = {'ellipse': True,
                                    'width': [25.0],
                                    'height': [15.0],
                                    'intensity': [0.0],
                                    'center': [0, 0],
                                    'speed': [80.0],
                                    'angle': [0.0],

                                    'render_on_cylinder': True,
                                    'closed_loop': [0],

                                    'opto_pre_time': [0.5],
                                    'opto_stim_time': [3.0],
                                    'opto_freq': [10.0],
                                    'opto_amp': [2.5],
                                    'opto_pulse_width': [0.05],

                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'MovingPatchWithOpto',
                               'num_epochs': 40,
                               'pre_time': 0.5,
                               'stim_time': 3.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}

# %%

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

class ExpandingEdges(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        # Select protocol parameters for this epoch
        if self.protocol_parameters['theta_offset_random']:
            self.convenience_parameters = self.selectParametersFromProtocolParameterNames(
                ['rate', 'expand_dark'],
                randomize_order = self.protocol_parameters['randomize_order'])
            self.convenience_parameters['current_theta_offset'] = np.random.uniform(0, 360)
        else:
            self.convenience_parameters = self.selectParametersFromProtocolParameterNames(
                ['rate', 'expand_dark', 'theta_offset'],
                randomize_order = self.protocol_parameters['randomize_order'])

        self.epoch_parameters = {'name': 'ExpandingEdges',
                                 'period': self.protocol_parameters['period'],
                                 'rate': self.convenience_parameters['current_rate'],
                                 'expander_color': self.protocol_parameters['dark_color'] if self.convenience_parameters['current_expand_dark'] else self.protocol_parameters['light_color'],
                                 'opposite_color': self.protocol_parameters['light_color'] if self.convenience_parameters['current_expand_dark'] else self.protocol_parameters['dark_color'],
                                 'width_0': self.protocol_parameters['width_0'],
                                 'hold_duration': self.protocol_parameters['hold_duration'],
                                 'color': [1, 1, 1, 1],
                                 'n_theta_pixels': self.protocol_parameters['n_theta_pixels'],
                                 'cylinder_radius': 1,
                                 'vert_extent': self.protocol_parameters['vert_extent'],
                                 'theta_offset': self.convenience_parameters['current_theta_offset'],
                                 'theta': self.screen_center[0]}

        self.meta_parameters = {'center': self.adjustCenter(self.protocol_parameters['center'])}

    def getParameterDefaults(self):
        self.protocol_parameters = {'period': 40.0,
                                    'rate': [-80.0, 80.0],
                                    'vert_extent': 80.0,
                                    'light_color': 1.0,
                                    'dark_color': 0.0,
                                    'expand_dark': [0,1],
                                    'width_0': 2,
                                    'hold_duration': 0.550,
                                    'n_theta_pixels': 5760,
                                    'center': [0, 0],
                                    'theta_offset': [0.0],
                                    'theta_offset_random': False,
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'ExpandingEdges',
                               'num_epochs': 400,
                               'pre_time': 1.0,
                               'stim_time': 0.800, # 0.550 hold then 0.250 rotate
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
        current_angle, current_height = self.selectParametersFromLists((self.protocol_parameters['angle'], self.protocol_parameters['height']), randomize_order = self.protocol_parameters['randomize_order'])

        center = self.adjustCenter(self.protocol_parameters['center'])
        centerX = center[0]
        centerY = center[1]

        height_in_radians = np.deg2rad(current_height)

        radius_in_meters = 1
        height_in_meters = 2 * radius_in_meters * np.tan(height_in_radians / 2)

        self.epoch_parameters = {'name': 'RotatingGrating',
                                 'period': self.protocol_parameters['period'],
                                 'rate': self.protocol_parameters['rate'],
                                 'hold_duration': self.protocol_parameters['hold_duration'],
                                 'color': [1, 1, 1, 1],
                                 'mean': self.protocol_parameters['mean'],
                                 'contrast': self.protocol_parameters['contrast'],
                                 'angle': current_angle,
                                 'offset': np.rad2deg(np.random.uniform(0, 2*np.pi)) if self.protocol_parameters['random_offset'] else 0,
                                 'cylinder_radius': radius_in_meters,
                                 'cylinder_height': height_in_meters,
                                 'profile': 'square',
                                 'theta': centerX,
                                 'phi': centerY}

        self.convenience_parameters = {'current_angle': current_angle, 'current_height': current_height}

        self.meta_parameters = {'center_size': self.protocol_parameters['center_size'],
                                'center': self.adjustCenter(self.protocol_parameters['center'])}

    def getParameterDefaults(self):
        self.protocol_parameters = {'period': 40.0,
                                    'rate': 80.0,
                                    'contrast': 1.0,
                                    'mean': 0.5,
                                    'angle': [0.0, 180.0],
                                    'height': [90.0],
                                    'hold_duration': 0.550,
                                    'center': [0, 0],
                                    'center_size': 180.0,
                                    'random_offset': False,
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'DriftingSquareGrating',
                               'num_epochs': 40,
                               'pre_time': 1.0,
                               'stim_time': 4.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}

# %%

class SplitDriftingSquareGrating(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def loadStimuli(self, client, multicall=None):
        passed_parameters_0 = self.epoch_parameters_0.copy()
        passed_parameters_1 = self.epoch_parameters_1.copy()

        bg = self.run_parameters.get('idle_color')
        if multicall is None:
            multicall = flyrpc.multicall.MyMultiCall(client.manager)
        multicall.load_stim(name='ConstantBackground', color=[bg,bg,bg,1], side_length=200)
        multicall.load_stim(**passed_parameters_0, hold=True)
        multicall.load_stim(**passed_parameters_1, hold=True)
        multicall()

    def getEpochParameters(self):
        # TODO: center size with aperture (center and center_size)
        current_angle = self.selectParametersFromLists(self.protocol_parameters['angle'], randomize_order = self.protocol_parameters['randomize_order'])

        offset = np.rad2deg(np.random.uniform(0, 2*np.pi)) if self.protocol_parameters['random_offset'] else 0

        self.epoch_parameters_0 = {'name': 'RotatingGrating',
                                 'period': self.protocol_parameters['period'],
                                 'rate': self.protocol_parameters['rate'],
                                 'color': [1, 1, 1, 1],
                                 'mean': self.protocol_parameters['mean'],
                                 'contrast': self.protocol_parameters['contrast'],
                                 'angle': current_angle,
                                 'offset': offset,
                                 'cylinder_radius': 1,
                                 'cylinder_location': (self.protocol_parameters['cylinder_xshift'],0,0),
                                 'cylinder_height': 10,
                                 'profile': 'square',
                                 'theta': self.screen_center[0]}
        self.epoch_parameters_1 = {'name': 'RotatingGrating',
                                 'period': self.protocol_parameters['period'],
                                 'rate': self.protocol_parameters['rate'], #-
                                 'color': [1, 1, 1, 1],
                                 'mean': self.protocol_parameters['mean'],
                                 'contrast': self.protocol_parameters['contrast'],
                                 'angle': current_angle+180.0, #remove
                                 'offset': offset,
                                 'cylinder_radius': 1,
                                 'cylinder_location': (self.protocol_parameters['cylinder_xshift'],0,0), #-
                                 'cylinder_height': 10,
                                 'profile': 'square',
                                 'theta': self.screen_center[0]}
        # self.epoch_parameters_1 = self.epoch_parameters_0.copy()
        # self.epoch_parameters_1['cylinder_location'] = (-self.protocol_parameters['cylinder_xshift'],0,0)


        self.convenience_parameters = {'current_angle': current_angle}

        self.meta_parameters = {'center_size': self.protocol_parameters['center_size'],
                                'center': self.adjustCenter(self.protocol_parameters['center'])}

    def getParameterDefaults(self):
        self.protocol_parameters = {'period': 20.0,
                                    'rate': 20.0,
                                    'contrast': 1.0,
                                    'mean': 0.5,
                                    'angle': [0.0, 180.0],
                                    'center': [0, 0],
                                    'center_size': 180.0,
                                    'cylinder_xshift': -0.001,
                                    'random_offset': False,
                                    'randomize_order': True,
                                    }

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'SplitDriftingSquareGrating',
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

        self.epoch_parameters = self.getMovingPatchParameters(width=current_diameter,
                                                              height=current_diameter,
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
                               'stim_time': 3.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}

# %%

class FlickeringVertBars(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        current_angle, current_temporal_frequency, current_theta = self.selectParametersFromLists((self.protocol_parameters['angle'], self.protocol_parameters['temporal_frequency'], self.protocol_parameters['theta']), randomize_order=self.protocol_parameters['randomize_order'])

        center = self.adjustCenter(self.protocol_parameters['center'])
        centerX = center[0]
        centerY = center[1]

        # make color trajectory
        color_traj = {'name': 'Sinusoid',
                      'temporal_frequency': current_temporal_frequency,
                      'amplitude': self.protocol_parameters['mean'] * self.protocol_parameters['contrast'],
                      'offset': self.protocol_parameters['mean']}

        if self.protocol_parameters['render_on_cylinder']:
            self.epoch_parameters = {'name': 'MovingPatchOnCylinder',
                                    'width': self.protocol_parameters['width'],
                                    'height': self.protocol_parameters['height'],
                                    'cylinder_radius': 1,
                                    'color': color_traj,
                                    'theta': centerX + current_theta,
                                    'phi': centerY + self.protocol_parameters['phi'],
                                    'angle': current_angle}
        else:
            self.epoch_parameters = {'name': 'MovingPatch',
                                    'width': self.protocol_parameters['width'],
                                    'height': self.protocol_parameters['height'],
                                    'sphere_radius': 1,
                                    'color': color_traj,
                                    'theta': centerX + current_theta,
                                    'phi': centerY + self.protocol_parameters['phi'],
                                    'angle': current_angle}

        self.convenience_parameters = {'current_angle': current_angle,
                                       'current_temporal_frequency': current_temporal_frequency,
                                       'current_theta': current_theta}

    def loadStimuli(self, client, multicall=None):
        bg = self.run_parameters.get('idle_color')
        if multicall is None:
            multicall = flyrpc.multicall.MyMultiCall(client.manager)
        multicall.set_global_theta_offset(self.protocol_parameters['fly_heading'])
        multicall.load_stim('ConstantBackground', color=[bg, bg, bg, 1.0])

        passedParameters = self.epoch_parameters.copy()
        multicall.load_stim(**passedParameters, hold=True)
        multicall()

    def getParameterDefaults(self):
        self.protocol_parameters = {'center': [0.0, 0.0],
                                    'angle': [0.0],
                                    'height': 150.0,
                                    'width': 10.0,
                                    'theta': [0.0, 10.0],
                                    'phi': 0,
                                    'contrast': 1.0,
                                    'mean': 0.5,
                                    'temporal_frequency': [10.0],
                                    'render_on_cylinder': True,
                                    'fly_heading': 0.0,
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'FlickeringVertBars',
                               'num_epochs': 30,
                               'pre_time': 1.0,
                               'stim_time': 4.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}

# %%

class FlickeringPatch(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        current_temporal_frequency, current_center = self.selectParametersFromLists((self.protocol_parameters['temporal_frequency'], self.protocol_parameters['center']), randomize_order=self.protocol_parameters['randomize_order'])

        adj_center = self.adjustCenter(current_center)

        # make color trajectory
        color_traj = {'name': 'Sinusoid',
                      'temporal_frequency': current_temporal_frequency,
                      'amplitude': self.protocol_parameters['mean'] * self.protocol_parameters['contrast'],
                      'offset': self.protocol_parameters['mean']}

        if self.protocol_parameters['render_on_cylinder']:
            self.epoch_parameters = {'name': 'MovingPatchOnCylinder',
                                    'width': self.protocol_parameters['width'],
                                    'height': self.protocol_parameters['height'],
                                    'cylinder_radius': 1,
                                    'color': color_traj,
                                    'theta': adj_center[0],
                                    'phi': adj_center[1],
                                    'angle': 0}
        else:
            self.epoch_parameters = {'name': 'MovingPatch',
                                    'width': self.protocol_parameters['width'],
                                    'height': self.protocol_parameters['height'],
                                    'sphere_radius': 1,
                                    'color': color_traj,
                                    'theta': adj_center[0],
                                    'phi': adj_center[1],
                                    'angle': 0}

        self.convenience_parameters = {'current_temporal_frequency': current_temporal_frequency,
                                       'current_center': current_center}

    def getParameterDefaults(self):
        self.protocol_parameters = {'height': 10.0,
                                    'width': 10.0,
                                    'center': [[0,0], [10,0]],
                                    'contrast': 1.0,
                                    'mean': 0.5,
                                    'temporal_frequency': [10.0],
                                    'render_on_cylinder': False,
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
        current_spot_speed, current_grate_rate = self.selectParametersFromLists((self.protocol_parameters['spot_speed'], self.protocol_parameters['grate_rate']),
                                                                                 all_combinations = True,
                                                                                 randomize_order = self.protocol_parameters['randomize_order'])

        patch_parameters = self.getMovingPatchParameters(speed = current_spot_speed,
                                                        width = self.protocol_parameters['spot_radius']*2,
                                                        height = self.protocol_parameters['spot_radius']*2,
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

    def loadStimuli(self, client, multicall=None):
        grate_parameters = self.epoch_parameters[0].copy()
        patch_parameters = self.epoch_parameters[1].copy()

        bg = self.run_parameters.get('idle_color')
        if multicall is None:
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

        patch_parameters = self.getMovingPatchParameters(speed=current_spot_speed,
                                                         width=self.protocol_parameters['spot_radius'] * 2,
                                                         height=self.protocol_parameters['spot_radius'] * 2,
                                                         color=self.protocol_parameters['spot_color'],
                                                         distance_to_travel=180)

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

    def loadStimuli(self, client, multicall=None):
        grate_parameters = self.epoch_parameters[0].copy()
        patch_parameters = self.epoch_parameters[1].copy()

        bg = self.run_parameters.get('idle_color')
        if multicall is None:
            multicall = flyrpc.multicall.MyMultiCall(client.manager)
        multicall.load_stim(**grate_parameters, hold=True)
        multicall.load_stim(**patch_parameters, hold=True)
        multicall()

    def getParameterDefaults(self):
        self.protocol_parameters = {'center': [0, 0],
                                    'spot_radius': 7.5,
                                    'spot_color': 0.0,
                                    'spot_speed': [60.0],
                                    'grate_period': [10.0, 20.0, 30.0, 40.0],
                                    'grate_rate': [-120.0, -90.0, -60.0, -30.0, -15.0, 0.0,
                                                   15.0, 30.0, 60.0, 90.0, 120.0],
                                    'grate_contrast': 0.5,
                                    'angle': 0.0,
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'SurroundGratingTuning',
                               'num_epochs': 220, # 11 x 5 avgs each
                               'pre_time': 1.0,
                               'stim_time': 3.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}

# %%

class TernaryBars(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        current_period, current_theta_offset, current_angle = self.selectParametersFromLists((self.protocol_parameters['period'], self.protocol_parameters['theta_offset'], self.protocol_parameters['angle']), randomize_order=self.protocol_parameters['randomize_order'])
        start_seed = int(np.random.choice(range(int(1e6))))

        distribution_data = {'name': 'Ternary',
                             'args': [],
                             'kwargs': {'rand_min': self.protocol_parameters['rand_min'],
                                        'rand_max': self.protocol_parameters['rand_max']}}
        if self.protocol_parameters['render_on_cylinder']:
            self.epoch_parameters = {'name': 'RandomBars',
                                    'period': current_period,
                                    'width': current_period,
                                    'vert_extent': self.protocol_parameters['vert_extent'],
                                    'theta_offset': current_theta_offset,
                                    'background': 0.0,
                                    'update_rate': self.protocol_parameters['update_rate'],
                                    'angle': current_angle,
                                    'start_seed': start_seed,
                                    'distribution_data': distribution_data}
        else:
            self.epoch_parameters = {'name': 'RandomGridOnSphericalPatch',
                                    'patch_width': current_period,
                                    'patch_height': self.protocol_parameters['vert_extent'],
                                    'height': self.protocol_parameters['vert_extent'],
                                    'width': self.protocol_parameters['horiz_extent'],
                                    'theta': current_theta_offset,
                                    'phi': 0,
                                    'angle': current_angle,
                                    'n_steps_x': 16,
                                    'n_steps_y': 14,
                                    'update_rate': self.protocol_parameters['update_rate'],
                                    'start_seed': start_seed,
                                    'distribution_data': distribution_data}


        self.convenience_parameters = {'start_seed': start_seed,
                                       'current_period': current_period,
                                       'current_theta_offset': current_theta_offset,
                                       'current_angle': current_angle}

    def loadStimuli(self, client, multicall=None):
        bg = self.run_parameters.get('idle_color')
        if multicall is None:
            multicall = flyrpc.multicall.MyMultiCall(client.manager)
        multicall.set_global_theta_offset(self.protocol_parameters['fly_heading'])
        multicall.load_stim('ConstantBackground', color=[bg, bg, bg, 1.0])

        passedParameters = self.epoch_parameters.copy()
        multicall.load_stim(**passedParameters, hold=True)
        multicall()

    def getParameterDefaults(self):
        self.protocol_parameters = {'period': [5.0],
                                    'vert_extent': 90.0,
                                    'horiz_extent': 180.0,
                                    'theta_offset': [0.0],
                                    # 'background': 0.0,
                                    'rand_min': 0.0,
                                    'rand_max': 1.0,
                                    'update_rate': 4.0,
                                    'angle': [0.0],
                                    'fly_heading': 0.0,
                                    'render_on_cylinder': True,
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'TernaryBars',
                               'num_epochs': 40,
                               'pre_time': 0.5,
                               'stim_time': 3.0,
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
