import yaml

with open("config.yml", "r") as config_file:
    config = yaml.full_load(config_file)
