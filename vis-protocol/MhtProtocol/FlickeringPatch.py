import numpy as np
from flystim.trajectory import RectangleTrajectory

class FlickeringPatch():
    def getEpochParameters(protocolObject):
        stimulus_ID = 'MovingPatch'
        stim_time = protocolObject.run_parameters['stim_time']
        
        current_temporal_frequency = protocolObject.selectParametersFromLists(protocolObject.protocol_parameters['temporal_frequency'],
                                                                randomize_order = protocolObject.protocol_parameters['randomize_order'])

        trajectory_sample_rate = 100 # Hz
        nPoints = trajectory_sample_rate * stim_time
        time_points = np.linspace(0, stim_time, nPoints)
        color_values = np.sin(time_points * 2 * np.pi * current_temporal_frequency)
        color_trajectory = list(zip(time_points,color_values))

        trajectory = RectangleTrajectory(x = protocolObject.protocol_parameters['center'][0],
                                              y = protocolObject.protocol_parameters['center'][1],
                                              angle = 0,
                                              h = protocolObject.protocol_parameters['height'],
                                              w = protocolObject.protocol_parameters['width'],
                                              color = color_trajectory).to_dict()   

        epoch_parameters = {'name':stimulus_ID,
                            'background':protocolObject.run_parameters['idle_color'],
                            'trajectory':trajectory}
        convenience_parameters = {'current_temporal_frequency':current_temporal_frequency,
                                  'center':protocolObject.protocol_parameters['center'],
                                  'width':protocolObject.protocol_parameters['width'],
                                  'height':protocolObject.protocol_parameters['height']}

        return epoch_parameters, convenience_parameters
        
        
    def getParameterDefaults():
        protocol_parameters = {'height':5.0,
                       'width':5.0,
                       'center': [55.0, 120.0],
                       'temporal_frequency': [1.0, 2.0, 4.0, 8.0, 16.0, 32.0],
                       'randomize_order':True}
        
        return protocol_parameters
