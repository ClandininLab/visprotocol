import os
import glob
import  importlib.resources
import yaml

import visprotocol


def getLabPackagePath():
    lab_package_path = importlib.resources.read_text(visprotocol, 'lab_package_path.txt')
    # lab_package_path = files(visprotocol).joinpath('lab_package_path.txt').open('r').read()
    return lab_package_path


def getAvailableUserNames():
    lab_package_path = getLabPackagePath()
    
    user_config_files = [os.path.split(f)[1] for f in glob.glob(os.path.join(lab_package_path, 'config', '*.yaml'))]
    user_names = [f.split('_config')[0] for f in user_config_files]
    return user_names


def getUserConfiguration(user_name):
    lab_package_path = getLabPackagePath()
    path_to_config_file = os.path.join(lab_package_path, 'config', user_name + '_config.yaml')
    with open(path_to_config_file, 'r') as ymlfile:
        cfg = yaml.safe_load(ymlfile)
    return cfg


def getAvailableRigConfigs(user_name):
    if user_name is not None:
        cfg = getUserConfiguration(user_name)
        rig_configs = list(cfg.get('rig_config').keys())
        return rig_configs
    else:
        print('Select a user first')
        return None


def getRigConfiguration(user_name, rig_name):
    user_config = getUserConfiguration(user_name)

    return user_config.get('rig_config').get(rig_name)


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

def getParameterPresetDirectory(cfg):
    lab_package_path = getLabPackagePath()

    return os.path.join(lab_package_path, cfg['parameter_presets_dir'])

def getDevices(cfg):
    configured_devices = {}
    for dev in cfg['rig_config'].get(cfg['rig_name']).get('devices'):
        configured_devices[dev] = cfg['rig_config'].get(cfg['rig_name']).get('devices')[dev]
    return configured_devices

def getModuleNameFromPath(path):
    return os.path.split(path)[-1].split('.')[0]