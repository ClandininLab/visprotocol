#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from visprotocol.protocol import clandinin_protocol
import flyrpc.multicall
import numpy as np

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
class LoomRandomlySpaced(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def precomputeEpochParameters(self):
        # Calculate ITIs probabilistically (tail_time)
        # Randomly spaced ITIs, drawn from a uniform distribution between avg_iti - 1 and avg_iti + 1
        total_loom_dur = self.run_parameters['num_epochs'] * self.run_parameters['stim_time']
        num_itis = self.run_parameters['num_epochs'] - 1
        avg_iti = (self.run_parameters['run_time'] - total_loom_dur) / num_itis
        iti_lo = max(avg_iti - 1, 0)
        iti_hi = min(avg_iti + 1, self.run_parameters['run_time'])
        self.itis = np.random.uniform(iti_lo, iti_hi, int(self.run_parameters['num_epochs']))

    def getEpochParameters(self):
        current_color = self.selectParametersFromLists(self.protocol_parameters['color'], randomize_order = self.protocol_parameters['randomize_order'])
        self.epoch_parameters = {'name': 'LoomingCircle',
                                 'radius': self.protocol_parameters['radius'],
                                 'color': current_color,
                                 'starting_distance': self.protocol_parameters['start_distance'],
                                 'speed': self.protocol_parameters['speed'],
                                 'n_steps': 36}
        iti = self.itis[self.num_epochs_completed]
        self.run_parameters['tail_time'] = iti

        self.convenience_parameters = {'current_color': current_color, 'current_tail_time': iti}

    def getParameterDefaults(self):
        self.protocol_parameters = {'radius': 0.005,
                                    'start_distance': 0.5,
                                    'speed': -0.25,
                                    'color': [0.0],
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'LoomRandomlySpaced',
                               'num_epochs': 2,
                               'pre_time': 0.0,
                               'stim_time': 2.0,
                               'run_time': 6.0,
                               'pre_run_time': 0.0,
                               'idle_color': 0.5}

class Loom(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        
        self.epoch_parameters = {'name': 'LoomingCircle',
                                 'radius': self.protocol_parameters['radius'],
                                 'color': self.protocol_parameters['color'],
                                 'starting_distance': self.protocol_parameters['start_distance'],
                                 'speed': self.protocol_parameters['speed'],
                                 'n_steps': 36}

    def getParameterDefaults(self):
        self.protocol_parameters = {'radius': 0.005,
                                    'start_distance': 0.125,
                                    'speed': -0.25,
                                    'color': 0.0,
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'Loom',
                               'num_epochs': 2,
                               'pre_time': 0.5,
                               'stim_time': 0.5,
                               'tail_time': 0.5,
                               'idle_color': 1.0}


class LoomRandomlySpacedRV(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def precomputeEpochParameters(self):
        # Calculate ITIs probabilistically (tail_time)
        # Randomly spaced ITIs, drawn from a uniform distribution between avg_iti - 1 and avg_iti + 1
        total_loom_dur = self.run_parameters['num_epochs'] * self.run_parameters['stim_time']
        num_itis = self.run_parameters['num_epochs'] - 1
        avg_iti = (self.run_parameters['run_time'] - total_loom_dur) / num_itis
        iti_lo = max(avg_iti - 1, 0)
        iti_hi = min(avg_iti + 1, self.run_parameters['run_time'])
        self.itis = np.random.uniform(iti_lo, iti_hi, int(self.run_parameters['num_epochs']))

    def getEpochParameters(self):
        current_color = self.selectParametersFromLists(self.protocol_parameters['color'], randomize_order = self.protocol_parameters['randomize_order'])

        loom_trajectory = {'name': 'Loom', 'rv_ratio': self.protocol_parameters['rv_ratio'], 'stim_time': self.run_parameters['stim_time'], 'start_size': self.protocol_parameters['start_size'], 'end_size': self.protocol_parameters['end_size']}

        adj_center = self.adjustCenter(self.protocol_parameters['center'])
        
        self.epoch_parameters = {'name': 'MovingSpot',
                                 'radius': loom_trajectory,
                                 'sphere_radius': 1,
                                 'color': current_color,
                                 'theta': adj_center[0],
                                 'phi': adj_center[1]}

        iti = self.itis[self.num_epochs_completed]
        self.run_parameters['tail_time'] = iti

        self.convenience_parameters = {'current_color': current_color, 'current_tail_time': iti}

    def getParameterDefaults(self):
        self.protocol_parameters = {'rv_ratio': 0.04,
                                    'start_size': 10.0,
                                    'end_size': 100.0,
                                    'color': [0.0],
                                    'center': [0.0, 0.0],
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'LoomRandomlySpacedRV',
                               'num_epochs': 40,
                               'pre_time': 0.0,
                               'stim_time': 0.5,
                               'run_time': 300.0,
                               'pre_run_time': 300.0,
                               'idle_color': 0.5}

class LoomPlusGrating(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        current_rv_ratio, current_grate_rate = self.selectParametersFromLists((self.protocol_parameters['rv_ratio'], self.protocol_parameters['grate_rate']),
                                                                                 all_combinations=True,
                                                                                 randomize_order = self.protocol_parameters['randomize_order'])


        # (1) Make the looming spot parameter dictionary
        stim_time = self.run_parameters['stim_time']
        start_size = self.protocol_parameters['start_size']
        end_size = self.protocol_parameters['end_size']

        # adjust center to screen center
        adj_center = self.adjustCenter(self.protocol_parameters['center'])

        current_rv_ratio = current_rv_ratio / 1e3  # msec -> sec
        r_traj = {'name': 'Loom',
                  'rv_ratio': current_rv_ratio,
                  'stim_time': stim_time,
                  'start_size': start_size,
                  'end_size': end_size}

        loom_parameters = {'name': 'MovingSpot',
                             'radius': r_traj,
                             'sphere_radius': 0.5,
                             'color': self.protocol_parameters['loom_color'],
                             'theta': adj_center[0],
                             'phi': adj_center[1]}

        # (1) Make the grating parameter dictionary
        grate_parameters = {'name': 'RotatingGrating',
                            'period': self.protocol_parameters['grate_period'],
                            'rate': current_grate_rate,
                            'color': [1, 1, 1, 1],
                            'mean': self.run_parameters['idle_color'],
                            'contrast': self.protocol_parameters['grate_contrast'],
                            'angle': self.protocol_parameters['angle'],
                            'offset': 0.0,
                            'cylinder_radius': 1.1,
                            'cylinder_height': 20,
                            'profile': 'square',
                            'theta': self.screen_center[0]}

        self.epoch_parameters = (grate_parameters, loom_parameters)
        self.convenience_parameters = {'current_rv_ratio': current_rv_ratio,
                                       'current_grate_rate': current_grate_rate}

    def loadStimuli(self, client):
        grate_parameters = self.epoch_parameters[0].copy()
        loom_parameters = self.epoch_parameters[1].copy()

        bg = self.run_parameters.get('idle_color')
        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        multicall.load_stim(**grate_parameters, hold=True)
        multicall.load_stim(**loom_parameters, hold=True)
        multicall()

    def getParameterDefaults(self): #populates the default numbers in the GUI
        self.protocol_parameters = {'center': [0, 0],
                                    'loom_color': 0.0,
                                    'rv_ratio': [30.0, 60.0, 90.0],  # msec
                                    'start_size': 2.5, # degrees
                                    'end_size': 60, # degrees
                                    'grate_period': 10.0,  # spatial period of grating, degrees
                                    'grate_rate': [-20, 0, 20],  # grating speed, deg/sec
                                    'grate_contrast': 0.5,  # spatial contrast of the grating
                                    'angle': 0, # roll angle, degrees
                                    'randomize_order': True}

    def getRunParameterDefaults(self): #params shared across all protocols
        self.run_parameters = {'protocol_ID': 'LoomPlusGrating',
                               'num_epochs': 10,
                               'pre_time': 1.0,
                               'stim_time': 4.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}


class DriftingSquareGrating(BaseProtocol):
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

    def getParameterDefaults(self): #populates the default numbers in the GUI
        self.protocol_parameters = {'period': 20.0,
                                    'rate': 20.0,
                                    'contrast': 1.0,
                                    'mean': 0.5,
                                    'angle': [0.0, 90.0, 180.0, 270.0],
                                    'center': [0, 0],
                                    'center_size': 180.0,
                                    'randomize_order': True}

    def getRunParameterDefaults(self): #params shared across all protocols
        self.run_parameters = {'protocol_ID': 'DriftingSquareGrating',
                               'num_epochs': 10,
                               'pre_time': 1.0,
                               'stim_time': 4.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}
