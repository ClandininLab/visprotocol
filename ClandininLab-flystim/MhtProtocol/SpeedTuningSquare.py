import numpy as np
from flystim.trajectory import RectangleTrajectory

class SpeedTuningSquare():
    def getEpochParameters(protocolObject):
        stimulus_ID = 'MovingPatch'
            
        currentSpeed = protocolObject.selectCurrentParameterFromList('speed')
        
        centerX = protocolObject.protocol_parameters['center'][0]
        centerY = protocolObject.protocol_parameters['center'][1]
        angle = protocolObject.protocol_parameters['angle']
        width = protocolObject.protocol_parameters['width']
        stim_time = protocolObject.run_parameters['stim_time']
        
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
                                         color = protocolObject.protocol_parameters['color']).to_dict()   

        epoch_parameters = {'name':stimulus_ID,
                            'background':protocolObject.run_parameters['idle_color'],
                            'trajectory':trajectory}
        convenience_parameters = {'width': width,
                                  'center':protocolObject.protocol_parameters['center'],
                                  'angle':angle,
                                  'currentSpeed':currentSpeed,
                                  'color':protocolObject.protocol_parameters['color']}

        return epoch_parameters, convenience_parameters
        
        
    def getParameterDefaults():
        protocol_parameters = {'width': 5.0,
                       'color':0.0,
                       'center': [55.0, 120.0],
                       'speed':[20.0, 40.0, 60.0, 80.0, 100.0, 120.0, 140.0, 160.0, 180.0, 200.0],
                       'angle': 0.0,
                       'randomize_order':True}
        
        return protocol_parameters