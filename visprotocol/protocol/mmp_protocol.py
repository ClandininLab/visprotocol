#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import os
import inspect
from datetime import datetime
from time import sleep


import visprotocol
from visprotocol.protocol import clandinin_protocol
from flystim.trajectory import Trajectory


class BaseProtocol(clandinin_protocol.BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)
# %%
class BinaryFlash(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        adj_center = self.adjustCenter(self.protocol_parameters['center'])

        self.epoch_parameters = {'name': 'MovingPatch',
                                 'width': self.protocol_parameters['width'],
                                 'height': self.protocol_parameters['height'],
                                 'sphere_radius': 1,
                                 'color': self.protocol_parameters['intensity'],
                                 'theta': adj_center[0],
                                 'phi': adj_center[1],
                                 'angle': 0}

    def getParameterDefaults(self):
        self.protocol_parameters = {'height':180.0,
                       'width':180.0,
                       'center': [0.0, 0.0],
                       'intensity': 1.0}


    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'BinaryFlash',
              'num_epochs':100,
              'pre_time':0.05,
              'stim_time':0.3,
              'tail_time':0.25,
              'idle_color':0.5}

#%%
class MultipleContrastFlash(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        current_intensity = self.selectParametersFromLists(self.protocol_parameters['intensity'],
                                                                randomize_order = self.protocol_parameters['randomize_order'])

        adj_center = self.adjustCenter(self.protocol_parameters['center'])

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
        self.protocol_parameters = {'height':180.0,
                       'width':180.0,
                       'center': [0.0, 0.0],
                       'intensity': [0, 0.25, 0.375, 0.625, 0.75, 1.0],
                       'randomize_order': True}


    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'MultipleContrastFlash',
              'num_epochs':600,
              'pre_time':0.05,
              'stim_time':0.02,
              'tail_time':0.45,
              'idle_color':0.5}
