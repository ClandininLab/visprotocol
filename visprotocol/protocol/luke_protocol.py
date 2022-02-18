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

class ConstantBackground(BaseProtocol):

    ##################################
    ### Used for long grey periods ###
    ##################################

    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):

        self.epoch_parameters = {'name': 'ConstantBackground',
                                 'color': [0.5, 0.5, 0.5, 1]}

    def getParameterDefaults(self):
        self.protocol_parameters = {}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'ConstantBackground',
                               'num_epochs': 10,
                               'pre_time': 0,
                               'stim_time': 5.0,
                               'tail_time': 0,
                               'idle_color': 0.5}

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
                               'stim_time': 0.5,
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
        passed_parameters = self.epoch_parameters.copy()
        #passed_parameters_1 = self.epoch_parameters[1].copy()
    
        bg = self.run_parameters.get('idle_color')
        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        multicall.load_stim(name='ConstantBackground', color=[bg,bg,bg,1], side_length=200)
        multicall.load_stim(**passed_parameters, hold=True)
        passed_parameters['angle'] = 180
        multicall.load_stim(**passed_parameters, hold=True)
        multicall()

    def getEpochParameters(self):
        # TODO: center size with aperture (center and center_size)
        #current_angle = self.selectParametersFromLists(self.protocol_parameters['angle'], randomize_order = self.protocol_parameters['randomize_order'])
        self.epoch_parameters = {}

        self.epoch_parameters = {'name': 'RotatingGrating',
                                 'period': self.protocol_parameters['period'],
                                 'rate': self.protocol_parameters['rate'],
                                 'color': [1, 1, 1, 1],
                                 'mean': self.protocol_parameters['mean'],
                                 'contrast': self.protocol_parameters['contrast'],
                                 'angle': self.protocol_parameters['angle'],
                                 'offset': 0.0,
                                 'cylinder_radius': 1,
                                 'cylinder_location': (self.protocol_parameters['cylinder_xshift'],0,0),
                                 'cylinder_height': 10,
                                 'profile': 'square',
                                 'theta': self.screen_center[0]}

        self.meta_parameters = {'center_size': self.protocol_parameters['center_size'],
                                'center': self.adjustCenter(self.protocol_parameters['center'])}

    def getParameterDefaults(self):
        self.protocol_parameters = {'period': 20.0,
                                    'rate': 20.0,
                                    'contrast': 1.0,
                                    'mean': 0.5,
                                    'angle': 0.0,
                                    'center': [0, 0],
                                    'center_size': 180.0,
                                    'cylinder_xshift': -0.001,
                                    'randomize_order': True,
                                    }

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'SplitDriftingSquareGrating',
                               'num_epochs': 40,
                               'pre_time': 0,
                               'stim_time': 0.5,
                               'tail_time': 0.1,
                               'idle_color': 0.5}

