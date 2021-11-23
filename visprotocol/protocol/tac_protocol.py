#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Last update 2021 Mar 14

@author: tacurrier and mhturner
"""

from visprotocol.protocol import clandinin_protocol
import numpy as np
import flyrpc.multicall

from flystim.trajectory import Trajectory

class BaseProtocol(clandinin_protocol.BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)  # call the parent class init method

# %%

class TwoColorNoise(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        adj_center = self.adjustCenter(self.protocol_parameters['center'])

        start_seed_1 = int(np.random.choice(range(int(1e6))))
        start_seed_2 = int(np.random.choice(range(int(1e6))))

        distribution_data = {'name': 'Ternary',
                             'args': [],
                             'kwargs': {'rand_min': self.protocol_parameters['rand_min'],
                                        'rand_max': self.protocol_parameters['rand_max']}}

        grid_1_parameters = {'name': 'RandomGridOnSphericalPatch',
                         'patch_width': 15,
                         'patch_height': 15,
                         'width': self.protocol_parameters['grid_width'],
                         'height': self.protocol_parameters['grid_height'],
                         'start_seed': start_seed_1,
                         'update_rate': self.protocol_parameters['update_rate'],
                         'distribution_data': distribution_data,
                         'theta': adj_center[0]+20,
                         'phi': adj_center[1],
                         'color': [1, 0, 0, 1],
                         'sphere_radius': 2}

        grid_2_parameters = {'name': 'RandomGridOnSphericalPatch',
                         'patch_width': 15,
                         'patch_height': 15,
                         'width': self.protocol_parameters['grid_width'],
                         'height': self.protocol_parameters['grid_height'],
                         'start_seed': start_seed_2,
                         'update_rate': self.protocol_parameters['update_rate'],
                         'distribution_data': distribution_data,
                         'theta': adj_center[0]-20,
                         'phi': adj_center[1],
                         'color': [0, 0, 1, 1],
                         'sphere_radius': 1}

        self.epoch_parameters = (grid_1_parameters, grid_2_parameters)

        self.convenience_parameters = {'start_seed_1': start_seed_1,
                                    'start_seed_2': start_seed_2}

    def loadStimuli(self, client):
        grid_1_parameters = self.epoch_parameters[0].copy()
        grid_2_parameters = self.epoch_parameters[1].copy()

        multicall = flyrpc.multicall.MyMultiCall(client.manager)
        bg = self.run_parameters.get('idle_color')
        multicall.load_stim('ConstantBackground', color=[bg, bg, bg, 1.0])
        multicall.load_stim(**grid_1_parameters, hold=True)
        multicall.load_stim(**grid_2_parameters, hold=True)

        multicall()

    def getParameterDefaults(self):
        self.protocol_parameters = {'patch_size': 5.0,
                                'update_rate': 20.0,
                                'rand_min': 0.0,
                                'rand_max': 1.0,
                                'grid_width': 60,
                                'grid_height': 60,
                                'center': [0.0, 0.0]}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'TwoColorNoise',
                           'num_epochs': 10,
                           'pre_time': 2.0,
                           'stim_time': 30.0,
                           'tail_time': 2.0,
                           'idle_color': 0.5}

# %%

class SpotPair(BaseProtocol):
 def __init__(self, cfg):
     super().__init__(cfg)

     self.getRunParameterDefaults()
     self.getParameterDefaults()

 def getEpochParameters(self):
     current_speed_2 = self.selectParametersFromLists(self.protocol_parameters['speed_2'], randomize_order=self.protocol_parameters['randomize_order'])

     center = self.protocol_parameters['center']
     center_1 = [center[0], center[1] + self.protocol_parameters['y_separation']/2]
     spot_1_parameters =  self.getMovingSpotParameters(color=[1, 0, 0, 1],
                                                       radius=self.protocol_parameters['diameter'][0]/2,
                                                       center=center_1,
                                                       speed=self.protocol_parameters['speed_1'],
                                                       angle=0)
     center_2 = [center[0], center[1] - self.protocol_parameters['y_separation']/2]
     spot_2_parameters =  self.getMovingSpotParameters(color=[0, 0, 1, 1],
                                                       radius=self.protocol_parameters['diameter'][1]/2,
                                                       center=center_2,
                                                       speed=current_speed_2,
                                                       angle=0)


     self.epoch_parameters = (spot_1_parameters, spot_2_parameters)

     self.convenience_parameters = {'current_speed_2': current_speed_2}

 def loadStimuli(self, client):
     spot_1_parameters = self.epoch_parameters[0].copy()
     spot_2_parameters = self.epoch_parameters[1].copy()

     multicall = flyrpc.multicall.MyMultiCall(client.manager)
     bg = self.run_parameters.get('idle_color')
     multicall.load_stim('ConstantBackground', color=[bg, bg, bg, 1.0])
     multicall.load_stim(**spot_1_parameters, hold=True)
     multicall.load_stim(**spot_2_parameters, hold=True)

     multicall()

 def getParameterDefaults(self):
     self.protocol_parameters = {'diameter': [5.0, 5.0],
                                 'intensity': [0.0, 0.0],
                                 'center': [0, 0],
                                 'y_separation': 7.0,
                                 'speed_1': 80.0,
                                 'speed_2': [-80.0, -40.0, 0.0, 40.0, 80.0],
                                 'randomize_order': True}

 def getRunParameterDefaults(self):
     self.run_parameters = {'protocol_ID': 'SpotPair',
                            'num_epochs': 40,
                            'pre_time': 0.5,
                            'stim_time': 4.0,
                            'tail_time': 1.0,
                            'idle_color': 0.5}


# %%

class SearchStimulus(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        adj_center = self.adjustCenter(self.protocol_parameters['center'])

        current_intensity = self.selectParametersFromLists(self.protocol_parameters['intensity'], randomize_order=self.protocol_parameters['randomize_order'])

        self.epoch_parameters = {'name': 'MovingPatch',
                                 'width': self.protocol_parameters['width'],
                                 'height': self.protocol_parameters['height'],
                                 'sphere_radius': 1,
                                 'color': current_intensity,
                                 'theta': adj_center[0],
                                 'phi': adj_center[1],
                                 'angle': 0}
        self.convenience_parameters = {'current_intensity': current_intensity}

    def getParameterDefaults(self):
        self.protocol_parameters = {'height': 20.0,
                                    'width': 20.0,
                                    'center': [0, 0],
                                    'intensity': [1.0, 0.0],
                                    'randomize_order': False}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'SearchStimulus',
                               'num_epochs': 10,
                               'pre_time': 1.0,
                               'stim_time': 0.5,
                               'tail_time': 1.0,
                               'idle_color': 0.5}
  # %%

class SphericalCheckerboardWhiteNoise(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        stimulus_ID = 'RandomGridOnSphericalPatch'
        adj_center = self.adjustCenter(self.protocol_parameters['center'])

        start_seed = int(np.random.choice(range(int(1e6))))

        distribution_data = {'name': 'Ternary',
                             'args': [],
                             'kwargs': {'rand_min': self.protocol_parameters['rand_min'],
                                        'rand_max': self.protocol_parameters['rand_max']}}

        self.epoch_parameters = {'name': stimulus_ID,
                                 'patch_width': self.protocol_parameters['patch_size'],
                                 'patch_height': self.protocol_parameters['patch_size'],
                                 'width': self.protocol_parameters['grid_width'],
                                 'height': self.protocol_parameters['grid_height'],
                                 'start_seed': start_seed,
                                 'update_rate': self.protocol_parameters['update_rate'],
                                 'distribution_data': distribution_data,
                                 'theta': adj_center[0],
                                 'phi': adj_center[1]}

        self.convenience_parameters = {'start_seed': start_seed}

    def getParameterDefaults(self):
        self.protocol_parameters = {'patch_size': 5.0,
                                    'update_rate': 20.0,
                                    'rand_min': 0.0,
                                    'rand_max': 1.0,
                                    'grid_width': 60,
                                    'grid_height': 60,
                                    'center': [0.0, 0.0]}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'SphericalCheckerboardWhiteNoise',
                               'num_epochs': 10,
                               'pre_time': 2.0,
                               'stim_time': 30.0,
                               'tail_time': 2.0,
                               'idle_color': 0.5}


        # %%

class UniformFlash(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        adj_center = self.adjustCenter(self.protocol_parameters['center'])

        current_intensity = self.selectParametersFromLists(self.protocol_parameters['intensity'], randomize_order=self.protocol_parameters['randomize_order'])

        self.epoch_parameters = {'name': 'MovingPatch',
                                 'width': self.protocol_parameters['width'],
                                 'height': self.protocol_parameters['height'],
                                 'sphere_radius': 1,
                                 'color': current_intensity,
                                 'theta': adj_center[0],
                                 'phi': adj_center[1],
                                 'angle': 0}
        self.convenience_parameters = {'current_intensity': current_intensity}

    def getParameterDefaults(self):
        self.protocol_parameters = {'height': 120.0,
                                    'width': 120.0,
                                    'center': [0, 0],
                                    'intensity': [1.0, 0.0],
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'UniformFlash',
                               'num_epochs': 10,
                               'pre_time': 1.0,
                               'stim_time': 0.5,
                               'tail_time': 1.0,
                               'idle_color': 0.5}

        # %%


class MovingRectangle(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        current_angle = self.selectParametersFromLists(self.protocol_parameters['angle'], randomize_order=self.protocol_parameters['randomize_order'])

        self.epoch_parameters = self.getMovingPatchParameters(angle=current_angle, color=self.protocol_parameters['intensity'])

        self.convenience_parameters = {'current_angle': current_angle}

    def getParameterDefaults(self):
        self.protocol_parameters = {'width': 5.0,
                                    'height': 5.0,
                                    'intensity': 0.0,
                                    'center': [0, 0],
                                    'speed': 80.0,
                                    'angle': [0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0],
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'MovingRectangle',
                               'num_epochs': 40,
                               'pre_time': 0.5,
                               'stim_time': 2.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}

        # %%


class FlickeringPatch(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        adj_center = self.adjustCenter(self.protocol_parameters['center'])

        current_temporal_frequency = self.selectParametersFromLists(self.protocol_parameters['temporal_frequency'], randomize_order=self.protocol_parameters['randomize_order'])

        # make color trajectory
        color_traj = {'name': 'Sinusoid',
                      'temporal_frequency': current_temporal_frequency,
                      'amplitude': self.protocol_parameters['mean'] * self.protocol_parameters['contrast'],
                      'offset': self.protocol_parameters['mean']}

        self.epoch_parameters = {'name': 'MovingPatch',
                                 'width': self.protocol_parameters['width'],
                                 'height': self.protocol_parameters['height'],
                                 'sphere_radius': 1,
                                 'color': color_traj,
                                 'theta': adj_center[0],
                                 'phi': adj_center[1],
                                 'angle': 0}

        self.convenience_parameters = {'current_temporal_frequency': current_temporal_frequency}

    def getParameterDefaults(self):
        self.protocol_parameters = {'height': 10.0,
                                    'width': 10.0,
                                    'center': [0, 0],
                                    'contrast': 1.0,
                                    'mean': 0.5,
                                    'temporal_frequency': [0.5, 1.0, 2.0, 4.0, 8.0, 16.0],
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'FlickeringPatch',
                               'num_epochs': 30,
                               'pre_time': 1.0,
                               'stim_time': 4.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}

        # %%


class DriftingSquareGrating(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        # TODO: center size with aperture (center and center_size)
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
                                    'angle': [0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0],
                                    'center': [0, 0],
                                    'center_size': 180.0,
                                    'randomize_order': True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'DriftingSquareGrating',
                               'num_epochs': 40,
                               'pre_time': 1.0,
                               'stim_time': 4.0,
                               'tail_time': 1.0,
                               'idle_color': 0.5}


        # %%
"""
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # MULTI-COMPONENT STIMS # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""

