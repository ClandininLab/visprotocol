import numpy as np
from flystim.trajectory import RectangleTrajectory

class ExpandingMovingSquare():
    def getEpochParameters(protocolObject):
        stimulus_ID = 'MovingPatch'
        
        currentWidth = protocolObject.selectCurrentParameterFromList('width')
        
        centerX = protocolObject.protocol_parameters['center'][0]
        centerY = protocolObject.protocol_parameters['center'][1]
        angle = protocolObject.protocol_parameters['angle']
        speed = protocolObject.protocol_parameters['speed']
        stim_time = protocolObject.run_parameters['stim_time']
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
                                              color = protocolObject.protocol_parameters['color']).to_dict()   

        epoch_parameters = {'name':stimulus_ID,
                            'background':protocolObject.run_parameters['idle_color'],
                            'trajectory':trajectory}
        convenience_parameters = {'currentWidth': currentWidth,
                                  'center':protocolObject.protocol_parameters['center'],
                                  'angle':protocolObject.protocol_parameters['angle'],
                                  'speed':protocolObject.protocol_parameters['speed'],
                                  'color':protocolObject.protocol_parameters['color']}

        return epoch_parameters, convenience_parameters
        
        
    def getParameterDefaults():
        protocol_parameters = {'width':[2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0],
                       'color':0.0,
                       'center': [55.0, 120.0],
                       'speed':60.0,
                       'angle': 0.0,
                       'randomize_order':True}
        
        return protocol_parameters
    
    def getRunParameterDefaults():
        run_parameters = {'protocol_ID':'ExpandingMovingSquare',
              'num_epochs':70,
              'pre_time':0.5,
              'stim_time':2.0,
              'tail_time':0.5,
              'idle_color':0.5}
        return run_parameters