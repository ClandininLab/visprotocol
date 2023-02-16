#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""
import numpy as np
import os
import flyrpc.multicall
import inspect
from time import sleep
import threading
from visprotocol.device.daq import labjack

import visprotocol
from visprotocol.protocol import clandinin_protocol


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


# %%


class ContrastReversingGrating(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        adj_center = self.adjustCenter(self.protocol_parameters['center'])

        # TODO: center size with aperture (center and center_size): maybe parent class aperture method?
        current_temporal_frequency, current_spatial_period = self.selectParametersFromLists((self.protocol_parameters['temporal_frequency'],
                                                                                             self.protocol_parameters['spatial_period']),
                                                                                            randomize_order=self.protocol_parameters['randomize_order'])

        # Make the contrast trajectory
        contrast_traj = {'name': 'Sinusoid',
                         'temporal_frequency': current_temporal_frequency,
                         'amplitude': self.protocol_parameters['contrast'],
                         'offset': 0}

        self.epoch_parameters = {'name': 'CylindricalGrating',
                                 'period': current_spatial_period,
                                 'color': [1, 1, 1, 1],
                                 'mean': self.protocol_parameters['mean'],
                                 'contrast': contrast_traj,
                                 'angle': self.protocol_parameters['angle'],
                                 'offset': 0.0,
                                 'cylinder_radius': 1.0,
                                 'cylinder_height': 10.0,
                                 'profile': 'square',
                                 'theta': adj_center[0]}

        self.convenience_parameters = {'current_temporal_frequency': current_temporal_frequency,
                                       'current_spatial_period': current_spatial_period}

    def getParameterDefaults(self):
        self.protocol_parameters = {'spatial_period': [10.0, 20.0],
                                    'contrast': 1.0,
                                    'mean': 0.5,
                                    'temporal_frequency': [0.5, 1.0, 2.0, 4.0, 8.0, 16.0],
                                    'center': [0, 0],
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


class DriftingSineGrating(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        # TODO: center size with aperture (center and center_size)
        current_period, current_rate, current_contrast = self.selectParametersFromLists((self.protocol_parameters['period'],
                                                                                         self.protocol_parameters['rate'],
                                                                                         self.protocol_parameters['contrast']), randomize_order=self.protocol_parameters['randomize_order'])

        self.epoch_parameters = {'name': 'RotatingGrating',
                                 'period': current_period,
                                 'rate': current_rate,
                                 'color': [1, 1, 1, 1],
                                 'mean': self.protocol_parameters['mean'],
                                 'contrast': current_contrast,
                                 'angle': self.protocol_parameters['angle'],
                                 'offset': 0.0,
                                 'cylinder_radius': 1,
                                 'cylinder_height': 10,
                                 'profile': 'sine',
                                 'theta': self.screen_center[0]}

        self.convenience_parameters = {'current_period': current_period,
                                       'current_rate': current_rate,
                                       'current_contrast': current_contrast}

        self.meta_parameters = {'center_size': self.protocol_parameters['center_size'],
                                'center': self.adjustCenter(self.protocol_parameters['center'])}

    def getParameterDefaults(self):
        self.protocol_parameters = {'period': [5.0, 10.0, 20.0],  # spatial period, degrees
                                    'rate': [10.0, 20.0, 40.0],  # drift speed, degrees/second
                                    'contrast': [1.0],
                                    'mean': 0.5,
                                    'angle': 0.0,
                                    'center': [0, 0],
                                    'center_size': 180.0,
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'DriftingSineGrating',
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


class FlickeringSpot(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        adj_center = self.adjustCenter(self.protocol_parameters['center'])

        current_temporal_frequency, current_diameter = self.selectParametersFromLists((self.protocol_parameters['temporal_frequency'],
                                                                                      self.protocol_parameters['diameter']),
                                                                                      randomize_order=self.protocol_parameters['randomize_order'])

        # make color trajectory
        color_traj = {'name': 'Sinusoid',
                      'temporal_frequency': current_temporal_frequency,
                      'amplitude': self.protocol_parameters['mean'] * self.protocol_parameters['contrast'],
                      'offset': self.protocol_parameters['mean']}

        self.epoch_parameters = {'name': 'MovingSpot',
                                 'radius': current_diameter/2,
                                 'sphere_radius': 1,
                                 'color': color_traj,
                                 'theta': adj_center[0],
                                 'phi': adj_center[1]}

        self.convenience_parameters = {'current_temporal_frequency': current_temporal_frequency,
                                       'current_diameter': current_diameter}

    def getParameterDefaults(self):
        self.protocol_parameters = {'diameter': [5.0, 10.0, 20.0, 30.0],
                                    'center': [0, 0],
                                    'contrast': 1.0,
                                    'mean': 0.5,
                                    'temporal_frequency': [0.5, 1.0, 2.0, 4.0, 8.0, 16.0],
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'FlickeringSpot',
                               'num_epochs': 30,
                               'pre_time': 1.0,
                               'stim_time': 4.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}

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

class OptoStepSeries(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        current_led_intensity, current_led_duration = self.selectParametersFromLists((self.protocol_parameters['led_intensity'],
                                                                                      self.protocol_parameters['led_duration']),
                                                                                     randomize_order=self.protocol_parameters['randomize_order'])


        self.convenience_parameters = {'current_led_intensity': current_led_intensity,
                                        'current_led_duration': current_led_duration}

        self.epoch_parameters = None

    def loadStimuli(self, client, multicall=None):
        pass

    def getParameterDefaults(self):
        self.protocol_parameters = {
                                    'led_duration': [0.25, 0.5, 2.0, 4.0],  # sec, duration. Must be shorter than stim_time
                                    'led_intensity': [0.25, 0.5, 1, 2, 4],  # V
                                    'randomize_order': True
                                    }


    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'OptoStepSeries',
                               'num_epochs': 150,
                               'pre_time': 2,
                               'stim_time': 5,
                               'tail_time': 10,
                               'idle_color': 0.5}


    def startStimuli(self, client, append_stim_frames=False, print_profile=True):
        # Create the labjack device
        # TODO: check to see if it makes more sense to not re-create device each epoch
        # TODO double check LED timing
        labjack_dev = labjack.LabJackTSeries()

        # Create the thread
        args_dict = {'output_channel': 'DAC0',
                     'pre_time': 0,  # sec
                     'step_time': self.convenience_parameters['current_led_duration'],  # sec
                     'tail_time': 0,  # sec
                     'step_amp': self.convenience_parameters['current_led_intensity'],  # V
                     'dt': 0.01,  # sec
                     }
        labjack_thread = threading.Thread(target=labjack_dev.analogOutputStep,
                                          args=tuple(args_dict.values()))

        assert self.convenience_parameters['current_led_duration'] < self.run_parameters['stim_time'], "led_duration must be shorter than stim_time"

        # Vis stimulus stuff follows. Just do flickering corner to give stim timing, I guess.
        sleep(self.run_parameters['pre_time'])

        # start the thread
        labjack_thread.start()

        # Multicall starts multiple stims simultaneously
        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        # stim time
        multicall.start_corner_square()
        multicall()  # multicall starts corner square
        sleep(self.run_parameters['stim_time'])  # sleep during the stim time

        # tail time
        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        multicall.black_corner_square()
        multicall()   # multicall to stop stim + corner square at the same time

        sleep(self.run_parameters['tail_time'])  # sleep during tail time

        # close the labjack device
        labjack_dev.setAnalogOutputToZero(output_channel='DAC0')
        labjack_dev.close()



# %% FlashSeriesWithOptoStep

class FlashSeriesWithOptoStep(BaseProtocol):
    # TODO: double check timing
    # TODO: TEST on rig
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        adj_center = self.adjustCenter(self.protocol_parameters['center'])

        current_led_intensity = self.selectParametersFromLists(self.protocol_parameters['led_intensity'], randomize_order=self.protocol_parameters['randomize_order'])

        time_intensity_tuples = [(0, 0.5)]  # (time (sec), intensity)
        for ft in self.protocol_parameters['flash_times']:
            # flash on
            new_tv = (ft, self.protocol_parameters['flash_intensity'])
            time_intensity_tuples.append(new_tv)

            # flash off
            new_tv = (ft+self.protocol_parameters['flash_width'], 0.5)
            time_intensity_tuples.append(new_tv)

        end_tv = (self.run_parameters['stim_time'], 0.5)
        time_intensity_tuples.append(end_tv)

        intensity_trajectory = {'name': 'tv_pairs',
                                'tv_pairs': time_intensity_tuples,
                                'kind': 'previous'}

        self.epoch_parameters = {'name': 'MovingPatch',
                                 'width': self.protocol_parameters['width'],
                                 'height': self.protocol_parameters['height'],
                                 'sphere_radius': 1,
                                 'color': intensity_trajectory,
                                 'theta': adj_center[0],
                                 'phi': adj_center[1],
                                 'angle': 0}

        self.convenience_parameters = {'current_led_intensity': current_led_intensity}

    def getParameterDefaults(self):
        # self.protocol_parameters = {'height': 240.0,
        #                             'width': 240.0,
        #                             'center': [0, 0],
        #                             'flash_width': 0.5,  # sec
        #                             'flash_times': [1, 3, 7, 9, 13],  # sec, flash onsets, into stim time
        #                             'flash_intensity': 1,

        #                             'led_time': 2,  # sec, onset
        #                             'led_duration': 6,  # sec, duration. Must be shorter than stim_time

        #                             'led_intensity': [0.25, 0.5, 1, 2, 4],  # V
        #                             'randomize_order': True}       
        self.protocol_parameters = {'height': 240.0,
                                    'width': 240.0,
                                    'center': [0, 0],
                                    'flash_width': 0.5,  # sec
                                    'flash_times': [1, 3.2, 4.5, 6.2, 8.2, 10.2, 12.2],  # sec, flash onsets, into stim time
                                    'flash_intensity': 1,

                                    'led_time': 3,  # sec, onset
                                    'led_duration': 3,  # sec, duration. Must be shorter than stim_time

                                    'led_intensity': [0.25, 1, 4],  # V
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'FlashSeriesWithOptoStep',
                               'num_epochs': 108,
                               'pre_time': 2,
                               'stim_time': 14,
                               'tail_time': 2,
                               'idle_color': 0.5}

    def startStimuli(self, client, append_stim_frames=False, print_profile=True):
        # Create the labjack device
        # TODO: check to see if it makes more sense to not re-create device each epoch
        # TODO double check LED timing
        labjack_dev = labjack.LabJackTSeries()

        # Create the thread
        args_dict = {'output_channel': 'DAC0',
                     'pre_time': self.protocol_parameters['led_time'],  # sec
                     'step_time': self.protocol_parameters['led_duration'],  # sec
                     'tail_time': self.run_parameters['stim_time'] - self.protocol_parameters['led_duration'] - self.protocol_parameters['led_time'],  # sec
                     'step_amp': self.convenience_parameters['current_led_intensity'],  # V
                     'dt': 0.01,  # sec
                     }
        labjack_thread = threading.Thread(target=labjack_dev.analogOutputStep,
                                          args=tuple(args_dict.values()))

        assert self.protocol_parameters['led_duration'] < self.run_parameters['stim_time'], "led_duration must be shorter than stim_time"

        # pre time
        sleep(self.run_parameters['pre_time'])

        # start the thread
        labjack_thread.start()

        # Multicall starts multiple stims simultaneously
        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        # stim time
        multicall.start_stim(append_stim_frames=append_stim_frames)
        multicall.start_corner_square()
        multicall()  # multicall starts stim and corner square at the same time
        sleep(self.run_parameters['stim_time'])  # sleep during the stim time

        # tail time
        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        multicall.stop_stim(print_profile=print_profile)
        multicall.black_corner_square()
        multicall()   # multicall to stop stim + corner square at the same time

        sleep(self.run_parameters['tail_time'])  # sleep during tail time

        # close the labjack device
        labjack_dev.setAnalogOutputToZero(output_channel='DAC0')
        labjack_dev.close()


# %% Flickering full field with opto

class FlickerWithOpto(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        # # # Visual stimulus parameters # # #
        # Adjust protocol_parameters['center'] according to rig screen center
        adj_center = self.adjustCenter(self.protocol_parameters['center'])

        # Sinusoid trajectory dictionary. See flystim.trajectory
        intensity_trajectory = {'name': 'Sinusoid',
                                'temporal_frequency': self.protocol_parameters['temporal_frequency'],
                                'amplitude': self.run_parameters['idle_color'] * self.protocol_parameters['contrast'],
                                'offset': self.run_parameters['idle_color']}

        # epoch_parameters dictionary. Defines the flystim stimulus for this epoch.
        # See flystim.stimuli
        self.epoch_parameters = {'name': 'MovingPatch',
                                 'width': self.protocol_parameters['width'],
                                 'height': self.protocol_parameters['height'],
                                 'sphere_radius': 1,
                                 'color': intensity_trajectory,
                                 'theta': adj_center[0],
                                 'phi': adj_center[1],
                                 'angle': 0}

        # # # Opto parameters # # #
        # Error checking: opto_mode has to be one of these three options
        assert self.protocol_parameters['opto_mode'] in ['on', 'off', 'alternating']

        # Figure out whether opto_stim is true/false for this epoch
        self.convenience_parameters = {}
        if self.protocol_parameters['opto_mode'] == 'on':
            self.convenience_parameters['opto_stim'] = True

        elif self.protocol_parameters['opto_mode'] == 'off':
            self.convenience_parameters['opto_stim'] = False

        elif self.protocol_parameters['opto_mode'] == 'alternating':
            if np.mod(self.num_epochs_completed, 2) == 0:  # Even numbered trials
                self.convenience_parameters['opto_stim'] = False
            else:   # Odd numbered trials
                self.convenience_parameters['opto_stim'] = True
        else:
            print('Unrecognized opto_mode string. Allowable: [on, off, alternating]')

        # Figure out opto timing for this epoch
        current_opto_start_time = self.selectParametersFromLists(self.protocol_parameters['opto_start_time'], randomize_order=self.protocol_parameters['randomize_order'])
        self.convenience_parameters['current_opto_start_time'] = current_opto_start_time

    def startStimuli(self, client, append_stim_frames=False, print_profile=True):
        if self.convenience_parameters['opto_stim']:  # Show opto on this trial
            # |--current_opto_start_time--|--opto_time--|--(pre_time-opto_time-current_opto_start_time)
            sleep(self.convenience_parameters['current_opto_start_time'])  # sleep until opto start time
            # deliver opto pulse
            client.daq_device.outputStep(output_channel='ctr1',
                                           low_time=0.001,
                                           high_time=self.protocol_parameters['opto_time'],
                                           initial_delay=0.0)
            sleep(self.run_parameters['pre_time']-self.protocol_parameters['opto_time']-self.convenience_parameters['current_opto_start_time'])
        else:  # no opto on this trial
            sleep(self.run_parameters['pre_time'])

        # The rest of this is standard visual stim stuff...
        # Multicall starts multiple stims simultaneously
        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        # stim time
        multicall.start_stim(append_stim_frames=append_stim_frames)
        multicall.start_corner_square()
        multicall()  # multicall starts stim and corner square at the same time
        sleep(self.run_parameters['stim_time'])  # sleep during the stim time

        # tail time
        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        multicall.stop_stim(print_profile=print_profile)
        multicall.black_corner_square()
        multicall()   # multicall to stop stim + corner square at the same time

        sleep(self.run_parameters['tail_time'])  # sleep during tail time

    def getParameterDefaults(self):
        self.protocol_parameters = {'height': 180.0,
                                    'width': 180.0,
                                    'center': [0, 0],
                                    'temporal_frequency': 1.0,  # Hz
                                    'contrast': 1.0,  # weber contrast. c = (i-b)/b
                                    'opto_mode': 'alternating',  # 'on', 'off', 'alternating'
                                    'opto_time': 1.0,  # sec
                                    'opto_start_time': [1, 2, 3, 4],  # sec, time within the pre-time
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'FlickerWithOpto',
                               'num_epochs': 80,
                               'pre_time': 5.0,
                               'stim_time': 3.0,
                               'tail_time': 2.0,
                               'idle_color': 0.5}


# %% Full field white noise with opto

class WhiteNoiseWithOpto(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        # # # Visual stimulus parameters # # #
        # Adjust protocol_parameters['center'] according to rig screen center
        adj_center = self.adjustCenter(self.protocol_parameters['center'])

        # # # Opto parameters # # #
        # Error checking: opto_mode has to be one of these three options
        self.convenience_parameters = {}
        assert self.protocol_parameters['opto_mode'] in ['on', 'off', 'alternating']

        if self.protocol_parameters['opto_mode'] == 'on':
            self.convenience_parameters['opto_stim'] = True
            start_seed = int(np.random.choice(range(int(1e6))))

        elif self.protocol_parameters['opto_mode'] == 'off':
            self.convenience_parameters['opto_stim'] = False
            start_seed = int(np.random.choice(range(int(1e6))))

        elif self.protocol_parameters['opto_mode'] == 'alternating':
            if np.mod(self.num_epochs_completed, 2) == 0:
                self.convenience_parameters['opto_stim'] = False
            else:
                self.convenience_parameters['opto_stim'] = True
            # Find seed s.t. subsequent trials share a seed. Increment seed every 2 trials
            if self.num_epochs_completed == 0:
                self.fly_start_seed = int(np.random.choice(range(int(1e6))))

            start_seed = self.fly_start_seed + (self.num_epochs_completed//2)
        else:
            print('Unrecognized opto_mode string. Allowable: [on, off, alternating]')

        # Random distribution dictionary. See flystim.distribution
        distribution_data = {'name': 'Ternary',
                             'args': [],
                             'kwargs': {'rand_min': 0,
                                        'rand_max': 1}}

        # epoch_parameters dictionary. Defines the flystim stimulus for this epoch.
        # See flystim.stimuli
        self.epoch_parameters = {'name': 'UniformWhiteNoise',
                                 'width': self.protocol_parameters['width'],
                                 'height': self.protocol_parameters['height'],
                                 'sphere_radius': 1,
                                 'start_seed': start_seed,
                                 'update_rate': self.protocol_parameters['update_rate'],
                                 'distribution_data': distribution_data,
                                 'theta': adj_center[0],
                                 'phi': adj_center[1],
                                 'angle': 0}

        self.convenience_parameters['start_seed'] = start_seed


    def startStimuli(self, client, append_stim_frames=False, print_profile=True):
        if self.convenience_parameters['opto_stim']:
            client.daq_device.outputStep(output_channel='ctr1',
                                         low_time=0.001,
                                         high_time=self.protocol_parameters['opto_time'],
                                         initial_delay=0.0)
            sleep(self.run_parameters['pre_time']-self.protocol_parameters['opto_time'])
        else:
            sleep(self.run_parameters['pre_time'])

        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        # stim time
        multicall.start_stim(append_stim_frames=append_stim_frames)
        multicall.start_corner_square()
        multicall()
        sleep(self.run_parameters['stim_time'])

        # tail time
        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        multicall.stop_stim(print_profile=print_profile)
        multicall.black_corner_square()
        multicall()
        sleep(self.run_parameters['tail_time'])

    def getParameterDefaults(self):
        self.protocol_parameters = {'height': 240.0,
                                    'width': 240.0,
                                    'center': [0, 0],
                                    'update_rate': 20.0,  # Noise update rate, Hz
                                    'opto_mode': 'alternating',  # 'on', 'off', 'alternating'
                                    'opto_time': 1.0,  # sec
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'WhiteNoiseWithOpto',
                               'num_epochs': 150,  # 2/10/2 & 150 trials = 25 min total noise (12.5 each opto). Total series time = 35 min.
                               'pre_time': 2.0,
                               'stim_time': 10.0,
                               'tail_time': 2.0,
                               'idle_color': 0.5}
# %%
"""
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # MULTI-COMPONENT STIMS # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""


class MedullaTuningSuite(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.cfg = cfg
        self.stim_list = ['ContrastReversingGrating']
        n = [16]  # weight each stim draw by how many trial types it has. Total = 16
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
            if stim_type == 'DriftingSineGrating':
                new_component_class = DriftingSineGrating(self.cfg)
                new_component_class.protocol_parameters = {'period': [5.0, 10.0, 20.0],  # spatial period, degrees
                                                           'rate': [10.0, 20.0, 40.0],  # drift speed, degrees/second
                                                           'contrast': 1.0,
                                                           'mean': 0.5,
                                                           'angle': 0.0,
                                                           'center': [0, 0],
                                                           'center_size': 180.0,
                                                           'randomize_order': True}

            elif stim_type == 'ContrastReversingGrating':
                new_component_class = ContrastReversingGrating(self.cfg)
                new_component_class.protocol_parameters = {'spatial_period': [10.0, 20.0, 40.0, 80.0],  # spatial period, degrees
                                                           'temporal_frequency': [0.5, 1.0, 2.0, 4.0],  # Hz
                                                           'contrast': 1.0,
                                                           'mean': 0.5,
                                                           'angle': 0.0,
                                                           'center': [30, 0],
                                                           'randomize_order': True}

            elif stim_type == 'FlickeringSpot':
                new_component_class = FlickeringSpot(self.cfg)
                new_component_class.protocol_parameters = {'diameter': [5.0, 10.0, 20.0, 30.0],
                                                           'center': [0, 0],
                                                           'contrast': 1.0,
                                                           'mean': 0.5,
                                                           'temporal_frequency': [1.0, 2.0, 4.0, 8.0, 16.0],
                                                           'randomize_order': True}

            # Lock component stim timing run params to suite run params
            new_component_class.run_parameters['pre_time'] = self.run_parameters['pre_time']
            new_component_class.run_parameters['stim_time'] = self.run_parameters['stim_time']
            new_component_class.run_parameters['tail_time'] = self.run_parameters['tail_time']
            new_component_class.run_parameters['idle_color'] = self.run_parameters['idle_color']

            self.component_classes[stim_type] = new_component_class

    def getEpochParameters(self):
        stim_type = str(self.stim_order[self.num_epochs_completed])  # note this num_epochs_completed is for the whole suite, not component stim!
        self.convenience_parameters = {'component_stim_type': stim_type}

        assert self.protocol_parameters['opto_mode'] in ['on', 'off', 'alternating']

        if self.protocol_parameters['opto_mode'] == 'on':
            self.convenience_parameters['opto_stim'] = True

        elif self.protocol_parameters['opto_mode'] == 'off':
            self.convenience_parameters['opto_stim'] = False

        elif self.protocol_parameters['opto_mode'] == 'alternating':
            if np.mod(self.num_epochs_completed, 2) == 0:
                self.convenience_parameters['opto_stim'] = False
            else:
                self.convenience_parameters['opto_stim'] = True
        else:
            print('Unrecognized opto_mode string. Allowable: [on, off, alternating]')


        self.component_class = self.component_classes[stim_type]

        self.component_class.getEpochParameters()
        self.convenience_parameters.update(self.component_class.convenience_parameters)
        self.epoch_parameters = self.component_class.epoch_parameters

    def loadStimuli(self, client):
        self.component_class.loadStimuli(client)
        self.component_class.advanceEpochCounter()  # up the component class epoch counter

    def startStimuli(self, client, append_stim_frames=False, print_profile=True):
        if self.convenience_parameters['opto_stim']:
            client.daq_device.outputStep(output_channel='ctr1',
                                           low_time=0.001,
                                           high_time=self.protocol_parameters['opto_time'],
                                           initial_delay=0.0)
            sleep(self.run_parameters['pre_time']-self.protocol_parameters['opto_time'])
        else:
            sleep(self.run_parameters['pre_time'])

        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        # stim time
        multicall.start_stim(append_stim_frames=append_stim_frames)
        multicall.start_corner_square()
        multicall()
        sleep(self.run_parameters['stim_time'])

        # tail time
        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        multicall.stop_stim(print_profile=print_profile)
        multicall.black_corner_square()
        multicall()

        sleep(self.run_parameters['tail_time'])

    def getParameterDefaults(self):
        self.protocol_parameters = {'opto_mode': 'alternating',  # 'on', 'off', 'alternating'
                                    'opto_time': 1.0}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'MedullaTuningSuite',
                               'num_epochs': 96,  # 96 = 16 stims * 2 opto conditions * 3 averages each
                               'pre_time': 2.0,
                               'stim_time': 3.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}
