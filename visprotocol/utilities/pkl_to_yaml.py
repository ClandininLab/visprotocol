# -*- coding: utf-8 -*-
"""
Created on Tue May 28 13:49:51 2019

@author: mhturner
"""
from visprotocol.utilities import squirrel
import yaml
import glob
import os

parameter_preset_directory = 'C:/Users/mhturner/Documents/GitHub/visprotocol/resources/mht/parameter_presets'

preset_files = [os.path.split(f)[1] for f in glob.glob(os.path.join(parameter_preset_directory,'*.pkl'))]

for f in preset_files:
    parameter_presets = squirrel.get(f.split('.')[0], data_directory = parameter_preset_directory)
    for k in parameter_presets.keys():
        with open(os.path.join(parameter_preset_directory, f.split('.')[0] + '.yaml'), 'w') as outfile:
            yaml.dump(parameter_presets, outfile, default_flow_style=False, sort_keys=False)
        
