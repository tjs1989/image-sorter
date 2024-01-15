import yaml


def get_yaml_keys(filepath):
    yaml_file = load_yaml_file(
        filename=filepath)
    return {key.lower(): value for key, value in yaml_file.items()}


def load_yaml_file(filename):
    with open(filename, 'r') as yaml_file:
        yaml_contents = yaml.safe_load(yaml_file)
    yaml_file.close()
    return yaml_contents
