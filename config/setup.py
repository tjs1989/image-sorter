import os

from utils.load_files import get_yaml_keys

script_dir = os.path.dirname(__file__)

def get_system_config():
    system_config_filepath = os.path.join(script_dir, "system_config.yaml")
    return get_yaml_keys(system_config_filepath)
