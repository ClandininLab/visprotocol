#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import os
from time import sleep

import visprotocol
from visprotocol.protocol import clandinin_protocol
import flyrpc.multicall

class BaseProtocol(clandinin_protocol.BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)  # call the parent class init method
# %%
"""
Define a new class for each stimulus protocol.
Each protocol class should define these methods:
    __init__()
    getEpochParameters()
    getParameterDefaults()
    getRunParameterDefaults()

It may define/overwrite these methods that are typically handled by the parent class

"""

class DriftingSquareGrating(BaseProtocol):

    ####################################################
    ### Used to make fullfield ROTATION "optic flow" ###
    ####################################################

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

class SplitDriftingSquareGrating(BaseProtocol):

    ###################################################
    ### Used to make fullfield FORWARD "optic flow" ###
    ###################################################

    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def loadStimuli(self, client):
        passed_parameters_0 = self.epoch_parameters[0].copy()
        passed_parameters_1 = self.epoch_parameters[1].copy()
    
        bg = self.run_parameters.get('idle_color')
        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        multicall.load_stim(name='ConstantBackground', color=[bg,bg,bg,1], side_length=200)
        multicall.load_stim(**passed_parameters_0, hold=True)
        multicall.load_stim(**passed_parameters_1, hold=True)
        multicall()

    def getEpochParameters(self):
        # TODO: center size with aperture (center and center_size)
        current_angle = self.selectParametersFromLists(self.protocol_parameters['angle'], randomize_order = self.protocol_parameters['randomize_order'])
        self.epoch_parameters = {}

        self.epoch_parameters[0] = {'name': 'RotatingGrating',
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
        self.epoch_parameters[1] = {'name': 'RotatingGrating',
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

class OpticFlowExperiment(BaseProtocol):

    ##################################################
    ### Concatenate multiple types of stimuli here ###
    ##################################################

        def __init__(self, cfg):
            super().__init__(cfg)
            self.cfg = cfg
            #self.stim_list = ['DriftingSquareGrating', 'SplitDriftingSquareGrating']
            self.stim_list = ['DriftingSquareGrating']


            

            #n = [4, 4]  # weight each stim draw by how many trial types it has. Total = 20
            #avg_per_stim = int(self.run_parameters['num_epochs'] / np.sum(n)) 
            #all_stims = [[self.stim_list[i]] * n[i] * avg_per_stim for i in range(len(n))]

            all_stims = [[self.stim_list[i]] * 10 for i in range(len(self.stim_list))]

            self.stim_order = np.random.permutation(np.hstack(all_stims))
            print(self.stim_order)

            # initialize each component class
            self.initComponentClasses()

            self.getRunParameterDefaults()
            self.getParameterDefaults()

            #self.run_parameters['num_epochs'] = 4

        def initComponentClasses(self):
            # pre-populate dict of component classes. Each with its own num_epochs_completed counter etc
            self.component_classes = {}
            for stim_type in self.stim_list:

                if stim_type == 'DriftingSquareGrating':
                    new_component_class = DriftingSquareGrating(self.cfg)

                    # COMMENTING THIS OUT. WILL GET SET IN THE CLASSES ABOVE
                    # RESSURECT IF I WANT TO LOOP OVER SPEEDS OR SOMETHING LIKE THAT

                    # new_component_class.protocol_parameters = {'diameter': [5.0, 15.0, 50.0],
                    #                                            'intensity': [0.0, 1.0],
                    #                                            'center': [0, 0],
                    #                                            'speed': [-80.0, 80.0],
                    #                                            'angle': 0.0,
                    #                                            'randomize_order': True}

                elif stim_type == 'SplitDriftingSquareGrating':
                    new_component_class = SplitDriftingSquareGrating(self.cfg)
                    # new_component_class.protocol_parameters = {'width': 10.0,
                    #                                            'height': 120.0,
                    #                                            'intensity': [0.0, 1.0],
                    #                                            'center': [0, 0],
                    #                                            'speed': 80.0,
                    #                                            'angle': [0.0, 180.0],
                    #                                            'randomize_order': True}

                # Lock component stim timing run params to suite run params
                new_component_class.run_parameters['pre_time'] = self.run_parameters['pre_time']
                new_component_class.run_parameters['stim_time'] = self.run_parameters['stim_time']
                new_component_class.run_parameters['tail_time'] = self.run_parameters['tail_time']
                new_component_class.run_parameters['idle_color'] = self.run_parameters['idle_color']

                self.component_classes[stim_type] = new_component_class

        def getEpochParameters(self):
            print(self.num_epochs_completed)
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
            self.run_parameters = {'protocol_ID': 'OpticFlowExperiment',
                                   'num_epochs': 10, # 80 = 16 * 5 averages each
                                   'pre_time': 0.1,
                                   'stim_time': 0.1,
                                   'tail_time': 0,
                                   'idle_color': 0.5}

