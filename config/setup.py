import os

from utils.load_files import get_yaml_keys

script_dir = os.path.dirname(__file__)
project_root = os.path.dirname(script_dir)

def get_system_config():
    system_config_filepath = os.path.join(script_dir, "system_config.yaml")
    return get_yaml_keys(system_config_filepath)

def resolve_path(path):
    return path if os.path.isabs(path) else os.path.join(project_root, path)
