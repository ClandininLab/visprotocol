#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 16 15:58:53 2018

@author: mhturner
"""

import ClandininLabProtocol
from flystim.launch import StimClient, StimManager
from flystim.screen import Screen
import numpy as np
from sys import platform
from math import pi

class ExampleProtocol(ClandininLabProtocol.ClandininLabProtocol):
    def __init__(self):
        super().__init__()
        # # # Define your data directory # # #             
        if platform == "darwin": #OSX (laptop, for dev.)
            self.data_directory = '/Users/mhturner/documents/stashedObjects'
            addr = ('127.0.0.1', 60629)
            use_server = False
        elif platform == "win32": #Windows (rig computer)
            self.data_directory = 'E:/Max/FlystimData/'
            addr = ('192.168.1.232', 60629)
            use_server = True

        # # # Parameters for the screen # # # 
        # Define screen(s) for the rig you use
        w = 14.2e-2; h = 9e-2; # meters of image at projection plane, screen only shows 9x9 of this
        zDistToScreen = 5.36e-2; # meters
        screens = [Screen(width=w, height=h, rotation=None, offset=(0, zDistToScreen, 0), id=0, fullscreen=False, vsync=None,
                     square_side=2e-2, square_loc='lr')]
    
        # # # Other metadata defaults. These can be changed in the gui as well # # #
        self.experimenter = 'MyName'
        self.rig = 'Bruker'

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
        if use_server:
            self.manager = StimClient(addr = addr) # use a server on rig computer
        else:
            w = 15.75e-2; h = 12.6e-2; # meters of image at projection plane
            screens = [Screen(width=w, height=h, rotation=-pi/4, offset=(5.0e-2, 6.1e-2, -6.1e-2), fullscreen=False, vsync=None)]
            self.manager = StimManager(screens)
        
        self.manager.black_corner_square()
        self.manager.set_idle_background(0)
    def getEpochParameters(self, protocol_ID, protocol_parameters, epoch):
        """
        This function selects the stimulus parameters sent to FlyStim for each epoch
        The protocol parameters are defined by the user, while the epoch parameters need to 
        correspond to parameters that flystim expects to receive for the stimulus
        You can define any mapping from protocol_parameters to epoch_parameters you
        would like. Any epoch_parameters you don't pass will revert to the flystim
        default
        """
        if self.num_epochs_completed == 0:
            self.persistent_parameters = {}
        convenience_parameters = {}
        if protocol_ID == 'CheckerboardWhiteNoise':
            stimulus_ID = 'RandomGrid' #underlying flystim stimulus_ID
            
            start_seed = int(np.random.choice(range(int(1e6))))

            epoch_parameters = {'name':stimulus_ID,
                                'theta_period':protocol_parameters['checker_width'],
                                'phi_period':protocol_parameters['checker_width'],
                                'rand_min':0.0,
                                'rand_max':1.0,
                                'start_seed':start_seed,
                                'update_rate':protocol_parameters['update_rate']}

        elif protocol_ID == 'DriftingSquareGrating':
            stimulus_ID = 'RotatingBars'
            
            currentAngle = self.selectCurrentParameterFromList(protocol_parameters['angle'], randomize_flag = protocol_parameters['randomize_order'])
            
            epoch_parameters = {'name':stimulus_ID,
                                'period':protocol_parameters['period'],
                                'duty_cycle':0.5,
                                'rate':protocol_parameters['rate'],
                                'color':protocol_parameters['color'],
                                'background':protocol_parameters['background'],
                                'angle':currentAngle}

        else:
            raise NameError('Unrecognized stimulus ID')
            
        return epoch_parameters, convenience_parameters
    
    
    def getParameterDefaults(self, protocol_ID):
        """    
        For each protocol, default protocol parameters are stored here:
        These will be used to populate the GUI, and are not directly passed to flystim
        so you can use high-level protocol parameters here that will be converted
        to lower-level flystim parameters in your getEpochParameters() function
        """
        if protocol_ID == 'CheckerboardWhiteNoise':
            params = {'checker_width':5.0,
                       'update_rate':60.0}
            
        elif protocol_ID == 'DriftingSquareGrating':
            params = {'period':20.0,
                       'rate':40.0,
                       'color':1.0,
                       'background':0.5,
                       'angle':[0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0],
                       'randomize_order':True}

        else:
            raise NameError('Unrecognized stimulus ID')         
            
        return params
    
    def selectCurrentParameterFromList(self, parameter_list, randomize_flag = False):
        if self.num_epochs_completed == 0: #new run: initialize location sequences
            parameter_sequence = parameter_list
            self.persistent_parameters = {'parameter_sequence':parameter_sequence}
                
        draw_ind = np.mod(self.num_epochs_completed,len(self.persistent_parameters['parameter_sequence']))
        if draw_ind == 0 and randomize_flag:
            rand_inds = np.random.permutation(len(self.persistent_parameters['parameter_sequence']))
            self.persistent_parameters['parameter_sequence'] = list(np.array(self.persistent_parameters['parameter_sequence'])[rand_inds])
            
        current_parameter = self.persistent_parameters['parameter_sequence'][draw_ind]
        return current_parameter
