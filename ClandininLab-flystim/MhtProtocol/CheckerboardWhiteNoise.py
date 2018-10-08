import numpy as np

class CheckerboardWhiteNoise():
    def getEpochParameters(protocolObject):
        stimulus_ID  = 'RandomGrid'
        
        start_seed = int(np.random.choice(range(int(1e6))))
        
        
        distribution_data = {'name':'Gaussian',
                                 'args':[],
                                 'kwargs':{'rand_mean':protocolObject.protocol_parameters['rand_mean'],
                                           'rand_stdev':protocolObject.protocol_parameters['rand_stdev']}}

        epoch_parameters = {'name':stimulus_ID,
                            'theta_period':protocolObject.protocol_parameters['checker_width'],
                            'phi_period':protocolObject.protocol_parameters['checker_width'],
                            'start_seed':start_seed,
                            'update_rate':protocolObject.protocol_parameters['update_rate'],
                            'distribution_data':distribution_data}
        convenience_parameters = {}
        
        return epoch_parameters, convenience_parameters
        
        
    def getParameterDefaults():
        protocol_parameters = {'checker_width':5.0,
                       'update_rate':0.5,
                       'rand_mean': 0.5,
                       'rand_stdev':0.15}
        
        return protocol_parameters
    
    def getRunParameterDefaults():
        run_parameters = {'protocol_ID':'CheckerboardWhiteNoise',
              'num_epochs':10,
              'pre_time':1.0,
              'stim_time':30.0,
              'tail_time':1.0,
              'idle_color':0.5}
        return run_parameters