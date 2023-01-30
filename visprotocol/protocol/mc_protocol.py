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

    def getMovingPatchParameters(self, center=None, angle=None, speed=None, width=None, height=None, color=None, distance_to_travel=None, render_on_cylinder=None):
        if center is None: center = self.adjustCenter(self.protocol_parameters['center'])
        if angle is None: angle = self.protocol_parameters['angle']
        if speed is None: speed = self.protocol_parameters['speed']
        if width is None: width = self.protocol_parameters['width']
        if height is None: height = self.protocol_parameters['height']
        if color is None: color = self.protocol_parameters['color']
        if render_on_cylinder is None: render_on_cylinder = self.protocol_parameters['render_on_cylinder']

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

        patch_parameters = {'name': 'MovingPatchOnCylinder' if render_on_cylinder else 'MovingPatch',
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

    def getOcclusionWithPauseParameters(self, center=None, start_theta=None, bar_width=None, bar_height=None, bar_prime_color=None, bar_probe_color=None, bar_speed=None, occluder_height=None, occluder_color=None,
                                        preprime_duration=None, prime_duration=None, occlusion_duration=None, pause_duration=None, probe_duration=None, render_on_cylinder=None, bar_surface_radius=None, occluder_surface_radius=None):
        if center is None: center = self.adjustCenter(self.protocol_parameters['center'])
        if start_theta is None: start_theta = self.protocol_parameters['start_theta'] #negative value starts from the opposite side of bar direction
        if bar_width is None: bar_width = self.protocol_parameters['bar_width']
        if bar_height is None: bar_height = self.protocol_parameters['bar_height']
        if bar_prime_color is None: bar_prime_color = self.protocol_parameters['bar_prime_color']
        if bar_probe_color is None: bar_probe_color = self.protocol_parameters['bar_probe_color']
        if bar_speed is None: bar_speed = self.protocol_parameters['bar_speed']
        if occluder_height is None: occluder_height = self.protocol_parameters['occluder_height']
        if occluder_color is None: occluder_color = self.protocol_parameters['occluder_color']
        if preprime_duration is None: preprime_duration = self.protocol_parameters['preprime_duration']
        if prime_duration is None: prime_duration = self.protocol_parameters['prime_duration']
        if occlusion_duration is None: occlusion_duration = self.protocol_parameters['occlusion_duration']
        if pause_duration is None: pause_duration = self.protocol_parameters['pause_duration']
        if probe_duration is None: probe_duration = self.protocol_parameters['probe_duration']
        if render_on_cylinder is None: render_on_cylinder = self.protocol_parameters['render_on_cylinder']
        if bar_surface_radius is None: bar_surface_radius = self.protocol_parameters['bar_surface_radius']
        if occluder_surface_radius is None: occluder_surface_radius = self.protocol_parameters['occluder_surface_radius']

        centerX = center[0]

        # Stimulus construction

        stim_duration = preprime_duration + prime_duration + occlusion_duration + probe_duration + pause_duration

        # consistent bar trajectory
        start_theta *= np.sign(bar_speed)
        time = [0, preprime_duration]
        x = [start_theta, start_theta]
        bar_color = [bar_prime_color, bar_prime_color]

        prime_movement = bar_speed * (prime_duration + occlusion_duration)
        prime_end_theta = start_theta + prime_movement
        prime_end_time = preprime_duration + prime_duration + occlusion_duration

        time.append(prime_end_time)
        x.append(prime_end_theta)
        bar_color.append(bar_prime_color)

        pause_end_theta = prime_end_theta
        pause_end_time = prime_end_time + pause_duration

        time.append(pause_end_time)
        x.append(pause_end_theta)
        bar_color.append(bar_probe_color)

        probe_movement = bar_speed * probe_duration
        probe_end_theta = pause_end_theta + probe_movement
        probe_end_time = pause_end_time + probe_duration

        time.append(probe_end_time)
        x.append(probe_end_theta)
        bar_color.append(bar_probe_color)

        # Compute location and width of the occluder per specification
        occlusion_start_theta = start_theta + bar_speed * prime_duration
        occluder_width = np.abs(bar_speed) * occlusion_duration + bar_width # the last term ensures that the bar is completely hidden during the occlusion period
        occluder_loc = occlusion_start_theta + np.sign(bar_speed) * (occluder_width/2 - bar_width/2) # the last two terms account for widths of the bar and the occluder, such that the bar is completely hidden during occlusion period
        occluder_time = [0, stim_duration]
        occluder_x = [occluder_loc, occluder_loc]

        # bar_traj_r = list(zip(time, (centerX - np.array(x)).tolist()))
        # occluder_traj_r = list(zip(occluder_time, (centerX - np.array(occluder_x)).tolist()))
        # bar_traj_l = list(zip(time, (centerX + np.array(x)).tolist()))
        # occluder_traj_l = list(zip(occluder_time, (centerX + np.array(occluder_x)).tolist()))

        # Create flystim trajectory objects
        bar_theta_traj      = {'name': 'tv_pairs', 'tv_pairs': list(zip(time, (centerX + np.array(x)).tolist())),                   'kind': 'linear'}
        bar_color_traj      = {'name': 'tv_pairs', 'tv_pairs': list(zip(time, bar_color)), 'kind': 'linear'}
        occluder_theta_traj = {'name': 'tv_pairs', 'tv_pairs': list(zip(occluder_time, (centerX + np.array(occluder_x)).tolist())), 'kind': 'linear'}

        if render_on_cylinder:
            bar_parameters = {'name': 'MovingPatchOnCylinder',
                                'width': bar_width,
                                'height': bar_height,
                                'color': bar_color_traj,
                                'theta': bar_theta_traj,
                                'phi': 0,
                                'angle': 0,
                                'cylinder_radius': bar_surface_radius}
            occluder_parameters = {'name': 'MovingPatchOnCylinder',
                                'width': occluder_width,
                                'height': occluder_height,
                                'color': occluder_color,
                                'theta': occluder_theta_traj,
                                'phi': 0,
                                'angle': 0,
                                'cylinder_radius': occluder_surface_radius}
        else:
            bar_parameters = {'name': 'MovingPatch',
                                'width': bar_width,
                                'height': bar_height,
                                'color': bar_color_traj,
                                'theta': bar_theta_traj,
                                'phi': 0,
                                'angle': 0,
                                'sphere_radius': bar_surface_radius}
            occluder_parameters = {'name': 'MovingPatch',
                                'width': occluder_width,
                                'height': occluder_height,
                                'color': occluder_color,
                                'theta': occluder_theta_traj,
                                'phi': 0,
                                'angle': 0,
                                'sphere_radius': occluder_surface_radius}

        return bar_parameters, occluder_parameters, stim_duration

# %%

    def getOcclusionFixedParameters(self, center=None, bar_start_theta=None, bar_end_theta=None, bar_width=None, bar_height=None,
                                    bar_prime_color=None, bar_probe_color=None, bar_speed=None,
                                    occluder_theta=None, occluder_width=None, occluder_height=None, occluder_color=None,
                                    preprime_duration=None, pause_duration=None, render_on_cylinder=None,
                                    bar_surface_radius=None, occluder_surface_radius=None, angle=None):
        if center is None: center = self.adjustCenter(self.protocol_parameters['center'])
        if angle is None: angle = self.protocol_parameters['angle']
        if bar_start_theta is None: bar_start_theta = self.protocol_parameters['bar_start_theta'] #negative value starts from the opposite side of bar direction
        if bar_end_theta is None: bar_end_theta = self.protocol_parameters['bar_end_theta'] #negative value starts from the opposite side of bar direction
        if bar_width is None: bar_width = self.protocol_parameters['bar_width']
        if bar_height is None: bar_height = self.protocol_parameters['bar_height']
        if bar_prime_color is None: bar_prime_color = self.protocol_parameters['bar_prime_color']
        if bar_probe_color is None: bar_probe_color = self.protocol_parameters['bar_probe_color']
        if bar_speed is None: bar_speed = self.protocol_parameters['bar_speed']
        if occluder_theta is None: occluder_theta = self.protocol_parameters['occluder_theta']
        if occluder_width is None: occluder_width = self.protocol_parameters['occluder_width']
        if occluder_height is None: occluder_height = self.protocol_parameters['occluder_height']
        if occluder_color is None: occluder_color = self.protocol_parameters['occluder_color']
        if preprime_duration is None: preprime_duration = self.protocol_parameters['preprime_duration']
        if pause_duration is None: pause_duration = self.protocol_parameters['pause_duration']
        if render_on_cylinder is None: render_on_cylinder = self.protocol_parameters['render_on_cylinder']
        if bar_surface_radius is None: bar_surface_radius = self.protocol_parameters['bar_surface_radius']
        if occluder_surface_radius is None: occluder_surface_radius = self.protocol_parameters['occluder_surface_radius']

        centerX = center[0]

        # Stimulus construction

        bar_start_theta *= np.sign(bar_speed)
        bar_end_theta *= np.sign(bar_speed)
        occluder_theta *= np.sign(bar_speed)


        # Bar
        theta_distance = np.abs(bar_end_theta - bar_start_theta)
        prime_distance = np.abs(occluder_theta - bar_start_theta)
        prime_duration = prime_distance / np.abs(bar_speed)
        probe_distance = np.abs(bar_end_theta - occluder_theta)
        probe_duration = probe_distance / np.abs(bar_speed)
        bar_duration_wo_pause = theta_distance / np.abs(bar_speed)
        bar_duration_w_pause = bar_duration_wo_pause + pause_duration
        stim_duration = preprime_duration + bar_duration_w_pause

        # Bar trajectory
        time =       [0,
                      preprime_duration,
                      preprime_duration+prime_duration,
                      preprime_duration+prime_duration+pause_duration,
                      stim_duration]
        x =          [bar_start_theta,
                      bar_start_theta,
                      occluder_theta,
                      occluder_theta,
                      bar_end_theta]
        bar_color =  [bar_prime_color,
                      bar_prime_color,
                      bar_prime_color,
                      bar_probe_color,
                      bar_probe_color]

        # Occluder trajectory
        occluder_time = [0, stim_duration]
        occluder_x = [occluder_theta, occluder_theta]

        # Create flystim trajectory objects
        bar_theta_traj      = {'name': 'tv_pairs', 'tv_pairs': list(zip(time, (centerX + np.array(x)).tolist())), 'kind': 'linear'}
        bar_color_traj      = {'name': 'tv_pairs', 'tv_pairs': list(zip(time, bar_color)), 'kind': 'previous'}
        occluder_theta_traj = {'name': 'tv_pairs', 'tv_pairs': list(zip(occluder_time, (centerX + np.array(occluder_x)).tolist())), 'kind': 'linear'}

        if render_on_cylinder:
            bar_parameters = {'name': 'MovingPatchOnCylinder',
                                'width': bar_width,
                                'height': bar_height,
                                'color': bar_color_traj,
                                'theta': bar_theta_traj,
                                'phi': 0,
                                'angle': angle,
                                'cylinder_radius': bar_surface_radius}
            occluder_parameters = {'name': 'MovingPatchOnCylinder',
                                'width': occluder_width,
                                'height': occluder_height,
                                'color': occluder_color,
                                'theta': occluder_theta_traj,
                                'phi': 0,
                                'angle': angle,
                                'cylinder_radius': occluder_surface_radius}
        else:
            bar_parameters = {'name': 'MovingPatch',
                                'width': bar_width,
                                'height': bar_height,
                                'color': bar_color_traj,
                                'theta': bar_theta_traj,
                                'phi': 0,
                                'angle': angle,
                                'sphere_radius': bar_surface_radius}
            occluder_parameters = {'name': 'MovingPatch',
                                'width': occluder_width,
                                'height': occluder_height,
                                'color': occluder_color,
                                'theta': occluder_theta_traj,
                                'phi': 0,
                                'angle': angle,
                                'sphere_radius': occluder_surface_radius}

        return bar_parameters, occluder_parameters, stim_duration

# %%

"""
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # FLY-CENTERED STIMS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""

class OcclusionWithPause(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        current_bar_width, current_bar_prime_color, current_bar_probe_color, current_bar_speed, current_occluder_color, current_occlusion_duration, current_pause_duration = self.selectParametersFromLists((self.protocol_parameters['bar_width'], self.protocol_parameters['bar_prime_color'], self.protocol_parameters['bar_probe_color'], self.protocol_parameters['bar_speed'], self.protocol_parameters['occluder_color'], self.protocol_parameters['occlusion_duration'], self.protocol_parameters['pause_duration']), randomize_order=self.protocol_parameters['randomize_order'])

        bar_parameters, occluder_parameters, stim_duration = self.getOcclusionWithPauseParameters(bar_width=current_bar_width, bar_prime_color=current_bar_prime_color, bar_probe_color=current_bar_probe_color, bar_speed=current_bar_speed, occluder_color=current_occluder_color, occlusion_duration=current_occlusion_duration, pause_duration=current_pause_duration)
        self.epoch_parameters = (bar_parameters, occluder_parameters)

        self.convenience_parameters = {'current_bar_width': current_bar_width,
                                       'current_bar_prime_color': current_bar_prime_color,
                                       'current_bar_probe_color': current_bar_probe_color,
                                       'current_bar_speed': current_bar_speed,
                                       'current_occluder_color': current_occluder_color,
                                       'current_occlusion_duration': current_occlusion_duration,
                                       'current_pause_duration': current_pause_duration,
                                       'current_stim_duration': stim_duration}

    def loadStimuli(self, client, multicall=None):
        self.run_parameters['stim_time'] = self.convenience_parameters['current_stim_duration']

        bg = self.run_parameters.get('idle_color')
        if multicall is None:
            multicall = flyrpc.multicall.MyMultiCall(client.manager)
        multicall.load_stim(name='ConstantBackground', color=[bg,bg,bg,1], side_length=200)
        for ep in self.epoch_parameters:
            multicall.load_stim(**ep.copy(), hold=True)
        multicall.print_on_server(str({k[8:]:v for k,v in self.convenience_parameters.items()}))
        multicall()

    def getParameterDefaults(self):
        self.protocol_parameters = {'center': [0, 0],
                                    'start_theta': -90.0,
                                    'bar_width': 15.0,
                                    'bar_height': 150.0,
                                    'bar_prime_color': [1.0, 0.0],
                                    'bar_probe_color': 1.0,
                                    'bar_speed': [-35.0, -25.0, -15.0, 15.0, 25.0, 35.0],
                                    'occluder_height': 170.0,
                                    'occluder_color': self.run_parameters.get('idle_color'),
                                    'preprime_duration': 0.0,
                                    'prime_duration': 2.0,
                                    'occlusion_duration': [0.5, 2.0],
                                    'pause_duration': [0.0, 1.0],
                                    'probe_duration': 1.5,
                                    'render_on_cylinder': False,
                                    'bar_surface_radius': 3.0,
                                    'occluder_surface_radius': 2.0,
                                    'randomize_order': True,}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'OcclusionWithPause',
                               'num_epochs': 240, # 12 x 20 each
                               'pre_time': 1.0,
                               'tail_time': 1.0,
                               'idle_color': 0.0}

# %%

class OcclusionFixed(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        current_angle, current_bar_start_theta, current_bar_width, current_bar_prime_color, current_bar_probe_color, current_bar_speed, current_occluder_color, current_pause_duration, current_closed_loop = self.selectParametersFromLists((self.protocol_parameters['angle'],self.protocol_parameters['bar_start_theta'],self.protocol_parameters['bar_width'], self.protocol_parameters['bar_prime_color'], self.protocol_parameters['bar_probe_color'], self.protocol_parameters['bar_speed'], self.protocol_parameters['occluder_color'],  self.protocol_parameters['pause_duration'],  self.protocol_parameters['closed_loop']), randomize_order=self.protocol_parameters['randomize_order'])

        bar_parameters, occluder_parameters, stim_duration = self.getOcclusionFixedParameters(bar_start_theta=current_bar_start_theta, bar_width=current_bar_width, bar_prime_color=current_bar_prime_color, bar_probe_color=current_bar_probe_color, bar_speed=current_bar_speed, occluder_color=current_occluder_color, pause_duration=current_pause_duration, angle=current_angle)
        self.epoch_parameters = [bar_parameters, occluder_parameters]

        self.convenience_parameters = {'current_angle': current_angle,
                                       'current_bar_width': current_bar_width,
                                       'current_bar_prime_color': current_bar_prime_color,
                                       'current_bar_probe_color': current_bar_probe_color,
                                       'current_bar_speed': current_bar_speed,
                                       'current_occluder_color': current_occluder_color,
                                       'current_pause_duration': current_pause_duration,
                                       'current_closed_loop': current_closed_loop,
                                       'current_stim_duration': stim_duration}

    def loadStimuli(self, client, multicall=None):
        self.run_parameters['stim_time'] = self.convenience_parameters['current_stim_duration']

        bg = self.run_parameters.get('idle_color')
        if multicall is None:
            multicall = flyrpc.multicall.MyMultiCall(client.manager)
        multicall.set_global_theta_offset(self.protocol_parameters['fly_heading'])
        multicall.load_stim(name='ConstantBackground', color=[bg,bg,bg,1], side_length=200)
        for ep in self.epoch_parameters:
            multicall.load_stim(**ep.copy(), hold=True)
        multicall.print_on_server(str({k[8:]:v for k,v in self.convenience_parameters.items()}))
        multicall()

    def startStimuli(self, client, append_stim_frames=False, print_profile=True):
        sleep(self.run_parameters['pre_time'])
        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        # Fictrac
        if self.cfg['do_loco']:
            if self.convenience_parameters['current_closed_loop']:
                multicall.loco_set_pos_0(theta_0=None, x_0=0, y_0=0, use_data_prev=True)
                multicall.loco_loop_update_closed_loop_vars(update_theta=True, update_x=False, update_y=False)
                multicall.loco_loop_start_closed_loop()
        # stim time
        multicall.start_stim(append_stim_frames=append_stim_frames)
        multicall.start_corner_square()
        multicall()

        sleep(self.convenience_parameters['current_stim_duration'])

        # tail time
        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        multicall.stop_stim(print_profile=print_profile)
        multicall.black_corner_square()
        # Fictrac
        if self.cfg['do_loco']:
            multicall.loco_loop_stop_closed_loop()
        multicall()

        sleep(self.run_parameters['tail_time'])

    def getParameterDefaults(self):
        self.protocol_parameters = {'center': [0, 0],
                                    'angle': [0.0],
                                    'closed_loop': [0],
                                    'bar_start_theta': [90.0],
                                    'bar_end_theta': 0.0,
                                    'bar_width': 15.0,
                                    'bar_height': 50.0,
                                    'bar_prime_color': [1.0],
                                    'bar_probe_color': 1.0,
                                    'bar_speed': [15.0, -15.0],
                                    'occluder_theta': 60.0,
                                    'occluder_width': 30.0,
                                    'occluder_height': 170.0,
                                    'occluder_color': [0.0],
                                    'preprime_duration': 0.0,
                                    'pause_duration': [0.0],
                                    'render_on_cylinder': True,
                                    'bar_surface_radius': 3.0,
                                    'occluder_surface_radius': 2.0,
                                    'fly_heading': 0.0,
                                    'randomize_order': True,}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'OcclusionFixed',
                               'num_epochs': 240, # 12 x 20 each
                               'pre_time': 1.0,
                               'tail_time': 1.0,
                               'idle_color': 0.0}

# %%

class StripeFixation(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        current_width, current_height, current_intensity, current_angle, current_theta, current_closed_loop = self.selectParametersFromLists((self.protocol_parameters['width'], self.protocol_parameters['height'], self.protocol_parameters['intensity'], self.protocol_parameters['angle'], self.protocol_parameters['theta'], self.protocol_parameters['closed_loop']), randomize_order=self.protocol_parameters['randomize_order'])

        self.convenience_parameters = {'current_width': current_width,
                                       'current_height': current_height,
                                       'current_angle': current_angle,
                                       'current_intensity': current_intensity,
                                       'current_theta': current_theta,
                                       'current_closed_loop': current_closed_loop}

        self.epoch_parameters = {'name': 'MovingPatchOnCylinder' if self.protocol_parameters['render_on_cylinder'] else 'MovingPatch',
                            'width': current_width,
                            'height': current_height,
                            'color': current_intensity,
                            'theta': current_theta,
                            'angle': current_angle}

    def loadStimuli(self, client, multicall=None):
        if multicall is None:
            multicall = flyrpc.multicall.MyMultiCall(client.manager)

        multicall.print_on_server(f'Epoch {self.convenience_parameters}')

        bg = self.run_parameters.get('idle_color')
        multicall.load_stim('ConstantBackground', color=[bg, bg, bg, 1.0])

        if isinstance(self.epoch_parameters, list):
            for ep in self.epoch_parameters:
                multicall.load_stim(**ep.copy(), hold=True)
        else:
            multicall.load_stim(**self.epoch_parameters.copy(), hold=True)

        multicall()

    def getParameterDefaults(self):
        self.protocol_parameters = {'width': [5.0],
                                    'height': [50.0],
                                    'intensity': [0.0, 1.0],
                                    'angle': [0.0],
                                    'theta': [0.0],
                                    'closed_loop': [0],
                                    'render_on_cylinder': True,
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'StripeFixation',
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
        current_rate, current_expand_dark = self.selectParametersFromLists((self.protocol_parameters['rate'], self.protocol_parameters['expand_dark']), randomize_order = self.protocol_parameters['randomize_order'])


        self.epoch_parameters = {'name': 'ExpandingEdges',
                                 'period': self.protocol_parameters['period'],
                                 'rate': current_rate,
                                 'expander_color': self.protocol_parameters['dark_color'] if current_expand_dark else self.protocol_parameters['light_color'],
                                 'opposite_color': self.protocol_parameters['light_color'] if current_expand_dark else self.protocol_parameters['dark_color'],
                                 'width_0': self.protocol_parameters['width_0'],
                                 'hold_duration': self.protocol_parameters['hold_duration'],
                                 'color': [1, 1, 1, 1],
                                 'n_theta_pixels': self.protocol_parameters['n_theta_pixels'],
                                 'cylinder_radius': 1,
                                 'vert_extent': self.protocol_parameters['vert_extent'],
                                 'theta_offset': self.protocol_parameters['theta_offset'],
                                 'theta': self.screen_center[0]}

        self.convenience_parameters = {'current_rate': current_rate, 'current_expand_dark': current_expand_dark}

        self.meta_parameters = {'center': self.adjustCenter(self.protocol_parameters['center'])}

    def getParameterDefaults(self):
        self.protocol_parameters = {'period': 40.0,
                                    'rate': [-80.0, 80.0],
                                    'vert_extent': 80.0,
                                    'theta_offset': 0.0,
                                    'light_color': 1.0,
                                    'dark_color': 0.0,
                                    'expand_dark': [0,1],
                                    'width_0': 2,
                                    'hold_duration': 0.550,
                                    'n_theta_pixels': 5760,
                                    'center': [0, 0],
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
        current_angle = self.selectParametersFromLists(self.protocol_parameters['angle'], randomize_order = self.protocol_parameters['randomize_order'])

        self.epoch_parameters = {'name': 'RotatingGrating',
                                 'period': self.protocol_parameters['period'],
                                 'rate': self.protocol_parameters['rate'],
                                 'hold_duration': self.protocol_parameters['hold_duration'],
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
        self.protocol_parameters = {'period': 40.0,
                                    'rate': 80.0,
                                    'contrast': 1.0,
                                    'mean': 0.5,
                                    'angle': [0.0, 180.0],
                                    'hold_duration': 0.550,
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

        self.epoch_parameters_0 = {'name': 'RotatingGrating',
                                 'period': self.protocol_parameters['period'],
                                 'rate': self.protocol_parameters['rate'],
                                 'color': [1, 1, 1, 1],
                                 'mean': self.protocol_parameters['mean'],
                                 'contrast': self.protocol_parameters['contrast'],
                                 'angle': current_angle,
                                 'offset': 0.0,
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
                                 'offset': 0.0, #change this??
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
        current_angle, current_temporal_frequency, current_theta_loc = self.selectParametersFromLists((self.protocol_parameters['angle'], self.protocol_parameters['temporal_frequency'], self.protocol_parameters['theta_loc']), randomize_order=self.protocol_parameters['randomize_order'])

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
                                    'theta': current_theta_loc,
                                    'phi': self.protocol_parameters['phi_loc'],
                                    'angle': current_angle}
        else:
            self.epoch_parameters = {'name': 'MovingPatch',
                                    'width': self.protocol_parameters['width'],
                                    'height': self.protocol_parameters['height'],
                                    'sphere_radius': 1,
                                    'color': color_traj,
                                    'theta': current_theta_loc,
                                    'phi': self.protocol_parameters['phi_loc'],
                                    'angle': current_angle}

        self.convenience_parameters = {'current_angle': current_angle,
                                       'current_temporal_frequency': current_temporal_frequency,
                                       'current_theta_loc': current_theta_loc}

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
        self.protocol_parameters = {'angle': [0.0],
                                    'height': 150.0,
                                    'width': 10.0,
                                    'theta_loc': [0.0, 10.0],
                                    'phi_loc': 0,
                                    'contrast': 1.0,
                                    'mean': 0.5,
                                    'temporal_frequency': [10.0],
                                    'fly_heading': 0.0,
                                    'render_on_cylinder': True,
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

        patch_parameters = self.getMovingSpotParameters(speed=current_spot_speed,
                                                        radius=self.protocol_parameters['spot_radius'],
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

class MovingRectangle(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        current_intensity, current_angle, current_closed_loop = self.selectParametersFromLists((self.protocol_parameters['intensity'], self.protocol_parameters['angle'],  self.protocol_parameters['closed_loop']), randomize_order=self.protocol_parameters['randomize_order'])


        self.epoch_parameters = self.getMovingPatchParameters(angle=current_angle, color=current_intensity)

        self.convenience_parameters = {'current_angle': current_angle,
                                       'current_intensity': current_intensity,
                                       'current_closed_loop': current_closed_loop}
    def loadStimuli(self, client, multicall=None):
        if multicall is None:
            multicall = flyrpc.multicall.MyMultiCall(client.manager)

        multicall.print_on_server(str({k[8:]:v for k,v in self.convenience_parameters.items()}))

        bg = self.run_parameters.get('idle_color')
        multicall.load_stim('ConstantBackground', color=[bg, bg, bg, 1.0])

        if isinstance(self.epoch_parameters, list):
            for ep in self.epoch_parameters:
                multicall.load_stim(**ep.copy(), hold=True)
        else:
            multicall.load_stim(**self.epoch_parameters.copy(), hold=True)

        multicall()

    def getParameterDefaults(self):
        self.protocol_parameters = {'width': 5.0,
                                    'height': 50.0,
                                    'intensity': [0.0, 1.0],
                                    'center': [0, 0],
                                    'speed': 80.0,
                                    'angle': [0.0, 180.0],
                                    'closed_loop': [0],
                                    'render_on_cylinder': True,
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'MovingRectangle',
                               'num_epochs': 40,
                               'pre_time': 0.5,
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
