#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 10:20:02 2018

@author: mhturner
"""

#!/usr/bin/env python3

import ClandininLabProtocol
from flystim.launch import StimManager
from flystim.screen import Screen

from datetime import datetime
import numpy.random as random
import squirrel
from sys import platform
# TODO: repeated use of the same screen, e.g. re-initialize or replace screen maybe? Button in GUI?
# TODO: interrupt mid-run. Threading?

class MhtProtocol(ClandininLabProtocol.ClandininLabProtocol):
    def __init__(self):
        super().__init__()
        # TODO: hdf5 experiment file. GUI for expt file initialization?
        
        # # # Where to find the experiment metadata file # # # 
        if platform == "darwin":
            self.data_directory = '/Users/mhturner/documents/stashedObjects/'
        elif platform == "win32":
            self.data_directory = '/Users/Main/Documents/Data/'
        self.date = datetime.now().isoformat()[:-16]
        try: # Load initialized metadata file
            self.experiment_file = squirrel.get(self.date, self.data_directory)
        except FileNotFoundError as e:
            raise NameError('Initialize experiment file first using initialize_experiment_file')
            
        # # #  List of your protocol IDs # # # 
        self.protocolIDList = ['CheckerboardWhiteNoise',
                               'RotatingSquareGrating',
                               'MovingRectangle']
        
            
        # # # Define screen(s) for the rig you use # # #
        w = 14.2e-2; h = 9e-2; # m of image at projection plane, screen only shows 9x9 of this
        zDistToScreen = 5.36e-2; # m
    
        screens = [Screen(width=w, height=h, rotation=None, offset=(0, zDistToScreen, 0), id=0, fullscreen=False, vsync=None,
                     square_side=2e-2, square_loc='lr')]
        self.manager = StimManager(screens)
        self.manager.black_corner_square()


    def getEpochParameters(self, protocol_ID, protocol_parameters, epoch):
        """
        This function selects the stimulus parameters sent to FlyStim for each epoch
        The protocol parameters are defined by the user, while the epoch parameters need to 
        correspond to parameters that flystim expects to receive for the stimulus
        You can define any mapping from protocol_parameters to epoch_parameters you
        would like. Any epoch_parameters you don't pass will revert to the flystim
        default
        """
        if protocol_ID == 'CheckerboardWhiteNoise':
            stimulus_ID = 'RandomGrid' #underlying flystim stimulus_ID
            epoch_parameters = protocol_parameters
            epoch_parameters['start_seed'] = int(random.choice(range(int(1e6))))
            
            
        elif protocol_ID == 'RotatingSquareGrating':
            stimulus_ID = 'RotatingBars'
            epoch_parameters = protocol_parameters
            
        elif protocol_ID == 'MovingRectangle':
            stimulus_ID = 'MovingPatch'
            epoch_parameters = {'theta_width':protocol_parameters['theta_width'],
                       'phi_width':protocol_parameters['phi_width'],
                       'color':protocol_parameters['color'],
                       'background':protocol_parameters['background']}
            
            
            elevation = protocol_parameters['elevation']
            speed = protocol_parameters['speed']
            stim_time = self.run_parameters['stim_time']
            # TODO: handle high level trajectory definitions for this protocol
            startPoint = (0,0,elevation)
            endPoint = (stim_time,0 + speed * stim_time,elevation)
            epoch_parameters['trajectory'] = [startPoint, endPoint]
            
        else:
            raise NameError('Unrecognized stimulus ID')
            
        return stimulus_ID, epoch_parameters
    
    
    def getParameterDefaults(self, protocol_ID):
        """    
        For each protocol, default protocol parameters are stored here:
        These will be used to populate the GUI, and are not directly passed to flystim
        so you can use high-level protocol parameters here that will be converted
        to lower-level flystim parameters in your getEpochParameters() function
        """
        if protocol_ID == 'CheckerboardWhiteNoise':
            params = {'theta_period':15.0,
                       'phi_period':15.0,
                       'rand_min':0.0,
                       'rand_max':1.0,
                       'start_seed':0,
                       'update_rate':60.0}
            
        elif protocol_ID == 'RotatingSquareGrating':
            params = {'period':20.0,
                       'duty_cycle':0.5,
                       'rate':10.0,
                       'color':1.0,
                       'background':0.5,
                       'angle':0.0}
            
        elif protocol_ID == 'MovingRectangle':
            params = {'theta_width':10.0,
                       'phi_width':30.0,
                       'color':0.0,
                       'background':0.5,
                       'elevation': 90.0,
                       'speed':60.0}
        
        else:
            raise NameError('Unrecognized stimulus ID')         
            
        return params
