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
from math import pi


class MhtProtocol(ClandininLabProtocol.ClandininLabProtocol):
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

    
        # # # Other metadata defaults. These can be changed in the gui as well # # #
        self.experimenter = 'MHT'
        self.rig = 'Bruker'

        # # #  List of your protocol IDs # # # 
        self.protocolIDList = ['CheckerboardWhiteNoise',
                               'DriftingSquareGrating',
                               'MovingRectangle',
                               'ExpandingMovingSquare',
                               'SpeedTuningSquare',
                               'MovingSquareMapping',
                               'SequentialOrRandomMotion',
                               'FlickeringPatch']
        # # #  List of fly metadata # # # 
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
                                'rand_min':protocol_parameters['rand_min'],
                                'rand_max':protocol_parameters['rand_max'],
                                'start_seed':start_seed,
                                'update_rate':protocol_parameters['update_rate'],
                                'distribution_type':protocol_parameters['distribution_type']}

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
            convenience_parameters = {'currentAngle': currentAngle,
                                      'center':protocol_parameters['center'],
                                      'speed':protocol_parameters['speed'],
                                      'color':protocol_parameters['color'],
                                      'height':protocol_parameters['height'],
                                      'width':protocol_parameters['width']}
            
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
            convenience_parameters = {'currentWidth': currentWidth,
                                      'center':protocol_parameters['center'],
                                      'angle':protocol_parameters['angle'],
                                      'speed':protocol_parameters['speed'],
                                      'color':protocol_parameters['color']}
            
        elif protocol_ID == 'SpeedTuningSquare':
            stimulus_ID = 'MovingPatch'
            
            currentSpeed = self.selectCurrentParameterFromList(protocol_parameters['speed'], randomize_flag = protocol_parameters['randomize_order'])
            
            centerX = protocol_parameters['center'][0]
            centerY = protocol_parameters['center'][1]
            angle = protocol_parameters['angle']
            width = protocol_parameters['width']
            stim_time = self.run_parameters['stim_time']
            
            distance_to_travel = 120 # deg
            #travel time in sec, at start of stim_time. Remaining stim_time spot just hangs at the end of the trajectory
            travel_time = distance_to_travel / currentSpeed  
            
            startX = (0,centerX - np.cos(np.radians(angle)) * distance_to_travel/2)
            startY = (0,centerY - np.sin(np.radians(angle)) * distance_to_travel/2)
            endX = (travel_time, centerX + np.cos(np.radians(angle)) * distance_to_travel/2)
            endY = (travel_time, centerY + np.sin(np.radians(angle)) * distance_to_travel/2)
            
            if  travel_time < stim_time:
                hangX = (stim_time, centerX + np.cos(np.radians(angle)) * distance_to_travel/2)
                hangY = (stim_time, centerY + np.sin(np.radians(angle)) * distance_to_travel/2)
                x = [startX, endX, hangX]
                y = [startY, endY, hangY]
            elif travel_time >= stim_time:
                print('Warning: stim_time is too short to show whole trajectory')
                x = [startX, endX]
                y = [startY, endY]

            trajectory = RectangleTrajectory(x = x,
                                                  y = y,
                                                  angle = angle,
                                                  h = width,
                                                  w = width,
                                                  color = protocol_parameters['color']).to_dict()   

            epoch_parameters = {'name':stimulus_ID,
                                'background':self.run_parameters['idle_color'],
                                'trajectory':trajectory}
            convenience_parameters = {'width': width,
                                      'center':protocol_parameters['center'],
                                      'angle':angle,
                                      'currentSpeed':currentSpeed,
                                      'color':protocol_parameters['color']}
            

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
                                      'randomize_order':protocol_parameters['randomize_order'],
                                      'square_width':protocol_parameters['square_width'],
                                      'color':protocol_parameters['color']}
            
            
        elif protocol_ID == 'SequentialOrRandomMotion':
            stimulus_ID = 'MovingPatch'

            stim_time = self.run_parameters['stim_time']
            no_steps = protocol_parameters['no_steps']
            
            time_steps = np.linspace(0,stim_time,no_steps)
            x_steps = np.linspace(protocol_parameters['azimuth_boundaries'][0],protocol_parameters['azimuth_boundaries'][1],no_steps)
            y_steps = np.linspace(protocol_parameters['elevation'],protocol_parameters['elevation'],no_steps)
            
            #switch back and forth between sequential and random
            randomized_order = bool(np.mod(self.num_epochs_completed,2))
            if randomized_order:
                x_steps = np.random.permutation(x_steps)
            
            # time-modulated trajectories
            x = Trajectory(list(zip(time_steps,x_steps)), kind = 'previous') #note interp kind is previous
            y = Trajectory(list(zip(time_steps,y_steps)), kind = 'previous')
            # constant trajectories:
            w = Trajectory(protocol_parameters['square_width'])
            h = Trajectory(protocol_parameters['square_width'])
            angle = Trajectory(0)
            color = Trajectory(protocol_parameters['color'])
            trajectory = {'x': x.to_dict(), 'y': y.to_dict(), 'w': w.to_dict(), 'h': h.to_dict(),
                'angle': angle.to_dict(), 'color': color.to_dict()}

            epoch_parameters = {'name':stimulus_ID,
                                'background':self.run_parameters['idle_color'],
                                'trajectory':trajectory}
            convenience_parameters = {'square_width':protocol_parameters['square_width'],
                                      'angle':0,
                                      'color':protocol_parameters['color'],
                                      'elevation':protocol_parameters['elevation'],
                                      'azimuth_boundaries':protocol_parameters['azimuth_boundaries'],
                                      'no_steps':protocol_parameters['no_steps'],
                                      'randomized_order':randomized_order,
                                      'x_steps':x_steps}
            
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
            convenience_parameters = {'current_temporal_frequency':current_temporal_frequency,
                                      'center':protocol_parameters['center'],
                                      'width':protocol_parameters['width'],
                                      'height':protocol_parameters['height']}
            
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
                       'update_rate':0.5,
                       'rand_min': 0.0,
                       'rand_max':1.0,
                       'distribution_type':'binary'}
            
        elif protocol_ID == 'DriftingSquareGrating':
            params = {'period':20.0,
                       'rate':20.0,
                       'color':1.0,
                       'background':0,
                       'angle':[0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0],
                       'randomize_order':True}
            
        elif protocol_ID == 'MovingRectangle':
            params = {'width':5.0,
                       'height':5.0,
                       'color':0.0,
                       'center': [55.0, 120],
                       'speed':60.0,
                       'angle': [0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0],
                       'randomize_order':True}
            
        elif protocol_ID == 'ExpandingMovingSquare':
            params = {'width':[2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0],
                       'color':0.0,
                       'center': [55.0, 120.0],
                       'speed':60.0,
                       'angle': 0.0,
                       'randomize_order':True}

        elif protocol_ID == 'SpeedTuningSquare':
            params = {'width': 5.0,
                       'color':0.0,
                       'center': [55.0, 120.0],
                       'speed':[20.0, 40.0, 60.0, 80.0, 100.0, 120.0, 140.0, 160.0, 180.0, 200.0],
                       'angle': 0.0,
                       'randomize_order':True}
            
        elif protocol_ID == 'MovingSquareMapping':
            params = {'square_width':5.0,
                       'color':0.0,
                       'elevation_locations': [100.0, 105.0, 110.0, 115.0, 120.0, 125.0, 130.0, 135.0, 140.0], # 100...140
                       'azimuth_locations': [30.0, 35.0, 40.0, 45.0, 50.0, 55.0, 60.0, 65.0, 70.0, 75.0, 80.0], #30...80
                       'speed':60.0,
                       'randomize_order':True}
            
        elif protocol_ID == 'SequentialOrRandomMotion':
            params = {'square_width':5.0,
                       'color':0.0,
                       'elevation': 120.0,
                       'azimuth_boundaries': [40.0, 70.0],
                       'no_steps': 12}
            
        elif protocol_ID == 'FlickeringPatch':
            params = {'height':5.0,
                       'width':5.0,
                       'center': [55.0, 120.0],
                       'temporal_frequency': [1.0, 2.0, 4.0, 8.0, 16.0, 32.0],
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
