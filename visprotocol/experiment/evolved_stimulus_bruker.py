#!/usr/bin/env python3

from flystim.stim_server import launch_stim_server
from flystim.screen import Screen

from time import sleep
import numpy as np

from stimvolver import stimulus_evolution

def main():
    pre_time = 0.05
    stim_time = 1.0
    tail_time = 0.05
    
    encoding_scheme = 'ternary_dense'
    update_rate = 1
    stixel_size = 5
    num_theta = 12
    num_phi = 8
    t_dim = 1
    background = 0.5
    center_theta = 90
    center_phi = 90
    
    num_generations = 50
    num_individuals = 40
    mutation_rate = 0.005
    num_persistent_parents = 10

    
    evolver = stimulus_evolution.StimulusEvolver(stim_size = (num_phi,num_theta,t_dim), 
                                                 pop_size = num_individuals, 
                                                 num_persistent_parents = num_persistent_parents,
                                                 mutation_rate = mutation_rate,
                                                 stimulus_type = encoding_scheme, 
                                                 response_type = 'model_RGC')

    manager = launch_stim_server(Screen(fullscreen=False))

    for gen in range(num_generations):
        if gen == 0:
            evolver.initializePopulation()

        print('----------GEN ' + str(gen) + '/' + str(num_generations) + '---------------')
        
        for ind in range(num_individuals):
            if ind == 0:
                stimulus_code = evolver.current_generation[ind,:].flatten() / 2 + 0.5
                
                manager.load_stim('ArbitraryGrid', stixel_size = stixel_size, 
                      num_theta = num_theta, num_phi = num_phi, t_dim = t_dim, update_rate = update_rate, 
                      center_theta = center_theta, center_phi = center_phi, background = background, 
                      stimulus_code = stimulus_code.tolist(), encoding_scheme = encoding_scheme, hold = True)
                
                
                sleep(pre_time)
            
                manager.start_stim()
                sleep(stim_time)
            
                manager.stop_stim(print_profile = False)
                sleep(tail_time)
            
        #collect responses from this generation
        
        #evolve next generation of stimuli
        evolver.evolve(1)

    evolver.plotResults()

if __name__ == '__main__':
    main()
    
    
    
