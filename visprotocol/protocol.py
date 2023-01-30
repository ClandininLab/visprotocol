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
import os
import yaml
import flyrpc.multicall
from visprotocol.util import config_tools


class BaseProtocol():
    def __init__(self, cfg):
        self.num_epochs_completed = 0
        self.parameter_preset_directory = os.path.curdir
        self.send_ttl = False
        self.convenience_parameters = {}
        self.getRunParameterDefaults()
        self.getParameterDefaults()
        self.loadParameterPresets()
        self.user_name = cfg.get('user_name')
        self.rig_name = cfg.get('rig_name')
        self.cfg = cfg
        self.save_metadata_flag = False

        self.parameter_preset_directory = config_tools.getParameterPresetDirectory(self.cfg)
        os.makedirs(self.parameter_preset_directory, exist_ok=True)

        # Rig-specific screen center
        self.screen_center = self.cfg.get('rig_config').get(self.rig_name).get('screen_center', [0, 0])
        self.rig = self.cfg.get('rig_config').get(self.rig_name).get('rig', '(rig)')

    def adjustCenter(self, relative_center):
        absolute_center = [sum(x) for x in zip(relative_center, self.screen_center)]
        return absolute_center

    def getEpochParameters(self):
        pass

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': '',
                               'num_epochs': 5,
                               'pre_time': 1.0,
                               'stim_time': 4.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}

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
        with open(os.path.join(self.parameter_preset_directory, self.run_parameters['protocol_ID'] + '.yaml'), 'w+') as ymlfile:
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

    def loadStimuli(self, client, multicall=None):
        if multicall is None:
            multicall = flyrpc.multicall.MyMultiCall(client.manager)

        bg = self.run_parameters.get('idle_color')
        multicall.load_stim('ConstantBackground', color=[bg, bg, bg, 1.0])

        if isinstance(self.epoch_parameters, list):
            for ep in self.epoch_parameters:
                multicall.load_stim(**ep.copy(), hold=True)
        else:
            multicall.load_stim(**self.epoch_parameters.copy(), hold=True)

        multicall()

    def startStimuli(self, client, append_stim_frames=False, print_profile=True, multicall=None):
        # pre time
        sleep(self.run_parameters['pre_time'])
        
        if multicall is None:
            multicall = flyrpc.multicall.MyMultiCall(client.manager)

        # stim time
        multicall.start_stim()
        multicall.start_corner_square()
        multicall()
        sleep(self.run_parameters['stim_time'])

        # tail time
        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        multicall.stop_stim(print_profile=print_profile)
        multicall.black_corner_square()
        multicall()

        sleep(self.run_parameters['tail_time'])

    # Convenience functions shared across protocols...
    def selectParametersFromLists(self, parameter_list, all_combinations=True, randomize_order=False):
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
                parameter_sequence = np.array(np.meshgrid(*parameter_list)).T.reshape(np.prod(list(len(x) for x in parameter_list)), len(parameter_list))
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
                self.persistent_parameters['parameter_sequence'] = list(np.array(self.persistent_parameters['parameter_sequence'])[rand_inds])
            else:
                self.persistent_parameters['parameter_sequence'] = list(np.array(self.persistent_parameters['parameter_sequence'])[rand_inds, :])

        current_parameters = self.persistent_parameters['parameter_sequence'][draw_ind]

        return current_parameters