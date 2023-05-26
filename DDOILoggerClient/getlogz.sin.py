#! @PYTHON3@
import argparse 
import sys
import configparser
from getlogz_functions import * 


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Get logs from logger database")
    parser.add_argument('--subsystem', type=str, required=False, default=None,
                         help="subsystem specific logs")
    parser.add_argument('--startDate', type=str, required=False, default=None,
                         help="starting date to retrieve logs")
    parser.add_argument('--endDate', type=str, required=False, default=None,
                         help="ending date to retrieve logs")
    parser.add_argument('--nLogs', type=int, required=False, default=100,
                         help="maximum number of logs to output")
    parser.add_argument('--minutes', type=int, required=False, default=None,
                         help="set to retrieve last n minutes of logs")
    parser.add_argument('--dateFormat', type=str, required=False, default='%Y-%m-%dT%H:%M:%S',
                         help="how the dates are formatted (default is YYYY-mm-ddTHH:MM:SS)")
    parser.add_argument('--dev', type=str_2_bool, required=False, default=False,
                         help="set to true if working locally")

    args = parser.parse_args()
    dev = args.dev

    config_loc = get_default_config_loc(dev)
    config_parser = configparser.ConfigParser()
    config_parser.read(config_loc)
    server = 'ZMQ_LOGGING_SERVER' if not dev else 'LOCAL_ZMQ_LOGGING_SERVER'
    config = config_parser[server]
    url = config.get('url')

    logs = get_logz(url, args.subsystem, args.minutes, args.startDate, args.endDate, args.nLogs, args.dateFormat )
    print_ouput_json_table(logs)
    sys.exit()