import numpy as np
from flystim.trajectory import Trajectory

class LoomingPatch():
    def getEpochParameters(protocolObject):
        stimulus_ID = 'MovingPatch'
        
#        current_rv_ratio = protocolObject.selectCurrentParameterFromList('rv_ratio') / 1e3 #msec -> sec

        stim_time = protocolObject.run_parameters['stim_time']
        start_size = protocolObject.protocol_parameters['start_size']
        end_size = protocolObject.protocol_parameters['end_size']
        
        rv_ratio = protocolObject.protocol_parameters['rv_ratio'] #msec
        trajectory_code = [0, 1, 2] #0 = expanding, 1 = reversed (shrinking), 2 = randomized


        current_rv_ratio, current_trajectory_code = protocolObject.selectParameterPairFromLists(rv_ratio, trajectory_code)
        current_rv_ratio = current_rv_ratio / 1e3 #msec -> sec
    
        time_steps = np.linspace(0,stim_time,100) #time steps of trajectory
        # calculate angular size at each time step for this rv ratio
        angular_size = 2 * np.rad2deg(np.arctan(current_rv_ratio * (1 /(stim_time - time_steps))))
        
        # shift curve vertically so it starts at start_size
        min_size = angular_size[0]
        size_adjust = min_size - start_size
        angular_size = angular_size - size_adjust
        # Cap the curve at end_size and have it just hang there
        max_size_ind = np.where(angular_size > end_size)[0][0]
        angular_size[max_size_ind:] = end_size

        # Get the correct trajectory type
        if current_trajectory_code == 0:
            current_trajectory_type = 'expanding'
            angular_size = angular_size # initial trajectory
            
        elif current_trajectory_code == 1:
            current_trajectory_type = 'contracting'
            angular_size = np.flip(angular_size) # reverse in time
            
        elif current_trajectory_code == 2:
            current_trajectory_type = 'randomized'
            angular_size = np.random.permutation(angular_size) #randomize in time

        # time-modulated trajectories
        h = Trajectory(list(zip(time_steps,angular_size)), kind = 'previous')
        w = Trajectory(list(zip(time_steps,angular_size)), kind = 'previous')

        # constant trajectories:
        centerX = Trajectory(protocolObject.protocol_parameters['center'][0])
        centerY = Trajectory(protocolObject.protocol_parameters['center'][1])
        color = Trajectory(protocolObject.protocol_parameters['color'])
        angle = Trajectory(0)
        trajectory = {'x': centerX.to_dict(), 'y': centerY.to_dict(), 'w': w.to_dict(), 'h': h.to_dict(),
            'angle': angle.to_dict(), 'color': color.to_dict()}
        

        epoch_parameters = {'name':stimulus_ID,
                            'background':protocolObject.run_parameters['idle_color'],
                            'trajectory':trajectory}

        convenience_parameters = {'center':protocolObject.protocol_parameters['center'],
                                  'current_rv_ratio':current_rv_ratio,
                                  'color':protocolObject.protocol_parameters['color'],
                                  'time_steps':time_steps,
                                  'angular_size':angular_size,
                                  'start_size':start_size,
                                  'end_size':end_size,
                                  'randomize_order':protocolObject.protocol_parameters['randomize_order'],
                                  'current_trajectory_type':current_trajectory_type}

        return epoch_parameters, convenience_parameters

    def getParameterDefaults():
        protocol_parameters = {'color':0.0,
                       'center': [55.0, 120],
                       'start_size': 2.5,
                       'end_size': 80.0,
                       'rv_ratio':[5.0, 10.0, 20.0, 40.0, 80.0],
                       'randomize_order': True}
        
        return protocol_parameters
    
    def getRunParameterDefaults():
        run_parameters = {'protocol_ID':'LoomingPatch',
              'num_epochs':75,
              'pre_time':0.5,
              'stim_time':1.0,
              'tail_time':0.5,
              'idle_color':0.5}
        return run_parameters