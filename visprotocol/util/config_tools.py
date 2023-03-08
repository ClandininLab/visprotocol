import os
import glob
import  importlib.resources
import yaml

import visprotocol

def get_config_directory():
    cfg_dir_path = importlib.resources.files(visprotocol).joinpath('path_to_config_dir.txt').open('r').read()

    # TODO handle no .txt file found
    return cfg_dir_path

def get_available_config_files():
    cfg_names = [os.path.split(f)[1] for f in glob.glob(os.path.join(get_config_directory(), '*.yaml'))]
    return cfg_names

def get_configuration_file(cfg_name):
     with open(os.path.join(get_config_directory(), cfg_name), 'r') as ymlfile:
        cfg = yaml.safe_load(ymlfile)
     return cfg

def get_available_rig_configs(cfg):
    return list(cfg.get('rig_config').keys())

def get_parameter_preset_directory(cfg):
    presets_dir = cfg.get('parameter_presets_dir', None)
    if presets_dir is not None:
        return os.path.join(get_config_directory(), presets_dir)
    else:
        raise Exception('You must define a parameter preset directory in your config file')

def get_screen_center(cfg):
    if 'current_rig_name' in cfg:
        screen_center = cfg.get('rig_config').get(cfg.get('current_rig_name')).get('screen_center', [0, 0])
    else:
        print('No rig selected, using default screen center')
        screen_center = [0, 0]
    
    return screen_center
    
def get_server_options(cfg):
    if 'current_rig_name' in cfg:
        server_options = cfg.get('rig_config').get(cfg.get('current_rig_name')).get('server_options', {'host': '0.0.0.0', 'port': 60629, 'use_server': False})
    else:
        print('No rig selected, using default server settings')
        server_options = {'host': '0.0.0.0',
                          'port': 60629,
                          'use_server': False}
    return server_options

def get_data_directory(cfg):
    if 'current_rig_name' in cfg:
        data_directory = cfg.get('rig_config').get(cfg.get('current_rig_name')).get('data_directory', os.getcwd())
    else:
        print('No rig selected, using default data directory')
        data_directory = os.getcwd()
    return data_directory

def get_experimenter(cfg):
    return cfg.get('experimenter', '')