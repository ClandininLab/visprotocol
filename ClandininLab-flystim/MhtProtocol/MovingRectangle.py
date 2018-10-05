import numpy as np
from flystim.trajectory import RectangleTrajectory

class MovingRectangle():
    def getEpochParameters(protocolObject):
        stimulus_ID = 'MovingPatch'
            
        currentAngle = protocolObject.selectCurrentParameterFromList('angle')
        
        centerX = protocolObject.protocol_parameters['center'][0]
        centerY = protocolObject.protocol_parameters['center'][1]
        speed = protocolObject.protocol_parameters['speed']
        stim_time = protocolObject.run_parameters['stim_time']
        distance_to_travel = speed * stim_time
        
        startX = (0,centerX - np.cos(np.radians(currentAngle)) * distance_to_travel/2)
        endX = (stim_time, centerX + np.cos(np.radians(currentAngle)) * distance_to_travel/2)
        startY = (0,centerY - np.sin(np.radians(currentAngle)) * distance_to_travel/2)
        endY = (stim_time, centerY + np.sin(np.radians(currentAngle)) * distance_to_travel/2)

        trajectory = RectangleTrajectory(x=[startX, endX],
                                              y=[startY, endY],
                                              angle=currentAngle,
                                              h = protocolObject.protocol_parameters['height'],
                                              w = protocolObject.protocol_parameters['width'],
                                              color = protocolObject.protocol_parameters['color']).to_dict()   

        epoch_parameters = {'name':stimulus_ID,
                            'background':protocolObject.run_parameters['idle_color'],
                            'trajectory':trajectory}
        convenience_parameters = {'currentAngle': currentAngle,
                                  'center':protocolObject.protocol_parameters['center'],
                                  'speed':protocolObject.protocol_parameters['speed'],
                                  'color':protocolObject.protocol_parameters['color'],
                                  'height':protocolObject.protocol_parameters['height'],
                                  'width':protocolObject.protocol_parameters['width']}

        return epoch_parameters, convenience_parameters
        
        
    def getParameterDefaults():
        protocol_parameters = {'width':5.0,
                       'height':5.0,
                       'color':0.0,
                       'center': [55.0, 120],
                       'speed':60.0,
                       'angle': [0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0],
                       'randomize_order':True}
        
        return protocol_parameters
    
    def getRunParameterDefaults():
        run_parameters = {'protocol_ID':'MovingRectangle',
              'num_epochs':40,
              'pre_time':0.5,
              'stim_time':2.0,
              'tail_time':0.5,
              'idle_color':0.5}
        return run_parameters