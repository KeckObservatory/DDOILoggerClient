#! @PYTHON3@
import argparse 
import json
import zmq
from datetime import datetime, timedelta


def format_log_params(subsystem=None, startDate=None, endDate=None, nLogs=None, dateFormat=None):
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
    params = format_log_params(subsystem, startDateStr, endDateStr, dateFormat=dateFormat)
    return params
    

def print_ouput_json_table(logs):
    excl = [ 'utc_sent' ]
    keys = ([x for x in logs[0].keys() if x not in excl])
    print('\t '.join(keys))
    for log in logs:
        row = []
        for key, val in log.items():
            if key in excl: continue
            if isinstance(val, dict):
                row.append(str(val))
                continue
            if not val:
                row.append('NA')
            if isinstance(val, str):
                row.append(val)
                continue
        print("\t ".join(row))
                
        # print(', '.join([str(x) for x in log.values()]))

def init_zmq(url):
    context = zmq.Context()
    socket = context.socket(zmq.DEALER)
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

def get_logz(url, subsystem, minutes, startDate, endDate, nLogs, dateFormat):
    socket, poll = init_zmq(url)
    if minutes:
        reqParams = get_last_n_minutes_logs(subsystem, minutes, endDate, dateFormat)
    else:
        reqParams = format_log_params(subsystem=subsystem, startDate=startDate, endDate=endDate, nLogs=nLogs, dateFormat=dateFormat)
    msg = {'msg_type': 'request_logs', 'body': reqParams}
    socket.send_string(json.dumps(msg)) #  zeromq method is faster
    sockets = dict(poll.poll(5000))
    resp = json.loads(socket.recv()) if socket in sockets else {}
    assert resp.get('resp', False) == 200, f"logs not recieved: {resp.get('msg', 'no msg found')}"
    logs = resp.get('msg')
    return logs
