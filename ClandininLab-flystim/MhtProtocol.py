#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 10:20:02 2018

@author: mhturner
"""

import ClandininLabProtocol
from flystim.launch import StimClient, StimManager
from flystim.screen import Screen
import numpy as np
from sys import platform
from flystim.trajectory import RectangleTrajectory, Trajectory

# TODO: send trigger for bruker acquisition
# TODO: split up sub-protocols maybe?
class MhtProtocol(ClandininLabProtocol.ClandininLabProtocol):
    def __init__(self):
        super().__init__()
        # # # Define your data directory # # #             
        if platform == "darwin": #OSX (laptop, for dev.)
            self.data_directory = '/Users/mhturner/documents/stashedObjects'
            addr = ('127.0.0.1', 60629)
            use_server = False
        elif platform == "win32": #Windows (rig computer)
            self.data_directory = '/Users/User/Documents/ExperimentDataFiles'
            addr = ('192.168.1.232', 60629)
            use_server = True

    
        # # # Other metadata defaults. These can be changed in the gui as well # # #
        self.experimenter = 'MHT'
        self.rig = 'Bruker'

        # # #  List of your protocol IDs # # # 
        self.protocolIDList = ['CheckerboardWhiteNoise',
                               'DriftingSquareGrating',
                               'MovingRectangle',
                               'ExpandingMovingSquare',
                               'MovingSquareMapping',
                               'FlickeringPatch']
        
        # # # Start the stim manager and set the frame tracker square to black # # #
        if use_server:
            self.manager = StimClient(addr = addr) # use a server on rig computer
        else:
            screens = [Screen(fullscreen=False, vsync=None)]
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
            
        elif protocol_ID == 'MovingRectangle':
            stimulus_ID = 'MovingPatch'
            
            currentAngle = self.selectCurrentParameterFromList(protocol_parameters['angle'], randomize_flag = protocol_parameters['randomize_order'])
            
            centerX = protocol_parameters['center'][0]
            centerY = protocol_parameters['center'][1]
            speed = protocol_parameters['speed']
            stim_time = self.run_parameters['stim_time']
            distance_to_travel = speed * stim_time
            
            startX = (0,centerX - np.cos(np.radians(currentAngle)) * distance_to_travel/2)
            endX = (stim_time, centerX + np.cos(np.radians(currentAngle)) * distance_to_travel/2)
            startY = (0,centerY - np.sin(np.radians(currentAngle)) * distance_to_travel/2)
            endY = (stim_time, centerY + np.sin(np.radians(currentAngle)) * distance_to_travel/2)

            trajectory = RectangleTrajectory(x=[startX, endX],
                                                  y=[startY, endY],
                                                  angle=currentAngle,
                                                  h = protocol_parameters['height'],
                                                  w = protocol_parameters['width'],
                                                  color = protocol_parameters['color']).to_dict()   

            epoch_parameters = {'name':stimulus_ID,
                                'background':self.run_parameters['idle_color'],
                                'trajectory':trajectory}
            convenience_parameters = {'currentAngle': currentAngle}
            
        elif protocol_ID == 'ExpandingMovingSquare':
            stimulus_ID = 'MovingPatch'
            
            currentWidth = self.selectCurrentParameterFromList(protocol_parameters['width'], randomize_flag = protocol_parameters['randomize_order'])
            
            centerX = protocol_parameters['center'][0]
            centerY = protocol_parameters['center'][1]
            angle = protocol_parameters['angle']
            speed = protocol_parameters['speed']
            stim_time = self.run_parameters['stim_time']
            distance_to_travel = speed * stim_time
            
            startX = (0,centerX - np.cos(np.radians(angle)) * distance_to_travel/2)
            endX = (stim_time, centerX + np.cos(np.radians(angle)) * distance_to_travel/2)
            startY = (0,centerY - np.sin(np.radians(angle)) * distance_to_travel/2)
            endY = (stim_time, centerY + np.sin(np.radians(angle)) * distance_to_travel/2)

            trajectory = RectangleTrajectory(x = [startX, endX],
                                                  y = [startY, endY],
                                                  angle = angle,
                                                  h = currentWidth,
                                                  w = currentWidth,
                                                  color = protocol_parameters['color']).to_dict()   

            epoch_parameters = {'name':stimulus_ID,
                                'background':self.run_parameters['idle_color'],
                                'trajectory':trajectory}
            convenience_parameters = {'currentWidth': currentWidth}

        elif protocol_ID == 'MovingSquareMapping':
            stimulus_ID = 'MovingPatch'
            if self.num_epochs_completed == 0: #new run: initialize location sequences
                location_sequence = np.concatenate((protocol_parameters['azimuth_locations'] ,
                                                   protocol_parameters['elevation_locations']))
                movement_axis_sequence = np.concatenate((np.ones(len(protocol_parameters['azimuth_locations'])) ,
                                                   2*np.ones(len(protocol_parameters['elevation_locations']))))
                self.persistent_parameters = {'movement_axis_sequence':movement_axis_sequence,
                              'location_sequence':location_sequence}
                    
            draw_ind = np.mod(self.num_epochs_completed,len(self.persistent_parameters['location_sequence']))
            if draw_ind == 0 and protocol_parameters['randomize_order']:
                rand_inds = np.random.permutation(len(self.persistent_parameters['location_sequence']))
                self.persistent_parameters['movement_axis_sequence'] = list(np.array(self.persistent_parameters['movement_axis_sequence'])[rand_inds])
                self.persistent_parameters['location_sequence'] = list(np.array(self.persistent_parameters['location_sequence'])[rand_inds])
                
            # select current locations from sequence
            if self.persistent_parameters['movement_axis_sequence'][draw_ind] == 1:
                current_search_axis = 'azimuth' #current location is an azimuth, movement along elevation
            elif self.persistent_parameters['movement_axis_sequence'][draw_ind] == 2:
                current_search_axis = 'elevation' #current location is an elevation, movement along azimuth
            current_location = self.persistent_parameters['location_sequence'][draw_ind]

            #where does the square begin? Should be just off screen...
            startingAzimuth = 20.0; startingElevation = 40.0;
            speed = protocol_parameters['speed']
            stim_time = self.run_parameters['stim_time']
            
            if current_search_axis == 'elevation': #move along x (azimuth)
                startX = (0,startingAzimuth)
                endX = (stim_time,startingAzimuth + speed * stim_time)    
                startY = (0,current_location)
                endY = (stim_time,current_location)    
            elif current_search_axis == 'azimuth':  #move along y (elevation)
                startX = (0,current_location)
                endX = (stim_time,current_location)
                startY = (0,startingElevation)
                endY = (stim_time,startingElevation + speed * stim_time)   

            trajectory = RectangleTrajectory(x = [startX, endX],
                                                 y = [startY, endY],
                                                 angle=0,
                                                 h = protocol_parameters['square_width'],
                                                 w = protocol_parameters['square_width'],
                                                 color = protocol_parameters['color']).to_dict()
            
            epoch_parameters = {'name':stimulus_ID,
                                'background':self.run_parameters['idle_color'],
                                'trajectory': trajectory}

            convenience_parameters = {'speed':speed,
                                      'current_search_axis':current_search_axis,
                                      'current_location':current_location,
                                      'randomize_order':protocol_parameters['randomize_order']}
            
            
        elif protocol_ID == 'FlickeringPatch':
            stimulus_ID = 'MovingPatch'
            stim_time = self.run_parameters['stim_time']
            
            current_temporal_frequency = self.selectCurrentParameterFromList(protocol_parameters['temporal_frequency'], randomize_flag = protocol_parameters['randomize_order'])

            trajectory_sample_rate = 100 # Hz
            nPoints = trajectory_sample_rate * stim_time
            time_points = np.linspace(0, stim_time, nPoints)
            color_values = np.sin(time_points * 2 * np.pi * current_temporal_frequency)
            color_trajectory = list(zip(time_points,color_values))

            trajectory = RectangleTrajectory(x = protocol_parameters['center'][0],
                                                  y = protocol_parameters['center'][1],
                                                  angle = 0,
                                                  h = protocol_parameters['height'],
                                                  w = protocol_parameters['width'],
                                                  color = color_trajectory).to_dict()   

            epoch_parameters = {'name':stimulus_ID,
                                'background':self.run_parameters['idle_color'],
                                'trajectory':trajectory}
            convenience_parameters = {'current_temporal_frequency':current_temporal_frequency}
            
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
            params = {'checker_width':10.0,
                       'update_rate':60.0}
            
        elif protocol_ID == 'DriftingSquareGrating':
            params = {'period':20.0,
                       'rate':40.0,
                       'color':1.0,
                       'background':0.5,
                       'angle':[0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0],
                       'randomize_order':True}
            
        elif protocol_ID == 'MovingRectangle':
            params = {'width':10.0,
                       'height':30.0,
                       'color':0.0,
                       'center': [90.0, 120.0],
                       'speed':60.0,
                       'angle': [0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0],
                       'randomize_order':True}
            
        elif protocol_ID == 'ExpandingMovingSquare':
            params = {'width':[5.0, 10.0, 20.0, 30.0, 40.0, 50.0],
                       'color':0.0,
                       'center': [90.0, 120.0],
                       'speed':60.0,
                       'angle': 0.0,
                       'randomize_order':True}
            
        elif protocol_ID == 'MovingSquareMapping':
            params = {'square_width':10.0,
                       'color':0.0,
                       'elevation_locations': [100.0, 110.0, 120.0, 130.0, 140.0], # 100...140
                       'azimuth_locations': [60.0, 70.0, 80.0, 90.0, 100.0, 110.0, 120.0], #60...120
                       'speed':60.0,
                       'randomize_order':True}
            
        elif protocol_ID == 'FlickeringPatch':
            params = {'height':10.0,
                       'width':10.0,
                       'center': [90.0, 120.0],
                       'temporal_frequency': [2.0, 4.0, 8.0, 16.0],
                       'randomize_order':True}
        else:
            raise NameError('Unrecognized stimulus ID')         
            
        return params
    
    def selectCurrentParameterFromList(self, parameter_list, randomize_flag = False):
        if self.num_epochs_completed == 0: #new run: initialize location sequences
            parameter_sequence = parameter_list
            if type(parameter_sequence) is not list:
                parameter_sequence = [parameter_sequence] #somebody probably entered a float instead of a list in the GUI
            self.persistent_parameters = {'parameter_sequence':parameter_sequence}
                
        draw_ind = np.mod(self.num_epochs_completed,len(self.persistent_parameters['parameter_sequence']))
        if draw_ind == 0 and randomize_flag:
            rand_inds = np.random.permutation(len(self.persistent_parameters['parameter_sequence']))
            self.persistent_parameters['parameter_sequence'] = list(np.array(self.persistent_parameters['parameter_sequence'])[rand_inds])
            
        current_parameter = self.persistent_parameters['parameter_sequence'][draw_ind]
        return current_parameter
