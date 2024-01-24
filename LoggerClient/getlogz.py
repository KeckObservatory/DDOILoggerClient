#! @PYTHON3@
import argparse 
import sys
from getlogz_functions import get_logz, print_ouput_json_table
import os
import yaml

def get_default_config_loc(dev=False, configname='logger_cfg.yaml'):
    config_loc = os.path.abspath(os.path.join(os.path.dirname(__file__), configname))
    kroot_config_loc = os.path.join('@CFGDIR@', configname)

    if not dev and os.path.isfile(kroot_config_loc):
        # .sin substitution comes from Makefile
        config_loc = kroot_config_loc 
    return config_loc


def get_url(config_parser):
    server = 'ZMQ_LOGGING_SERVER' if not dev else 'LOCAL_ZMQ_LOGGING_SERVER'
    config = config_parser[server]
    url = config.get('url')
    return url 

if __name__ == '__main__':
    dev = '--dev' in sys.argv
    parser = argparse.ArgumentParser(description="Get logs from logger database")
    parser.add_argument("--dev", nargs='?', help="include adds config file in kroot")

    config_loc = get_default_config_loc(dev)
    with open(config_loc, 'r') as f:
        config = yaml.safe_load(f)


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