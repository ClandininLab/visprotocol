import numpy as np

class CheckerboardWhiteNoise():
    def getEpochParameters(protocolObject):
        """
        getEpochParameters(protocolObject) 
            Generates the parameters that need to be sent to flystim to produce a stimulus. This function is essentially a
            mapping between protocol_parameters (and other data about the current epoch) and epoch_parameters for flystim
        
            input: 
                -protocolObject is an object of a protocol class (e.g. ExampleProtocol), which is a child
                of the parent class ClandininLabProtocol. Anything you want to pass to getEpochParameters should be
                accessible from your protocol object
            returns:
                -epoch_parameters: parameters passed directly to flystim to generate the stimulus
                -convenience_parameters: arbitrary dictionary of parameters you want to save out with the metadata,
                                    These are not used to generate the stimuli
        """
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
        """
        getParameterDefaults() 
            returns:
                -protocol_parameters: default parameters used to populate the GUI.
                                Protocol parameters are user-defined and do not need to 
        """
        
        protocol_parameters = {'checker_width':5.0,
                       'update_rate':60.0,
                       'rand_min': 0.0,
                       'rand_max':1.0,
                       'distribution_type':'binary'}
        
        return protocol_parameters