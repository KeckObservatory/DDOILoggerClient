#! @PYTHON3@
import pdb
import argparse 
import sys
from getlogz_functions import get_logz, print_ouput_json_table
import os
import yaml

def get_default_config_loc(dev=False):
    if dev:
        config_loc = os.path.abspath(os.path.dirname(__file__))
    else:
        # .sin substitution comes from Makefile
        config_loc = '@CFGDIR@'

    config_loc = os.path.join(config_loc, 'logger_cfg.yaml')
    return config_loc


def get_url(config_parser):
    server = 'ZMQ_LOGGING_SERVER' if not dev else 'LOCAL_ZMQ_LOGGING_SERVER'
    config = config_parser[server]
    url = config.get('url')
    return url 

if __name__ == '__main__':
    dev = not 'kroot' in os.path.abspath(os.path.dirname(__file__)).lower() # sets to true if not using KROOT
    config_loc = get_default_config_loc(dev)
    with open(config_loc, 'r') as f:
        config = yaml.safe_load(f)
    parser = argparse.ArgumentParser(description="Get logs from logger database")

    for key in [*config['ARG_REQUIRED_KEYS'], *config['ARG_KEYS']]:
        argType = config['ARG_TYPES'][key]
        argHelp = config['ARG_HELP'].get(key, None)
        argDefault = config['ARG_DEFAULTS'].get(key, None)
        parser.add_argument(f"--{key}", 
                             type=getattr(__builtins__, argType), 
                             default=argDefault,
                             help=argHelp
                             )

    args = parser.parse_args()

    url = get_url(config)
    logs = get_logz(url, **vars(args))
    print_ouput_json_table(logs)
    sys.exit()