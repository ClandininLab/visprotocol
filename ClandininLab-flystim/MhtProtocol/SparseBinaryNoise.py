import numpy as np
from flystim.trajectory import Trajectory

class SparseBinaryNoise():
    def getEpochParameters(protocolObject):
        stimulus_ID = 'MovingPatch'

        stim_time = protocolObject.run_parameters['stim_time'] #sec
        flash_duration = protocolObject.protocol_parameters['flash_duration'] #sec
        
        time_steps = np.arange(0,stim_time,flash_duration)
        no_steps = len(time_steps)
        x_steps = np.random.choice(protocolObject.protocol_parameters['azimuth_locations'], size = no_steps, replace=True)
        y_steps = np.random.choice(protocolObject.protocol_parameters['elevation_locations'], size = no_steps, replace=True)
        color_steps = np.random.choice((0.0,1.0), size = no_steps, replace = True)
        
        # time-modulated trajectories
        x = Trajectory(list(zip(time_steps,x_steps)), kind = 'previous') #note interp kind is previous
        y = Trajectory(list(zip(time_steps,y_steps)), kind = 'previous')
        color = Trajectory(list(zip(time_steps,color_steps)), kind = 'previous')
        
        
        # constant trajectories:
        w = Trajectory(protocolObject.protocol_parameters['square_width'])
        h = Trajectory(protocolObject.protocol_parameters['square_width'])
        angle = Trajectory(0)
        trajectory = {'x': x.to_dict(), 'y': y.to_dict(), 'w': w.to_dict(), 'h': h.to_dict(),
            'angle': angle.to_dict(), 'color': color.to_dict()}

        epoch_parameters = {'name':stimulus_ID,
                            'background':protocolObject.run_parameters['idle_color'],
                            'trajectory':trajectory}
        convenience_parameters = {'square_width':protocolObject.protocol_parameters['square_width'],
                                  'angle':0,
                                  'elevation_locations':protocolObject.protocol_parameters['elevation_locations'],
                                  'azimuth_locations':protocolObject.protocol_parameters['azimuth_locations'],
                                  'flash_duration':protocolObject.protocol_parameters['flash_duration'],
                                  'x_steps':x_steps,
                                  'y_steps':y_steps,
                                  'time_steps':time_steps,
                                  'color_steps':color_steps}

        return epoch_parameters, convenience_parameters
        
        
    def getParameterDefaults():
        protocol_parameters = {'square_width':5.0,
                       'elevation_locations': [100.0, 105.0, 110.0, 115.0, 120.0, 125.0, 130.0, 135.0, 140.0], # 100...140
                       'azimuth_locations': [30.0, 35.0, 40.0, 45.0, 50.0, 55.0, 60.0, 65.0, 70.0, 75.0, 80.0], #30...80
                       'flash_duration':0.25}
        
        return protocol_parameters
    
    
    def getRunParameterDefaults():
        run_parameters = {'protocol_ID':'SparseBinaryNoise',
              'num_epochs':5,
              'pre_time':5.0,
              'stim_time':60.0,
              'tail_time':5.0,
              'idle_color':0.5}
        return run_parameters