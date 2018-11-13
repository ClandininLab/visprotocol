#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 10:20:02 2018

@author: mhturner
"""

import ClandininLabProtocol
from flystim.screen import Screen
import numpy as np
import socket
from math import pi

from flystim.stim_server import launch_stim_server
from flyrpc.transceiver import MySocketClient



class BaseProtocol(ClandininLabProtocol.ClandininLabProtocol):
    def __init__(self):
        super().__init__()
        # # # Define your data directory # # #             
        if socket.gethostname() == "MHT-laptop": # (laptop, for dev.)
            self.data_directory = '/Users/mhturner/documents/stashedObjects'
            host = '0.0.0.0'
            port = 60629
            use_server = False
            self.send_ttl = False
        else:
            self.data_directory = 'E:/Max/FlystimData/'
            host = '192.168.1.232'
            port = 60629
            use_server = True
            self.send_ttl = True

    
        # # # Other metadata defaults. These can be changed in the gui as well # # #
        self.experimenter = 'MHT'
        self.rig = 'Bruker'

        # # #  List of your protocol IDs # # # 
        self.protocolIDList = ['CheckerboardWhiteNoise',
                               'DriftingSquareGrating',
                               'ExpandingMovingSquare',
                               'FlickeringPatch',
                               'LoomingPatch',
                               'MovingRectangle',
                               'MovingSquareMapping',
                               'SequentialOrRandomMotion',
                               'SineTrajectoryPatch',
                               'SpeedTuningSquare',
                               'StationaryMapping',
                               'SparseNoise']
        
        # # #  Lists of fly metadata # # # 
        self.prepChoices = ['Left optic lobe',
                            'Right optic lobe',
                            'Whole brain']
        self.driverChoices = ['L2 (21Dhh)','LC11 (R22H02; R20G06)','LC17 (R21D03; R65C12)',
                              'LC18 (R82D11; R92B11)', 'LC26 (VT007747; R85H06)', 
                              'LC9 (VT032961; VT040569)','LC20 (R17A04, R35B06)']
        self.indicatorChoices = ['GCaMP6f',
                                 'GCaMP6m',
                                 'ASAP2f',
                                 'ASAP4c',
                                 '10_90_GCaMP6f',
                                 'SF-iGluSnFR.A184V']

        
        # # # Start the stim manager and set the frame tracker square to black # # #
        if use_server:
            self.manager = MySocketClient(host=host, port=port)
        else:
            w = 15.75e-2; h = 12.6e-2; # meters of image at projection plane
            screens = [Screen(width=w, height=h, rotation=-pi/4, offset=(5.0e-2, 6.1e-2, -6.1e-2), fullscreen=False, vsync=None)]
            self.manager = launch_stim_server(screens)
        
        self.manager.black_corner_square()
        self.manager.set_idle_background(0)


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
