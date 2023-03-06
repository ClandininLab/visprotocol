import os
import glob
import  importlib.resources
import yaml

import visprotocol


# def getLabPackagePath():
#     # lab_package_path = importlib.resources.read_text(visprotocol, 'lab_package_path.txt')
#     # lab_package_path = files(visprotocol).joinpath('lab_package_path.txt').open('r').read()
#     return lab_package_path


# def getAvailableUserNames():
#     lab_package_path = getLabPackagePath()
    
#     user_config_files = [os.path.split(f)[1] for f in glob.glob(os.path.join(lab_package_path, 'config', '*.yaml'))]
#     user_names = [f.split('_config')[0] for f in user_config_files]
#     return user_names

def getConfigDirectory():
    # cfg_dir_path = importlib.resources.read_text(visprotocol, 'path_to_config_dir.txt')
    cfg_dir_path = importlib.resources.files(visprotocol).joinpath('path_to_config_dir.txt').open('r').read()

    # TODO handle no .txt file found
    return cfg_dir_path

def getAvailableConfigFiles():
    cfg_names = [os.path.split(f)[1] for f in glob.glob(os.path.join(getConfigDirectory(), '*.yaml'))]
    return cfg_names

def getConfigurationFile(cfg_name):
     with open(os.path.join(getConfigDirectory(), cfg_name), 'r') as ymlfile:
        cfg = yaml.safe_load(ymlfile)
     return cfg

def getAvailableRigConfigs(cfg):
    return list(cfg.get('rig_config').keys())

def getParameterPresetDirectory(cfg):
    presets_dir = cfg.get('parameter_presets_dir', None)
    if presets_dir is not None:
        return os.path.join(getConfigDirectory(), presets_dir)
    else:
        raise Exception('You must define a parameter preset directory in your config file')

def getScreenCenter(cfg):
    if 'current_rig_name' in cfg:
        screen_center = cfg.get('rig_config').get(cfg.get('current_rig_name')).get('screen_center', [0, 0])
    else:
        print('No rig selected, using default screen center')
        screen_center = [0, 0]
    
    return screen_center
    
def getServerOptions(cfg):
    if 'current_rig_name' in cfg:
        server_options = cfg.get('rig_config').get(cfg.get('current_rig_name')).get('server_options', {'host': '0.0.0.0', 'port': 60629, 'use_server': False})
    else:
        print('No rig selected, using default server settings')
        server_options = {'host': '0.0.0.0',
                          'port': 60629,
                          'use_server': False}
    return server_options

def getDataDirectory(cfg):
    if 'current_rig_name' in cfg:
        data_directory = cfg.get('rig_config').get(cfg.get('current_rig_name')).get('data_directory', os.getcwd())
    else:
        print('No rig selected, using default data directory')
        data_directory = os.getcwd()
    return data_directory

# def getRigConfiguration(user_name, rig_name):
#     user_config = getUserConfiguration(user_name)

#     return user_config.get('rig_config').get(rig_name)


def getFullPathsToModules(cfg):
    lab_package_path = getLabPackagePath()
    full_module_paths = {'protocol_module_path': os.path.join(lab_package_path, cfg['protocol_module_path']),
                         'data_module_path': os.path.join(lab_package_path, cfg['data_module_path']),
                         'client_module_path': os.path.join(lab_package_path, cfg['client_module_path']),

                         'protocol_module_name': getModuleNameFromPath(cfg['protocol_module_path']),
                         'data_module_name': getModuleNameFromPath(cfg['data_module_path']),
                         'client_module_name': getModuleNameFromPath(cfg['client_module_path'])
                        }

    return full_module_paths


def getDevices(cfg):
    configured_devices = {}
    for dev in cfg['rig_config'].get(cfg['rig_name']).get('devices'):
        configured_devices[dev] = cfg['rig_config'].get(cfg['rig_name']).get('devices')[dev]
    return configured_devices

def getModuleNameFromPath(path):
    return os.path.split(path)[-1].split('.')[0]