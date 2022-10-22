#! @PYTHON3@
import pdb
import argparse 
import json
import zmq
import sys
from datetime import datetime, timedelta
import requests
import os
import configparser

def get_logs(subsystem=None, startDate=None, endDate=None, nLogs=None, dateFormat=None):
    params = {} 
    if startDate:
        params['startDate'] = startDate 
    if endDate:
        params['endDate'] = endDate 
    if subsystem:
        params['subsystem'] = subsystem 
    if nLogs:
        params['nLogs'] = nLogs 
    if dateFormat:
        params['dateFormat'] = dateFormat 
    return params 


def get_last_n_minutes_logs(subsystem, minutes, endDate=None, dateFormat=None):
    if not endDate:
        endDate = datetime.utcnow()
    else:
        endDate = datetime.strptime(endDate, dateFormat)
    startDate = endDate - timedelta(minutes=minutes)
    startDateStr = datetime.strftime(startDate, dateFormat)
    endDateStr = datetime.strftime(endDate, dateFormat)
    params = get_logs(subsystem, startDateStr, endDateStr, dateFormat=dateFormat)
    return params
    
def get_default_config_loc(dev=False):
    if dev: #todo work on making this bulletproof
        config_loc = os.path.abspath(os.path.dirname(__file__))
    else:
        config_loc = '/kroot/rel/default/data/ddoilogger/'

    config_loc = os.path.join(config_loc, 'logger_cfg.ini')
    return config_loc

def print_ouput_json_table(logs):
    excl = [ 'utc_sent' ]
    keys = ([x for x in logs[0].keys() if x not in excl])
    print(', '.join(keys))
    for log in logs:
        row = []
        for key, val in log.items():
            if key in excl: continue
            if isinstance(val, dict):
                row.append(str(val))
                continue
            if isinstance(val, str):
                row.append(val)
                continue
        print(", ".join(row))
                
        # print(', '.join([str(x) for x in log.values()]))

def init_zmq(url):
    context = zmq.Context()
    socket = context.socket(zmq.DEALER)
    # identity = u'worker-%s' % self.subsystem
    # self.socket.identity = identity.encode('ascii')
    socket.connect(url)
    poll = zmq.Poller()
    poll.register(socket, zmq.POLLIN)
    return socket, poll
        
def str_2_bool(val):
    if isinstance(val, bool):
        return val
    if val.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif val.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected')

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
    print(config_loc)
    config_parser = configparser.ConfigParser()
    config_parser.read(config_loc)
    server = 'ZMQ_LOGGING_SERVER' if not dev else 'LOCAL_ZMQ_LOGGING_SERVER'
    config = config_parser[server]
    url = config.get('url')

    socket, poll = init_zmq(url)

    if args.minutes:
        reqParams = get_last_n_minutes_logs(args.subsystem, args.minutes, args.endDate)
    else:
        reqParams = get_logs(subsystem=args.subsystem, startDate=args.startDate, endDate=args.endDate, nLogs=args.nLogs, dateFormat=args.dateFormat)

    msg = {'msg_type': 'request_logs', 'body': reqParams}
    socket.send_string(json.dumps(msg)) #  zeromq method is faster

    sockets = dict(poll.poll(5000))
    resp = json.loads(socket.recv()) if socket in sockets else {}
    assert resp.get('resp', False) == 200, f"logs not recieved: {resp.get('msg', 'no msg found')}"
    logs = resp.get('msg')

    pdb.set_trace()
    print_ouput_json_table(logs)
    sys.exit()
