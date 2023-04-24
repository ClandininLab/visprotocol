#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Protocol parent class. Override any methods in here in the user protocol subclass

A user-defined protocol class needs to overwrite the following methods, at minimum:
-get_epoch_parameters()
-get_parameter_defaults()

And probably also:
-get_run_parameter_defaults()

see the simple example protocol classes at the bottom of this module.

-protocol_parameters: user-defined params that are mapped to flystim epoch params
                     *saved as attributes at the epoch run level
-epoch_parameters: parameter set used to define flystim stimulus
                     *saved as attributes at the individual epoch level
-convenience_parameters: user-defined params to save to epoch data, to simplify downstream analysis
                     *saved as attributes at the individual epoch level
"""
import numpy as np
from time import sleep
import os.path
import os
import yaml
import itertools
import flyrpc.multicall
from visprotocol.util import config_tools


class BaseProtocol():
    def __init__(self, cfg):
        self.cfg = cfg

        self.num_epochs_completed = 0
        self.parameter_preset_directory = os.path.curdir
        self.trigger_on_epoch_run = True  # Used in control.EpochRun.start_run(), sends a TTL trigger to start acquisition devices
        self.trigger_on_epoch = False  # Used in control.EpochRun.start_epoch(), sends a TTL trigger to start acquisition devices
        self.save_metadata_flag = False  # Bool, whether or not to save this series. Set to True by GUI on 'record' but not 'view'.

        # convenience_parameters used to store protocol parameters that will be saved out in an easily accessible place in the data file
        # Fill this in with desired parameters in get_epoch_parameters(). Can also be used to control other features of the stimulus and used in load_stimuli()
        self.convenience_parameters = {}

        self.get_run_parameter_defaults()
        self.get_parameter_defaults()
        self.load_parameter_presets()
        
        self.parameter_preset_directory = config_tools.get_parameter_preset_directory(self.cfg)
        if self.parameter_preset_directory is not None:
            os.makedirs(self.parameter_preset_directory, exist_ok=True)

        # Rig-specific screen center
        self.screen_center = config_tools.get_screen_center(self.cfg)

    def adjust_center(self, relative_center):
        absolute_center = [sum(x) for x in zip(relative_center, self.screen_center)]
        return absolute_center

    def get_epoch_parameters(self):
        """ Overwrite me in the child subclass"""
        self.epoch_parameters = None

    def get_run_parameter_defaults(self):
        self.run_parameters = {'protocol_ID': '',
                               'num_epochs': 5,
                               'pre_time': 1.0,
                               'stim_time': 4.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}

    def get_parameter_defaults(self):
        """ Overwrite me in the child subclass"""
        self.protocol_parameters = {}

    def load_parameter_presets(self):
        fname = os.path.join(self.parameter_preset_directory, self.run_parameters['protocol_ID']) + '.yaml'
        if os.path.isfile(fname):
            with open(fname, 'r') as ymlfile:
                self.parameter_presets = yaml.safe_load(ymlfile)
        else:
            self.parameter_presets = {}

    def update_parameter_presets(self, name):
        self.load_parameter_presets()
        new_preset = {'run_parameters': self.run_parameters,
                      'protocol_parameters': self.protocol_parameters}
        self.parameter_presets[name] = new_preset
        with open(os.path.join(self.parameter_preset_directory, self.run_parameters['protocol_ID'] + '.yaml'), 'w+') as ymlfile:
            yaml.dump(self.parameter_presets, ymlfile, default_flow_style=False, sort_keys=False)

    def select_protocol_preset(self, name):
        '''
        Parameters that are not present in the preset will use the current protocol's default values.
        '''

        self.getRunParameterDefaults()
        self.getParameterDefaults()

        if name not in self.parameter_presets:
            warnings.warn(f'Warning: Preset {name} not found.', RuntimeWarning)
            return

        # Warn about any param that is not in the preset
        for k in self.run_parameters.keys():
            if k not in self.parameter_presets[name]['run_parameters'].keys():
                warnings.warn(f'Warning: run parameter {k} not found in preset {name}; using default.', RuntimeWarning)
        for k in self.protocol_parameters.keys():
            if k not in self.parameter_presets[name]['protocol_parameters'].keys():
                warnings.warn(f'Warning: protocol parameter {k} not found in preset {name}; using default.', RuntimeWarning)

        # Update the protocol parameters
        # Warn about any preset param that is not in the current protocol
        for k, v in self.parameter_presets[name]['run_parameters'].items():
            if k in self.run_parameters.keys():
                self.run_parameters[k] = v
            else:
                warnings.warn(f'Warning: run parameter {k} not found in current protocol. Skipping preset parameter.', RuntimeWarning)
        for k, v in self.parameter_presets[name]['protocol_parameters'].items():
            if k in self.protocol_parameters.keys():
                self.protocol_parameters[k] = v
            else:
                warnings.warn(f'Warning: protocol parameter {k} not found in current protocol. Skipping preset parameter.', RuntimeWarning)            

    def advance_epoch_counter(self):
        self.num_epochs_completed += 1

    def load_stimuli(self, manager, multicall=None):
        if multicall is None:
            multicall = flyrpc.multicall.MyMultiCall(manager)

        bg = self.run_parameters.get('idle_color')
        multicall.load_stim('ConstantBackground', color=[bg, bg, bg, 1.0])

        if isinstance(self.epoch_parameters, list):
            for ep in self.epoch_parameters:
                multicall.load_stim(**ep.copy(), hold=True)
        else:
            multicall.load_stim(**self.epoch_parameters.copy(), hold=True)

        multicall()

    def start_stimuli(self, manager, append_stim_frames=False, print_profile=True, multicall=None):
        # pre time
        sleep(self.run_parameters['pre_time'])
        
        if multicall is None:
            multicall = flyrpc.multicall.MyMultiCall(manager)

        # stim time
        multicall.start_stim()
        multicall.start_corner_square()
        multicall()
        sleep(self.run_parameters['stim_time'])

        # tail time
        multicall = flyrpc.multicall.MyMultiCall(manager)
        multicall.stop_stim(print_profile=print_profile)
        multicall.black_corner_square()
        multicall()

        sleep(self.run_parameters['tail_time'])
# %% Convenience methods
    def select_parameters_from_lists(self, parameter_list, all_combinations=True, randomize_order=False):
        """
        inputs
        parameter_list can be:
            -list/array of parameters
            -single value (int, float etc)
            -tuple of lists, where each list contains values for a single parameter
                    in this case, all_combinations = True will return all possible combinations of parameters, taking
                    one from each parameter list. If all_combinations = False, keeps params associated across lists
        randomize_order will randomize sequence or sequences at the beginning of each new sequence
        """

        # parameter_list is a tuple of lists or a single list
        if type(parameter_list) is list: # single protocol parameter list, choose one from this list
            parameter_sequence = parameter_list

        elif type(parameter_list) is tuple: # multiple lists of protocol parameters
            if all_combinations:
                parameter_list_new = []

                # check for non-list elements of the tuple (int or float user entry)
                for param in list(parameter_list):
                    if type(param) is not list:
                        parameter_list_new.append([param])
                    else:
                        parameter_list_new.append(param)
                parameter_list = tuple(parameter_list_new)

                # parameter_sequence is num_combinations by num params
                parameter_sequence = list(itertools.product(*parameter_list))
            else:
                # keep params in lists associated with one another
                # requires param lists of equal length
                parameter_sequence = np.vstack(parameter_list).T

        else: # user probably entered a single value (int or float), convert to list
            parameter_sequence = [parameter_list]

        if self.num_epochs_completed == 0: # new run: initialize persistent sequences
            self.persistent_parameters = {'parameter_sequence': parameter_sequence}

        draw_ind = np.mod(self.num_epochs_completed, len(self.persistent_parameters['parameter_sequence']))
        if draw_ind == 0 and randomize_order: # randomize sequence
            rand_inds = np.random.permutation(len(self.persistent_parameters['parameter_sequence']))
            if len(np.shape(self.persistent_parameters['parameter_sequence'])) == 1:
                self.persistent_parameters['parameter_sequence'] = list(np.array(self.persistent_parameters['parameter_sequence'], dtype=object)[rand_inds])
            else:
                self.persistent_parameters['parameter_sequence'] = list(np.array(self.persistent_parameters['parameter_sequence'], dtype=object)[rand_inds, :])

        current_parameters = self.persistent_parameters['parameter_sequence'][draw_ind]

        return current_parameters
    
    def select_parameters_from_protocol_parameter_names(self, parameter_names, all_combinations=True, randomize_order=False):
        """
        inputs
        parameter_names:
            list of protocol parameter names (keys of self.protocol_parameters)
        all_combinations:
            True will return all possible combinations of parameters, taking one from each parameter list. 
            False keeps params associated across lists
        randomize_order will randomize sequence or sequences at the beginning of each new sequence
        
        returns
        current_parameters_dict:
            dictionary of parameter names and values specific to this epoch. parameter names are prepended with 'current_'
        """
        parameter_tuple = tuple(self.protocol_parameters[parameter_name] for parameter_name in parameter_names)
        current_parameters = self.select_parameters_from_lists(parameter_tuple, all_combinations=all_combinations, randomize_order=randomize_order)

        current_parameters_dict = {"current_" + parameter_name: current_parameters[i] for i, parameter_name in enumerate(parameter_names)}
        
        return current_parameters_dict
    
    def get_moving_patch_parameters(self, center=None, angle=None, speed=None, width=None, height=None, color=None, distance_to_travel=None, ellipse=None, render_on_cylinder=None):
        if center is None: center = self.protocol_parameters['center']
        if angle is None: angle = self.protocol_parameters['angle']
        if speed is None: speed = self.protocol_parameters['speed']
        if width is None: width = self.protocol_parameters['width']
        if height is None: height = self.protocol_parameters['height']
        if color is None: color = self.protocol_parameters['color']
        if ellipse is None: ellipse = self.protocol_parameters['ellipse'] if 'ellipse' in self.protocol_parameters else False
        if render_on_cylinder is None: render_on_cylinder = self.protocol_parameters['render_on_cylinder'] if 'render_on_cylinder' in self.protocol_parameters else False

        center = self.adjust_center(center)

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

# %% Some simple visual stimulus protocol classes

"""
Drifting square wave grating, painted on a cylinder
"""
class DriftingSquareGrating(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.get_run_parameter_defaults()
        self.get_parameter_defaults()

    def get_epoch_parameters(self):
        current_angle = self.select_parameters_from_lists(self.protocol_parameters['angle'], randomize_order = self.protocol_parameters['randomize_order'])

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

    def get_parameter_defaults(self):
        self.protocol_parameters = {'period': 20.0,
                                    'rate': 20.0,
                                    'contrast': 1.0,
                                    'mean': 0.5,
                                    'angle': [0.0, 90.0, 180.0, 270.0],
                                    'center': [0, 0],
                                    'center_size': 180.0,
                                    'randomize_order': True}

    def get_run_parameter_defaults(self):
        self.run_parameters = {'protocol_ID': 'DriftingSquareGrating',
                               'num_epochs': 40,
                               'pre_time': 1.0,
                               'stim_time': 4.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}

# %%

class MovingPatch(BaseProtocol):
    """
    Moving patch, either rectangular or elliptical. Moves along a spherical or cylindrical trajectory
    """
    def __init__(self, cfg):
        super().__init__(cfg)

        self.get_run_parameter_defaults()
        self.get_parameter_defaults()

    def get_epoch_parameters(self):
        # Select protocol parameters for this epoch
        self.convenience_parameters = self.select_parameters_from_protocol_parameter_names(
            ['width_height', 'intensity', 'speed', 'angle'], 
            randomize_order = self.protocol_parameters['randomize_order'])

        # Create flystim epoch parameters dictionary
        self.epoch_parameters = self.get_moving_patch_parameters(angle=self.convenience_parameters['current_angle'],
                                                                speed=self.convenience_parameters['current_speed'],
                                                                width=self.convenience_parameters['current_width_height'][0],
                                                                height=self.convenience_parameters['current_width_height'][1],
                                                                color=self.convenience_parameters['current_intensity'])

    def get_parameter_defaults(self):
        self.protocol_parameters = {'ellipse': True,
                                    'width_height': [[5, 5], [10, 10], [15, 15], [20, 20], [25, 25], [30, 30]],
                                    'intensity': [0.0],
                                    'center': [0, 0],
                                    'speed': [80.0],
                                    'angle': [0.0],
                                    'render_on_cylinder': False,
                                    'randomize_order': True}

    def get_run_parameter_defaults(self):
        self.run_parameters = {'protocol_ID': 'MovingPatch',
                               'num_epochs': 40,
                               'pre_time': 0.5,
                               'stim_time': 3.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}
