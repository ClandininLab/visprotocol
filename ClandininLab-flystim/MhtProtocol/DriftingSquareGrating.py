class DriftingSquareGrating():
    def getEpochParameters(protocolObject):
        stimulus_ID  = 'RotatingBars'
        
        currentAngle = protocolObject.selectParametersFromLists(protocolObject.protocol_parameters['angle'],
                                                                randomize_order = protocolObject.protocol_parameters['randomize_order'])
        
        epoch_parameters = {'name':stimulus_ID,
                            'period':protocolObject.protocol_parameters['period'],
                            'duty_cycle':0.5,
                            'rate':protocolObject.protocol_parameters['rate'],
                            'color':protocolObject.protocol_parameters['color'],
                            'background':protocolObject.protocol_parameters['background'],
                            'angle':currentAngle}
        
        convenience_parameters = {}

        return epoch_parameters, convenience_parameters
        
        
    def getParameterDefaults():
        protocol_parameters = {'period':20.0,
                       'rate':20.0,
                       'color':1.0,
                       'background':0,
                       'angle':[0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0],
                       'randomize_order':True}
        
        return protocol_parameters
    
    def getRunParameterDefaults():
        run_parameters = {'protocol_ID':'DriftingSquareGrating',
              'num_epochs':40,
              'pre_time':0.5,
              'stim_time':4.0,
              'tail_time':0.5,
              'idle_color':0.5}
        return run_parameters