import numpy as np
from flystim.trajectory import RectangleTrajectory

class MovingSquareMapping():
    def getEpochParameters(protocolObject):
        stimulus_ID = 'MovingPatch'
        az_loc = protocolObject.protocol_parameters['azimuth_locations']
        el_loc = protocolObject.protocol_parameters['elevation_locations']
        
        if type(az_loc) is not list:
            az_loc = [az_loc]
        if type(el_loc) is not list:
            el_loc = [el_loc]
        
        location_list = np.concatenate((az_loc, el_loc))
        movement_axis_list = np.concatenate((np.ones(len(az_loc)), 2*np.ones(len(el_loc))))
        
        current_search_axis_code, current_location = protocolObject.selectParametersFromLists((movement_axis_list, location_list),
                                                                                              all_combinations = False,
                                                                                              randomize_order = protocolObject.protocol_parameters['randomize_order'])
        
        if current_search_axis_code == 1:
            current_search_axis = 'azimuth'
        elif current_search_axis_code == 2:
            current_search_axis = 'elevation'

        #where does the square begin? Should be just off screen...
        startingAzimuth = 20.0; startingElevation = 40.0;
        speed = protocolObject.protocol_parameters['speed']
        stim_time = protocolObject.run_parameters['stim_time']
        
        if current_search_axis == 'elevation': #move along x (azimuth)
            startX = (0,startingAzimuth)
            endX = (stim_time,startingAzimuth + speed * stim_time)    
            startY = (0,current_location)
            endY = (stim_time,current_location)    
        elif current_search_axis == 'azimuth':  #move along y (elevation)
            startX = (0,current_location)
            endX = (stim_time,current_location)
            startY = (0,startingElevation)
            endY = (stim_time,startingElevation + speed * stim_time)   

        trajectory = RectangleTrajectory(x = [startX, endX],
                                             y = [startY, endY],
                                             angle=0,
                                             h = protocolObject.protocol_parameters['square_width'],
                                             w = protocolObject.protocol_parameters['square_width'],
                                             color = protocolObject.protocol_parameters['color']).to_dict()
        
        epoch_parameters = {'name':stimulus_ID,
                            'background':protocolObject.run_parameters['idle_color'],
                            'trajectory': trajectory}

        convenience_parameters = {'speed':speed,
                                  'current_search_axis':current_search_axis,
                                  'current_location':current_location,
                                  'randomize_order':protocolObject.protocol_parameters['randomize_order'],
                                  'square_width':protocolObject.protocol_parameters['square_width'],
                                  'color':protocolObject.protocol_parameters['color']}

        return epoch_parameters, convenience_parameters
        
        
    def getParameterDefaults():
        protocol_parameters = {'square_width':5.0,
                       'color':0.0,
                       'elevation_locations': [100.0, 105.0, 110.0, 115.0, 120.0, 125.0, 130.0, 135.0, 140.0], # 100...140
                       'azimuth_locations': [30.0, 35.0, 40.0, 45.0, 50.0, 55.0, 60.0, 65.0, 70.0, 75.0, 80.0], #30...80
                       'speed':60.0,
                       'randomize_order':True}
        
        return protocol_parameters
    
    
    def getRunParameterDefaults():
        run_parameters = {'protocol_ID':'MovingSquareMapping',
              'num_epochs':100,
              'pre_time':0.5,
              'stim_time':2.0,
              'tail_time':0.5,
              'idle_color':0.5}
        return run_parameters