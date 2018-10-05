import numpy as np
from flystim.trajectory import Trajectory

class SequentialOrRandomMotion():
    def getEpochParameters(protocolObject):
        stimulus_ID = 'MovingPatch'

        stim_time = protocolObject.run_parameters['stim_time']
        no_steps = protocolObject.protocol_parameters['no_steps']
        
        time_steps = np.linspace(0,stim_time,no_steps)
        x_steps = np.linspace(protocolObject.protocol_parameters['azimuth_boundaries'][0],protocolObject.protocol_parameters['azimuth_boundaries'][1],no_steps)
        y_steps = np.linspace(protocolObject.protocol_parameters['elevation'],protocolObject.protocol_parameters['elevation'],no_steps)
        
        #switch back and forth between sequential and random
        randomized_order = bool(np.mod(protocolObject.num_epochs_completed,2))
        if randomized_order:
            x_steps = np.random.permutation(x_steps)
        
        # time-modulated trajectories
        x = Trajectory(list(zip(time_steps,x_steps)), kind = 'previous') #note interp kind is previous
        y = Trajectory(list(zip(time_steps,y_steps)), kind = 'previous')
        # constant trajectories:
        w = Trajectory(protocolObject.protocol_parameters['square_width'])
        h = Trajectory(protocolObject.protocol_parameters['square_width'])
        angle = Trajectory(0)
        color = Trajectory(protocolObject.protocol_parameters['color'])
        trajectory = {'x': x.to_dict(), 'y': y.to_dict(), 'w': w.to_dict(), 'h': h.to_dict(),
            'angle': angle.to_dict(), 'color': color.to_dict()}

        epoch_parameters = {'name':stimulus_ID,
                            'background':protocolObject.run_parameters['idle_color'],
                            'trajectory':trajectory}
        convenience_parameters = {'square_width':protocolObject.protocol_parameters['square_width'],
                                  'angle':0,
                                  'color':protocolObject.protocol_parameters['color'],
                                  'elevation':protocolObject.protocol_parameters['elevation'],
                                  'azimuth_boundaries':protocolObject.protocol_parameters['azimuth_boundaries'],
                                  'no_steps':protocolObject.protocol_parameters['no_steps'],
                                  'randomized_order':randomized_order,
                                  'x_steps':x_steps}

        return epoch_parameters, convenience_parameters
        
        
    def getParameterDefaults():
        protocol_parameters = {'square_width':5.0,
                       'color':0.0,
                       'elevation': 120.0,
                       'azimuth_boundaries': [50.0, 70.0],
                       'no_steps': 8}
        
        return protocol_parameters
    
    
    def getRunParameterDefaults():
        run_parameters = {'protocol_ID':'SequentialOrRandomMotion',
              'num_epochs':20,
              'pre_time':0.5,
              'stim_time':0.5,
              'tail_time':1.0,
              'idle_color':0.5}
        return run_parameters