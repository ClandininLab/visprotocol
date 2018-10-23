#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 16 15:58:53 2018

@author: mhturner
"""

import ClandininLabProtocol
from flystim.screen import Screen
import numpy as np
from sys import platform
from math import pi

from flyrpc.launch import launch_server
from flyrpc.transceiver import MySocketClient
import flystim.stim_server

class BaseProtocol(ClandininLabProtocol.ClandininLabProtocol):
    def __init__(self):
        super().__init__()
        # # # Define your data directory # # #             
        self.data_directory = '/Users/mhturner/documents/stashedObjects'
        host = '0.0.0.0'
        port = 60629

        # # # Parameters for the screen # # # 
        # Define screen(s) for the rig you use
        w = 15.75e-2; h = 12.6e-2; # meters of image at projection plane
        screens = [Screen(width=w, height=h, rotation=-pi/4, offset=(5.0e-2, 6.1e-2, -6.1e-2), fullscreen=True, vsync=None, id=1)]
    
        # # # Other metadata defaults. These can be changed in the gui as well # # #
        self.experimenter = 'MyName'
        self.rig = 'Leica'

        # # #  List of your protocol IDs # # # 
        self.protocolIDList = ['CheckerboardWhiteNoise',
                               'DriftingSquareGrating']
        
        # # #  List of fly metadata # # # 
        self.prepChoices = ['Left optic lobe',
                            'Right optic lobe',
                            'Whole brain']
        self.driverChoices = ['L2 (21Dhh)']
        self.indicatorChoices = ['GCaMP6f']
        
        # # # Start the stim manager and set the frame tracker square to black # # #
        self.manager = launch_server(flystim.stim_server, setup_name='macbook', auto_stop=True)
        
        self.manager.black_corner_square()
        self.manager.set_idle_background(0)
    
    
    # Convenience functions across protocols...
    def selectCurrentParameterFromList(self, parameter_string):
        
        if self.num_epochs_completed == 0: #new run: initialize location sequences
            parameter_sequence = self.protocol_parameters[parameter_string]
            if type(parameter_sequence) is not list:
                parameter_sequence = [parameter_sequence] #somebody probably entered a float instead of a list in the GUI
            self.persistent_parameters = {'parameter_sequence':parameter_sequence}
                
        draw_ind = np.mod(self.num_epochs_completed,len(self.persistent_parameters['parameter_sequence']))
        if draw_ind == 0 and self.protocol_parameters['randomize_order']:
            rand_inds = np.random.permutation(len(self.persistent_parameters['parameter_sequence']))
            self.persistent_parameters['parameter_sequence'] = list(np.array(self.persistent_parameters['parameter_sequence'])[rand_inds])
            
        current_parameter = self.persistent_parameters['parameter_sequence'][draw_ind]
        return current_parameter
