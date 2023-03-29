import os
import glob
import importlib.resources
import yaml
import sys

import visprotocol

def get_lab_package_directory():
    with open(importlib.resources.files(visprotocol).joinpath('path_to_lab_package.txt')) as path_file:
        cfg_dir_path = path_file.read()


    # cfg_dir_path = importlib.resources.files(visprotocol).joinpath('path_to_lab_package.txt').open('r').read()

    # TODO handle no .txt file found
    return cfg_dir_path

def get_available_config_files():
    cfg_names = [os.path.split(f)[1] for f in glob.glob(os.path.join(get_lab_package_directory(), 'configs', '*.yaml'))]
    return cfg_names

def get_configuration_file(cfg_name):
     with open(os.path.join(get_lab_package_directory(), 'configs', cfg_name), 'r') as ymlfile:
        cfg = yaml.safe_load(ymlfile)
     return cfg

def get_available_rig_configs(cfg):
    return list(cfg.get('rig_config').keys())

def get_parameter_preset_directory(cfg):
    presets_dir = cfg.get('parameter_presets_dir', None)
    if presets_dir is not None:
        return os.path.join(get_lab_package_directory(), presets_dir)
    else:
        raise Exception('You must define a parameter preset directory in your config file')

def get_path_to_module(cfg, module_name):
    module_path = cfg.get('module_paths', None).get(module_name, None)
    if module_path is not None:
        out_path = os.path.join(get_lab_package_directory(), module_path)
        if os.path.exists(out_path):
            return out_path
        else:
            raise Exception('User defined protocols module not found at {}, check your config file'.format(out_path))
    else:
        return None

def load_user_module(cfg, module_name):

    path_to_module = get_path_to_module(cfg, module_name)
    if path_to_module is None:
        print('!!! Using builtin {} module. To use user defined module, you must point to that module in your config file !!!'.format(module_name))
        return None
    else:
        spec = importlib.util.spec_from_file_location(module_name, path_to_module)
        loaded_mod = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = loaded_mod
        spec.loader.exec_module(loaded_mod)

        print('Loaded {} module from {}'.format(module_name, path_to_module))
        return loaded_mod

def load_trigger_device(cfg):
    # load device modules
    daq = load_user_module(cfg, 'daq')

    # fetch the trigger device definition from the config
    trigger_device_definition = cfg['rig_config'][cfg.get('current_rig_name')]['devices'].get('trigger', None)

    if trigger_device_definition is None:
        trigger_device = None
    else:
        # eval the trigger device definition to make it
        trigger_device = eval('daq.{}'.format(trigger_device_definition))

    return trigger_device

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