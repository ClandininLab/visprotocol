#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from visprotocol.protocol import clandinin_protocol
import flyrpc.multicall
import numpy as np


class BaseProtocol(clandinin_protocol.BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)  # call the parent class init method
# %%

class HemifieldDriftingGrating(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        hemifield = ['left', 'right', 'both']
        left_rate = [-self.protocol_parameters['rate'], +self.protocol_parameters['rate']]
        right_rate = [-self.protocol_parameters['rate'], +self.protocol_parameters['rate']]
        current_hemifield, current_left_rate, current_right_rate = self.selectParametersFromLists((hemifield, left_rate, right_rate), randomize_order=self.protocol_parameters['randomize_order'])

        current_left_rate = float(current_left_rate)
        current_right_rate = float(current_right_rate)

        right_alpha = [int(x < (self.protocol_parameters['split_center'] - self.protocol_parameters['split_halfwidth'])) for x in range(36)]
        right_grate = {'name': 'RotatingGrating',
                      'period': self.protocol_parameters['period'],
                      'rate': current_right_rate,
                      'color': [1, 1, 1, 1],
                      'alpha_by_face': right_alpha,
                      'mean': self.protocol_parameters['mean'],
                      'contrast': self.protocol_parameters['contrast'],
                      'angle': 0,
                      'offset': 0.0,
                      'cylinder_radius': 2.0,
                      'cylinder_height': 10,
                      'profile': 'square',
                      'theta': self.screen_center[0]}

        left_alpha = [int(x >= (self.protocol_parameters['split_center'] + self.protocol_parameters['split_halfwidth'])) for x in range(36)]
        left_grate = {'name': 'RotatingGrating',
                       'period': self.protocol_parameters['period'],
                       'rate': current_left_rate,
                       'color': [1, 1, 1, 1],
                       'alpha_by_face': left_alpha,
                       'mean': self.protocol_parameters['mean'],
                       'contrast': self.protocol_parameters['contrast'],
                       'angle': 0,
                       'offset': 0.0,
                       'cylinder_radius': 1.0,
                       'cylinder_height': 10,
                       'profile': 'square',
                       'theta': self.screen_center[0]}

        self.epoch_parameters = (left_grate, right_grate)
        self.convenience_parameters = {'current_hemifield': str(current_hemifield),
                                       'current_left_rate': current_left_rate,
                                       'current_right_rate': current_right_rate}

        print('current_hemifield = {}'.format(current_hemifield))
        print('current_left_rate = {}'.format(current_left_rate))
        print('current_right_rate = {}'.format(current_right_rate))

        self.meta_parameters = {'current_hemifield': current_hemifield}

    def loadStimuli(self, client):
        left_parameters = self.epoch_parameters[0].copy()
        right_parameters = self.epoch_parameters[1].copy()

        bg = self.run_parameters.get('idle_color')
        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        multicall.load_stim('ConstantBackground', color=[bg, bg, bg, 1.0])

        if self.meta_parameters['current_hemifield'] == 'left':
            multicall.load_stim(**left_parameters, hold=True)
        elif self.meta_parameters['current_hemifield'] == 'right':
            multicall.load_stim(**right_parameters, hold=True)
        elif self.meta_parameters['current_hemifield'] == 'both':
            multicall.load_stim(**right_parameters, hold=True)
            multicall.load_stim(**left_parameters, hold=True)

        multicall()

    def getParameterDefaults(self):
        self.protocol_parameters = {'period': 20.0,
                                    'rate': 20.0,
                                    'split_center': 25,
                                    'split_halfwidth': 3,
                                    'contrast': 1.0,
                                    'mean': 0.5,
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'DriftingSquareGrating',
                               'num_epochs': 12,
                               'pre_time': 1.0,
                               'stim_time': 4.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}


class DriftingSquareGrating(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
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
                                    'angle': [0.0, 180.0],
                                    'center': [0, 0],
                                    'center_size': 180.0,
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'DriftingSquareGrating',
                               'num_epochs': 10,
                               'pre_time': 1.0,
                               'stim_time': 4.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}