class MedullaSuite(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.cfg = cfg
        self.stim_list = ['FlickeringPatch', 'DriftingSquareGrating', 'MovingRectangle', 'UniformFlash']
        n = [3, 2, 2, 2]  # weight each stim draw by how many trial types it has
        avg_per_stim = int(self.run_parameters['num_epochs'] / np.sum(n))
        all_stims = [[self.stim_list[i]] * n[i] * avg_per_stim for i in range(len(n))]

        self.stim_order = np.random.permutation(np.hstack(all_stims))

        # initialize each component class
        self.initComponentClasses()

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def initComponentClasses(self):
        # pre-populate dict of component classes. Each with its own num_epochs_completed counter etc
        self.component_classes = {}
        for stim_type in self.stim_list:

            if stim_type == 'DriftingSquareGrating':
                new_component_class = DriftingSquareGrating(self.cfg)
                new_component_class.protocol_parameters = {'period': 20.0,
                                                           'rate': 20.0,
                                                           'contrast': 1.0,
                                                           'mean': 0.5,
                                                           'angle': [0.0, 180.0],
                                                           'center': [0, 0],
                                                           'center_size': 180.0,
                                                           'randomize_order': True}

            elif stim_type == 'UniformFlash':
                new_component_class = UniformFlash(self.cfg)
                new_component_class.protocol_parameters = {'height': 240.0,
                                                           'width': 240.0,
                                                           'center': [0, 0],
                                                           'intensity': [1.0, 0.0],
                                                           'randomize_order': True}

            elif stim_type == 'FlickeringPatch':
                new_component_class = FlickeringPatch(self.cfg)
                new_component_class.protocol_parameters = {'height': 30.0,
                                                           'width': 30.0,
                                                           'center': [0, 0],
                                                           'contrast': 1.0,
                                                           'mean': 0.5,
                                                           'temporal_frequency': [1.0, 2.0, 8.0],
                                                           'randomize_order': True}

            elif stim_type == 'MovingRectangle':
                new_component_class = MovingRectangle(self.cfg)
                new_component_class.protocol_parameters = {'width': 20.0,
                                                           'height': 120.0,
                                                           'intensity': 0.0,
                                                           'center': [0, 0],
                                                           'speed': 80.0,
                                                           'angle': [0.0, 180.0],
                                                           'randomize_order': True}

            # Lock component stim timing run params to suite run params
            new_component_class.run_parameters['pre_time'] = self.run_parameters['pre_time']
            new_component_class.run_parameters['stim_time'] = self.run_parameters['stim_time']
            new_component_class.run_parameters['tail_time'] = self.run_parameters['tail_time']
            new_component_class.run_parameters['idle_color'] = self.run_parameters['idle_color']

            self.component_classes[stim_type] = new_component_class

    def getEpochParameters(self):
        stim_type = str(self.stim_order[self.num_epochs_completed]) # note this num_epochs_completed is for the whole suite, not component stim!
        self.convenience_parameters = {'component_stim_type': stim_type}
        self.component_class = self.component_classes[stim_type]

        self.component_class.getEpochParameters()
        self.convenience_parameters.update(self.component_class.convenience_parameters)
        self.epoch_parameters = self.component_class.epoch_parameters

    def loadStimuli(self, client):
        self.component_class.loadStimuli(client)
        self.component_class.advanceEpochCounter() # up the component class epoch counter

    def getParameterDefaults(self):
        self.protocol_parameters = {}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID': 'MedullaSuite',
                               'num_epochs': 200, #200 = 20 * 10 averages each
                               'pre_time': 1.5,
                               'stim_time': 3.0,
                               'tail_time': 1.5,
                               'idle_color': 0.5}
