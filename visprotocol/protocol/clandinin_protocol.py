#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Protocol parent class. Override any methods in here in the user protocol subclass

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
import yaml
import inspect
import flyrpc.multicall

import visprotocol


class BaseProtocol():
    def __init__(self, user_name, rig_config):
        self.num_epochs_completed = 0
        self.parameter_preset_directory = os.path.curdir
        self.send_ttl = False
        self.convenience_parameters = {}
        self.getRunParameterDefaults()
        self.getParameterDefaults()
        self.loadParameterPresets()

        self.parameter_preset_directory = os.path.join(inspect.getfile(visprotocol).split('visprotocol')[0], 'visprotocol', 'resources', user_name, 'parameter_presets')

        # Load user config file
        path_to_config_file = os.path.join(inspect.getfile(visprotocol).split('visprotocol')[0], 'visprotocol', 'config', user_name + '_config.yaml')
        with open(path_to_config_file, 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)
            # Rig-specific screen center
            self.screen_center = cfg.get('rig_config').get(rig_config).get('screen_center', [0,0])
            self.rig = cfg.get('rig_config').get(rig_config).get('rig', '(rig)')

    def adjustCenter(self, relative_center):
        absolute_center = [sum(x) for x in zip(relative_center, self.screen_center)]
        return absolute_center

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'',
              'num_epochs':5,
              'pre_time':1.0,
              'stim_time':4.0,
              'tail_time':1.0,
              'idle_color':0.5}

    def getParameterDefaults(self):
        self.protocol_parameters = {}

    def loadParameterPresets(self):
        fname = os.path.join(self.parameter_preset_directory, self.run_parameters['protocol_ID']) + '.yaml'
        if os.path.isfile(fname):
            with open(fname, 'r') as ymlfile:
                self.parameter_presets = yaml.safe_load(ymlfile)
        else:
            self.parameter_presets = {}

    def updateParameterPresets(self, name):
        self.loadParameterPresets()
        new_preset = {'run_parameters': self.run_parameters,
                      'protocol_parameters': self.protocol_parameters}
        self.parameter_presets[name] = new_preset
        with open(os.path.join(self.parameter_preset_directory, self.run_parameters['protocol_ID'] + '.yaml'), 'w') as ymlfile:
            yaml.dump(self.parameter_presets, ymlfile, default_flow_style=False, sort_keys=False)

    def selectProtocolPreset(self, name):
        if name in self.parameter_presets:
            self.run_parameters = self.parameter_presets[name]['run_parameters']
            self.protocol_parameters = self.parameter_presets[name]['protocol_parameters']
        else:
            self.getRunParameterDefaults()
            self.getParameterDefaults()

    def advanceEpochCounter(self):
        self.num_epochs_completed += 1

    def loadStimuli(self, client):
        bg = self.run_parameters.get('idle_color')
        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        multicall.load_stim('ConstantBackground', color=[bg, bg, bg, 1.0])

        passedParameters = self.epoch_parameters.copy()
        multicall.load_stim(**passedParameters, hold=True)
        multicall()

    def startStimuli(self, client):
        sleep(self.run_parameters['pre_time'])
        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        #stim time
        multicall.start_stim()
        multicall.start_corner_square()
        multicall()
        sleep(self.run_parameters['stim_time'])

        #tail time
        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        multicall.stop_stim(print_profile=False)
        multicall.black_corner_square()
        multicall()
        sleep(self.run_parameters['tail_time'])

    # Convenience functions shared across protocols...
    def selectParametersFromLists(self, parameter_list, all_combinations = True, randomize_order = False):
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
        if type(parameter_list) is list: #single protocol parameter list, choose one from this list
            parameter_sequence = parameter_list

        elif type(parameter_list) is tuple: #multiple lists of protocol parameters
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
                parameter_sequence = np.array(np.meshgrid(*parameter_list)).T.reshape(np.prod(list(len(x) for x in parameter_list)),len(parameter_list))
            else:
                #keep params in lists associated with one another
                #requires param lists of equal length
                parameter_sequence = np.vstack(parameter_list).T

        else: #user probably entered a single value (int or float), convert to list
            parameter_sequence = [parameter_list]


        if self.num_epochs_completed == 0: #new run: initialize persistent sequences
                self.persistent_parameters = {'parameter_sequence':parameter_sequence}

        draw_ind = np.mod(self.num_epochs_completed,len(self.persistent_parameters['parameter_sequence']))
        if draw_ind == 0 and randomize_order: #randomize sequence
            rand_inds = np.random.permutation(len(self.persistent_parameters['parameter_sequence']))
            if len(np.shape(self.persistent_parameters['parameter_sequence'])) == 1:
                self.persistent_parameters['parameter_sequence'] = list(np.array(self.persistent_parameters['parameter_sequence'])[rand_inds])
            else:
                self.persistent_parameters['parameter_sequence'] = list(np.array(self.persistent_parameters['parameter_sequence'])[rand_inds,:])

        current_parameters = self.persistent_parameters['parameter_sequence'][draw_ind]

        return current_parameters


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
        if distance_to_travel is None: #distance_to_travel is set by speed and stim_time
            distance_to_travel = speed * stim_time
            #trajectory just has two points, at time=0 and time=stim_time
            startX = (0,centerX - np.cos(np.radians(angle)) * distance_to_travel/2)
            endX = (stim_time, centerX + np.cos(np.radians(angle)) * distance_to_travel/2)
            startY = (0,centerY - np.sin(np.radians(angle)) * distance_to_travel/2)
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