class OpticFlowExperiment(BaseProtocol):

    ##################################################
    ### Concatenate multiple types of stimuli here ###
    ##################################################

    def __init__(self, cfg):
        super().__init__(cfg)
        self.cfg = cfg
        self.getRunParameterDefaults()
        self.getParameterDefaults()

        ############################# SET THESE ##############################
        # How long should a cluster of epochs be?
        epoch_cluster_duration = 1 #in min
        epoch_cluster_duration *= 60 # now in sec

        # What stimuli and how to weight them?
        self.stim_list = ['DriftingSquareGrating', 'SplitDriftingSquareGrating']#'SplitDriftingSquareGrating']
        stim_weights = [2,1]

        #################### FORM A SINGLE EPOCH CLUSTER ####################
        # calculate duration of an epoch (a single stim presentation)
        epoch_duration = self.run_parameters['pre_time'] + \
                         self.run_parameters['stim_time'] + \
                         self.run_parameters['tail_time']

        # given the duration of a single epoch and a cluster of epochs, how many epochs to present?
        num_epochs_in_cluster = int(epoch_cluster_duration / epoch_duration)
        
        # create a list that contains the correct number of each stim
        stim_per_unit = int(num_epochs_in_cluster / np.sum(stim_weights))
        all_stims = [[self.stim_list[i]] * stim_weights[i] * stim_per_unit for i in range(len(self.stim_list))]
        self.stim_order = list(np.random.permutation(np.hstack(all_stims))) # Randomize list

        #Update num epochs in cluster since could have decreased by a few due to rounding down
        num_epochs_in_cluster = int(stim_per_unit * np.sum(stim_weights))
        print(num_epochs_in_cluster)
        #self.run_parameters['num_epochs'] = num_epochs_in_cluster
        #####################################################################

        self.stim_order.append('ConstantBackground')

        self.stim_order = self.stim_order + self.stim_order + self.stim_order
        # so currently this should take 4.5 min

        self.run_parameters['num_epochs'] = len(self.stim_order)

        # initialize each component class
        self.initComponentClasses()

    def initComponentClasses(self):
        print('init')
        # pre-populate dict of component classes. Each with its own num_epochs_completed counter etc
        self.component_classes = {}
        for stim_type in ['DriftingSquareGrating', 'SplitDriftingSquareGrating', 'ConstantBackground']:

            if stim_type == 'DriftingSquareGrating':
                new_component_class = DriftingSquareGrating(self.cfg)
                new_component_class.run_parameters = self.run_parameters
                #new_component_class.run_parameters['stim_time'] = 0.1

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
                new_component_class.run_parameters = self.run_parameters
                #new_component_class.run_parameters['stim_time'] = 0.2

            elif stim_type == 'ConstantBackground':
                new_component_class = ConstantBackground(self.cfg)
                new_component_class.run_parameters = self.run_parameters
                #new_component_class.run_parameters['stim_time'] = 2

            # if stim_type in ['DriftingSquareGrating', 'SplitDriftingSquareGrating']:
                # Lock component stim timing run params to suite run params
                # new_component_class.run_parameters['pre_time'] = self.run_parameters['pre_time']
                # new_component_class.run_parameters['stim_time'] = 5 #self.run_parameters['stim_time']
                # new_component_class.run_parameters['tail_time'] = self.run_parameters['tail_time']
                # new_component_class.run_parameters['idle_color'] = self.run_parameters['idle_color']



            self.component_classes[stim_type] = new_component_class
            print("init stim time: {}".format(new_component_class.run_parameters['stim_time']))

    def getEpochParameters(self):
        print(self.num_epochs_completed)
        stim_type = str(self.stim_order[self.num_epochs_completed]) # note this num_epochs_completed is for the whole suite, not component stim!
        self.convenience_parameters = {'component_stim_type': stim_type}
        self.component_class = self.component_classes[stim_type]
        #print(stim_type)
        #print(self.component_class.run_parameters['stim_time'])
        if stim_type in ['DriftingSquareGrating', 'SplitDriftingSquareGrating']:
            self.component_class.run_parameters['stim_time'] = 0.5
        if stim_type == 'ConstantBackground':
            self.component_class.run_parameters['stim_time'] = 30

        self.component_class.getEpochParameters()
        self.convenience_parameters.update(self.component_class.convenience_parameters)
        self.epoch_parameters = self.component_class.epoch_parameters

        self.run_parameters = self.component_class.run_parameters
        
        self.run_parameters['num_epochs'] = len(self.stim_order)

        #self.run_parameters['stim_time'] = 5

    def loadStimuli(self, client):
        self.component_class.loadStimuli(client)
        self.component_class.advanceEpochCounter() # up the component class epoch counter

    def getParameterDefaults(self):
        self.protocol_parameters = {}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'OpticFlowExperiment',
                               'num_epochs': 0, # this will get reset above
                               'pre_time': 0.1,
                               'stim_time': 0.5,
                               'tail_time': 0,
                               'idle_color': 0.5}

