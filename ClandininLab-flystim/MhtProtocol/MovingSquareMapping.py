import numpy as np
from flystim.trajectory import RectangleTrajectory

class MovingSquareMapping():
    def getEpochParameters(protocolObject):
        stimulus_ID = 'MovingPatch'
        location_list = np.concatenate((protocolObject.protocol_parameters['azimuth_locations'] ,
                                        protocolObject.protocol_parameters['elevation_locations']))
        movement_axis_list = np.concatenate((np.ones(len(protocolObject.protocol_parameters['azimuth_locations'])) ,
                                               2*np.ones(len(protocolObject.protocol_parameters['elevation_locations']))))
        
        
        current_search_axis_code, current_location = protocolObject.selectParametersFromLists((movement_axis_list, location_list),
                                                                                              all_combinations = False,
                                                                                              randomize_order = protocolObject.protocol_parameters['randomize_order'])
        
        if current_search_axis_code == 1:
            current_search_axis = 'azimuth'
        elif current_search_axis_code == 2:
            current_search_axis = 'elevation'
#        
#        if protocolObject.num_epochs_completed == 0: #new run: initialize location sequences
#            location_sequence = np.concatenate((protocolObject.protocol_parameters['azimuth_locations'] ,
#                                               protocolObject.protocol_parameters['elevation_locations']))
#            movement_axis_sequence = np.concatenate((np.ones(len(protocolObject.protocol_parameters['azimuth_locations'])) ,
#                                               2*np.ones(len(protocolObject.protocol_parameters['elevation_locations']))))
#            protocolObject.persistent_parameters = {'movement_axis_sequence':movement_axis_sequence,
#                          'location_sequence':location_sequence}
#                
#        draw_ind = np.mod(protocolObject.num_epochs_completed,len(protocolObject.persistent_parameters['location_sequence']))
#        if draw_ind == 0 and protocolObject.protocol_parameters['randomize_order']:
#            rand_inds = np.random.permutation(len(protocolObject.persistent_parameters['location_sequence']))
#            protocolObject.persistent_parameters['movement_axis_sequence'] = list(np.array(protocolObject.persistent_parameters['movement_axis_sequence'])[rand_inds])
#            protocolObject.persistent_parameters['location_sequence'] = list(np.array(protocolObject.persistent_parameters['location_sequence'])[rand_inds])
#            
#        # select current locations from sequence
#        if protocolObject.persistent_parameters['movement_axis_sequence'][draw_ind] == 1:
#            current_search_axis = 'azimuth' #current location is an azimuth, movement along elevation
#        elif protocolObject.persistent_parameters['movement_axis_sequence'][draw_ind] == 2:
#            current_search_axis = 'elevation' #current location is an elevation, movement along azimuth
#        current_location = protocolObject.persistent_parameters['location_sequence'][draw_ind]

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