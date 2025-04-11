# create predefine path with config
# read config
# extract version
# send data to module
# get the data from module


import os
import sys
import yaml

from settings import config_file, logger


def isfile(file):
    try:
        return os.path.isfile(file)
    except Exception as e:
        print(f"Found the error: {e}")
        return False


def open_file(file):
    if isfile(file):
        with open(file) as f:
            return f.read()


def validator(data: dict):
    error = False
    if not data:
        logger.error("file doesn't contain any data")
        error = True

    if "version" not in data:
        logger.error("Please specify the version")
        error = True

    if "project" not in data:
        logger.fatal("Project description is missing")
        error = True

    if error:
        sys.exit(1)

    return data

def parser(data):
    pass

def main():
    yaml_config_data = open_file(config_file)
    config_data = validator(yaml.safe_load(yaml_config_data))
    parser(config_data)



if __name__ == '__main__':
    main()
    # pass
