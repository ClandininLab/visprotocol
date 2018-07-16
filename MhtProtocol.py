#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 10:20:02 2018

@author: mhturner
"""

import ClandininLabProtocol
from flystim.launch import StimManager
from flystim.screen import Screen
import numpy as np
from sys import platform

class MhtProtocol(ClandininLabProtocol.ClandininLabProtocol):
    def __init__(self):
        super().__init__()
        # # # Define your data directory # # #             
        if platform == "darwin": #OSX (laptop, for dev.)
            self.data_directory = '/Users/mhturner/documents/stashedObjects'
        elif platform == "win32": #Windows (rig computer)
            self.data_directory = '/Users/Main/Documents/Data'

        # # # Parameters for the screen # # # 
        if platform == "darwin": #OSX (laptop, for dev.)
            FullScreen = False
            ScreenID = 0
        elif platform == "win32": #Windows (rig computer)
            FullScreen = True
            ScreenID = 1
            
        # Define screen(s) for the rig you use
        w = 14.2e-2; h = 9e-2; # meters of image at projection plane, screen only shows 9x9 of this
        zDistToScreen = 5.36e-2; # meters
        screens = [Screen(width=w, height=h, rotation=None, offset=(0, zDistToScreen, 0), id=ScreenID, fullscreen=FullScreen, vsync=None,
                     square_side=2e-2, square_loc='lr')]
    
        # # # Other metadata defaults. These can be changed in the gui as well # # #
        self.experimenter = 'MHT'
        self.rig = 'Bruker'

        # # #  List of your protocol IDs # # # 
        self.protocolIDList = ['CheckerboardWhiteNoise',
                               'DriftingSquareGrating',
                               'MovingRectangle',
                               'MovingSquareMapping']
        
        # # # Start the stim manager and set the frame tracker square to black # # #
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

            epoch_parameters = {'theta_period':2*protocol_parameters['checker_width'],
                                'phi_period':2*protocol_parameters['checker_width'],
                                'rand_min':0.0,
                                'rand_max':1.0,
                                'start_seed':start_seed,
                                'update_rate':protocol_parameters['update_rate']}

        elif protocol_ID == 'DriftingSquareGrating':
            stimulus_ID = 'RotatingBars'
            
            currentAngle = self.selectCurrentParameterFromList(protocol_parameters['angle'], randomize_flag = protocol_parameters['randomize_order'])
            
            epoch_parameters = {'period':protocol_parameters['period'],
                                'duty_cycle':0.5,
                                'rate':protocol_parameters['rate'],
                                'color':protocol_parameters['color'],
                                'background':protocol_parameters['background'],
                                'angle':currentAngle}
            
        elif protocol_ID == 'MovingRectangle':
            stimulus_ID = 'MovingPatch'
            
            elevation = protocol_parameters['elevation']
            speed = protocol_parameters['speed']
            stim_time = self.run_parameters['stim_time']
            # TODO: handle high level trajectory definitions for this protocol
            startPoint = (0,0,elevation)
            endPoint = (stim_time,0 + speed * stim_time,elevation)            
            
            epoch_parameters = {'theta_width':protocol_parameters['theta_width'],
                                'phi_width':protocol_parameters['phi_width'],
                                'color':protocol_parameters['color'],
                                'background':self.run_parameters['idle_color'],
                                'trajectory':[startPoint, endPoint]}

        elif protocol_ID == 'MovingSquareMapping':
            stimulus_ID = 'MovingPatch'
            if self.num_epochs_completed == 0: #new run: initialize location sequences
                location_sequence = np.concatenate((protocol_parameters['azimuth_locations'] ,
                                                   protocol_parameters['elevation_locations']))
                movement_axis_sequence = np.concatenate((np.ones(len(protocol_parameters['azimuth_locations'])) ,
                                                   2*np.ones(len(protocol_parameters['elevation_locations']))))
                self.persistent_parameters = {'movement_axis_sequence':movement_axis_sequence,
                              'location_sequence':location_sequence}
                    
            # TODO: handle True/False parameters
            draw_ind = np.mod(self.num_epochs_completed,len(self.persistent_parameters['location_sequence']))
            if draw_ind == 0 and protocol_parameters['randomize_order']:
                rand_inds = np.random.permutation(len(self.persistent_parameters['location_sequence']))
                self.persistent_parameters['movement_axis_sequence'] = list(np.array(self.persistent_parameters['movement_axis_sequence'])[rand_inds])
                self.persistent_parameters['location_sequence'] = list(np.array(self.persistent_parameters['location_sequence'])[rand_inds])
                
            # select current locations from sequence
            if self.persistent_parameters['movement_axis_sequence'][draw_ind] == 1:
                current_movement_axis = 'azimuth'
            elif self.persistent_parameters['movement_axis_sequence'][draw_ind] == 2:
                current_movement_axis = 'elevation'
            current_location = self.persistent_parameters['location_sequence'][draw_ind]

            #where does the square begin? Should be just off screen...
            startingAzimuth = 20.0; startingElevation = 40.0;
            speed = protocol_parameters['speed']
            stim_time = self.run_parameters['stim_time']
            
            if current_movement_axis == 'elevation': #movement along elevation, for a given azimuth
                startPoint = (0,startingAzimuth,current_location)
                endPoint = (stim_time,startingAzimuth + speed * stim_time,current_location)    
            elif current_movement_axis == 'azimuth': #movement along azimuth, for a given elevation
                startPoint = (0,current_location,startingElevation)
                endPoint = (stim_time,current_location, startingElevation + speed * stim_time)     

            epoch_parameters = {'theta_width':protocol_parameters['square_width'],
                                'phi_width':protocol_parameters['square_width'],
                                'color':protocol_parameters['color'],
                                'background':self.run_parameters['idle_color'],
                                'trajectory':[startPoint, endPoint]}
            
            convenience_parameters = {'speed':speed,
                                      'current_movement_axis':current_movement_axis,
                                      'current_location':current_location,
                                      'randomize_order':protocol_parameters['randomize_order']}
            
        else:
            raise NameError('Unrecognized stimulus ID')
            
        return stimulus_ID, epoch_parameters, convenience_parameters
    
    
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
            
        elif protocol_ID == 'MovingRectangle':
            params = {'theta_width':10.0,
                       'phi_width':30.0,
                       'color':0.0,
                       'elevation': 90.0,
                       'speed':60.0}
            
        elif protocol_ID == 'MovingSquareMapping':
            params = {'square_width':10.0,
                       'color':0.0,
                       'elevation_locations': [60.0, 70.0, 80.0, 90.0, 100.0, 110.0, 120.0], # 60...120
                       'azimuth_locations': [40.0, 50.0, 60.0, 70.0, 80.0, 90.0], #40...140
                       'speed':60.0,
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
