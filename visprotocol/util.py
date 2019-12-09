import os
import glob
import visprotocol
import inspect
import yaml


def getAvailableUserNames():
    # looks for user names based on .yaml config files in visprotocol/config directory
    # Filenames should be: USER_config.yaml
    config_dir = os.path.join(os.path.abspath(os.path.join(os.path.split(__file__)[0], os.pardir)), 'config')
    user_config_files = [os.path.split(f)[1] for f in glob.glob(os.path.join(config_dir,'*.yaml'))]

    user_names = [f.split('_config')[0] for f in user_config_files]
    return user_names


def getAvailableRigConfigs(user_name):
    if user_name is not None:
        cfg = getUserConfiguration(user_name)
        rig_configs = list(cfg.get('rig_config').keys())
        return rig_configs
    else:
        print('Select a user first')
        return None


def getUserConfiguration(user_name):
    path_to_config_file = os.path.join(inspect.getfile(visprotocol).split('visprotocol')[0], 'visprotocol', 'config', user_name + '_config.yaml')
    with open(path_to_config_file, 'r') as ymlfile:
        cfg = yaml.safe_load(ymlfile)
    return cfg

def getRigConfiguration(user_name, rig_name):
    # open user config file and find available rig configurations
    path_to_config_file = os.path.join(inspect.getfile(visprotocol).split('visprotocol')[0], 'visprotocol', 'config', user_name + '_config.yaml')
    with open(path_to_config_file, 'r') as ymlfile:
        cfg = yaml.safe_load(ymlfile)
    rig_cfg = cfg.get('rig_config').get(rig_name)

    return rig_cfg
