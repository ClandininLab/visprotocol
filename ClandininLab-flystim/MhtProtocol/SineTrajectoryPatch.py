import numpy as np
from flystim.trajectory import Trajectory

class SineTrajectoryPatch():
    def getEpochParameters(protocolObject):
        stimulus_ID = 'MovingPatch'
        
        current_temporal_frequency = protocolObject.selectCurrentParameterFromList('temporal_frequency')

        centerX = protocolObject.protocol_parameters['center'][0]
        centerY = protocolObject.protocol_parameters['center'][1]
        amplitude = protocolObject.protocol_parameters['amplitude']
        movement_axis = protocolObject.protocol_parameters['movement_axis']
        
        stim_time = protocolObject.run_parameters['stim_time']
        
        time_steps = np.linspace(0,stim_time,500) #time steps of trajectory
        distance_along_movement_axis = amplitude * np.sin(time_steps * 2 * np.pi * current_temporal_frequency)

        x_steps = centerX + np.cos(np.radians(movement_axis)) * distance_along_movement_axis
        y_steps = centerY + np.sin(np.radians(movement_axis)) * distance_along_movement_axis

        # time-modulated trajectories
        x = Trajectory(list(zip(time_steps,x_steps)), kind = 'previous')
        y = Trajectory(list(zip(time_steps,y_steps)), kind = 'previous')
        
        # constant trajectories:
        color = Trajectory(protocolObject.protocol_parameters['color'])
        w = Trajectory(protocolObject.protocol_parameters['width']) 
        h = Trajectory(protocolObject.protocol_parameters['height']) 
        angle = Trajectory(movement_axis)
        
        trajectory = {'x': x.to_dict(), 'y': y.to_dict(), 'w': w.to_dict(), 'h': h.to_dict(),
            'angle': angle.to_dict(), 'color': color.to_dict()}
        

        epoch_parameters = {'name':stimulus_ID,
                            'background':protocolObject.run_parameters['idle_color'],
                            'trajectory':trajectory}
        
        convenience_parameters = {'width': protocolObject.protocol_parameters['width'],
                                  'height':protocolObject.protocol_parameters['height'],
                                  'color':protocolObject.protocol_parameters['color'],
                                  'center':protocolObject.protocol_parameters['center'],
                                  'amplitude':protocolObject.protocol_parameters['amplitude'],
                                  'temporal_frequency':protocolObject.protocol_parameters['temporal_frequency'],
                                  'current_temporal_frequency':current_temporal_frequency,
                                  'movement_axis':protocolObject.protocol_parameters['movement_axis'],
                                  'randomize_order':protocolObject.protocol_parameters['randomize_order'],
                                  'time_steps':time_steps,
                                  'x_steps':x_steps,
                                  'y_steps':y_steps
                                  }

        return epoch_parameters, convenience_parameters
        
        
    def getParameterDefaults():
        protocol_parameters = {'width':5.0,
                       'height':5.0,
                       'color':0.0,
                       'center': [55.0, 120],
                       'amplitude': 20, #deg, half of total travel distance
                       'temporal_frequency': [1, 2, 4, 6, 8], #Hz
                       'movement_axis': 0,
                       'randomize_order':True}
        
        return protocol_parameters
    
    def getRunParameterDefaults():
        run_parameters = {'protocol_ID':'SineTrajectoryPatch',
              'num_epochs':40,
              'pre_time':0.5,
              'stim_time':2.0,
              'tail_time':0.5,
              'idle_color':0.5}
        return run_parameters
