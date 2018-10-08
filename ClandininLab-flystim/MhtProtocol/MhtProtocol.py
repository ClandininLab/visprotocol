#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 10:20:02 2018

@author: mhturner
"""

import ClandininLabProtocol
from flystim.screen import Screen
import numpy as np
from sys import platform
from math import pi

from flyrpc.launch import launch_server
import flystim.stim_server
import flyrpc.echo_server


class BaseProtocol(ClandininLabProtocol.ClandininLabProtocol):
    def __init__(self):
        super().__init__()
        # # # Define your data directory # # #             
        if platform == "darwin": #OSX (laptop, for dev.)
            self.data_directory = '/Users/mhturner/documents/stashedObjects'
            host = '127.0.0.1'
            port = 60629
            use_server = False
        elif platform == "win32": #Windows (rig computer)
            self.data_directory = 'E:/Max/FlystimData/'
            host = '192.168.1.232'
            port = 60629
            use_server = True

    
        # # # Other metadata defaults. These can be changed in the gui as well # # #
        self.experimenter = 'MHT'
        self.rig = 'Bruker'

        # # #  List of your protocol IDs # # # 
        self.protocolIDList = ['CheckerboardWhiteNoise',
                               'DriftingSquareGrating',
                               'ExpandingMovingSquare',
                               'FlickeringPatch',
                               'MovingRectangle',
                               'MovingSquareMapping',
                               'SequentialOrRandomMotion',
                               'SparseBinaryNoise',
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
            self.manager = launch_server(flyrpc.echo_server, host=host, port=port, auto_stop=False)
        else:
            w = 15.75e-2; h = 12.6e-2; # meters of image at projection plane
            screens = [Screen(width=w, height=h, rotation=-pi/4, offset=(5.0e-2, 6.1e-2, -6.1e-2), fullscreen=False, vsync=None)]
            # TODO: pass screen into launch_server
            self.manager = launch_server(flystim.stim_server, setup_name='macbook', auto_stop=True)
        
        self.manager.black_corner_square()
        self.manager.set_idle_background(0)


    # Convenience functions shared across protocols...
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
