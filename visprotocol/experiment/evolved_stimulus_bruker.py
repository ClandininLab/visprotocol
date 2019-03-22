#!/usr/bin/env python3

from time import sleep
import nidaqmx
from datetime import datetime
import flyrpc.multicall
import os

from stimvolver import stimulus_evolution
import visprotocol.client
import visprotocol.data
import visprotocol.protocol


def main():
    protocol = visprotocol.protocol.mht_protocol.BaseProtocol()

    protocol.run_parameters = {'protocol_ID':'evolved_grid_stimulus',
              'pre_time':0.25,
              'stim_time':1.0,
              'tail_time':0.25,
              'idle_color':0.5}
    
    protocol.epoch_parameters = {'name':'ArbitraryGrid',
                                 'encoding_scheme':'ternary_dense',
                                 'update_rate': 1,
                                 'stixel_size': 5,
                                 'num_theta': 12,
                                 'num_phi': 8,
                                 't_dim': 1,
                                 'background': 0.5,
                                 'center_theta': 120,
                                 'center_phi': 120}
    protocol.send_ttl = True
    series_number = 8
    
    #GA evolver parameters:
    num_generations = 5
    num_individuals = 10
    mutation_rate = 0.005
    num_persistent_parents = 10
    
    
    client = visprotocol.client.mht_client.Client()
    multicall = flyrpc.multicall.MyMultiCall(client.manager)
    

    data = visprotocol.data.mht_data.Data()
    data.experiment_file_name = 'test'
    data.initializeExperimentFile()

    stim_size = (protocol.epoch_parameters['num_phi'],
                 protocol.epoch_parameters['num_theta'],
                 protocol.epoch_parameters['t_dim'])
    
    evolver = stimulus_evolution.StimulusEvolver(stim_size = stim_size, 
                                                 pop_size = num_individuals, 
                                                 num_persistent_parents = num_persistent_parents,
                                                 mutation_rate = mutation_rate,
                                                 stimulus_type = protocol.epoch_parameters['encoding_scheme'], 
                                                 response_type = 'Bruker_bot')
    
    date_name = datetime.now().isoformat()[:-16].replace('-','')
    evolver.ResponseGenerator.data_directory = os.path.join('E:/Max/FlystimData', date_name)
    evolver.ResponseGenerator.series_name = 'TSeries-' + date_name + '-' + ('00' + str(series_number))[-3:]
    evolver.ResponseGenerator.pre_time = protocol.run_parameters['pre_time'] * 1e3 #sec -> msec
    
    client.manager.set_idle_background(protocol.run_parameters['idle_color'])

    for gen in range(num_generations):
        
        evolver.ResponseGenerator.cycle_number = gen+1
        if gen == 0:
            evolver.initializePopulation()
        print('----------GEN ' + str(gen) + '/' + str(num_generations) + '---------------')
        
        if protocol.send_ttl:
            # Send a TTL pulse through the NI-USB to trigger acquisition
            with nidaqmx.Task() as task:
                task.co_channels.add_co_pulse_chan_time("Dev5/ctr0",
                                                        low_time=0.002,
                                                        high_time=0.001)
                task.start()
                
        
        for ind in range(num_individuals):
            stimulus_code = evolver.current_generation[ind,:].flatten() / 2 + 0.5 #convert to intensity on [0,1] from contrast [-1,1]
            protocol.epoch_parameters['stimulus_code'] = stimulus_code.tolist()
            
            
            # # # # Load and start flystim stimulus # # # # #
            passedParameters = protocol.epoch_parameters.copy()
            multicall.load_stim(**passedParameters)
            
            sleep(protocol.run_parameters['pre_time'])
            #stim time
            multicall.start_stim()
            multicall.start_corner_square()
            multicall()
            sleep(protocol.run_parameters['stim_time'])
            
            #tail time
            multicall.stop_stim()
            multicall.black_corner_square()
            multicall()
            sleep(protocol.run_parameters['tail_time'])     

        #collect responses from this generation
        
        #evolve next generation of stimuli
        evolver.evolve(1)

    evolver.plotResults()

if __name__ == '__main__':
    main()
    
    
    