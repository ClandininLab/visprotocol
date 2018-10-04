import numpy as np

class CheckerboardWhiteNoise():
    def getEpochParameters(protocolObject):
        stimulus_ID  = 'RandomGrid'
        
        start_seed = int(np.random.choice(range(int(1e6))))

        epoch_parameters = {'name':stimulus_ID,
                            'theta_period':protocolObject.protocol_parameters['checker_width'],
                            'phi_period':protocolObject.protocol_parameters['checker_width'],
                            'rand_min':protocolObject.protocol_parameters['rand_min'],
                            'rand_max':protocolObject.protocol_parameters['rand_max'],
                            'start_seed':start_seed,
                            'update_rate':protocolObject.protocol_parameters['update_rate'],
                            'distribution_type':protocolObject.protocol_parameters['distribution_type']}
        convenience_parameters = {}
        
        return epoch_parameters, convenience_parameters
        
        
    def getParameterDefaults():
        protocol_parameters = {'checker_width':5.0,
                       'update_rate':0.5,
                       'rand_min': 0.0,
                       'rand_max':1.0,
                       'distribution_type':'binary'}
        
        return protocol_parameters