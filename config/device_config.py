import yaml

with open("config/device_config.yaml", 'r') as file:
    DEVICE_CONFIG = yaml.safe_load(file)