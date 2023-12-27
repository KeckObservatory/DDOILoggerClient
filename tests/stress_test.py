import pdb
import yaml
import os
import json
from pymongo import MongoClient
import zmq
import sys
from datetime import datetime
import logging 
from logging import StreamHandler, FileHandler
from time import sleep

sys.path.append('../DDOILoggerClient')
from DDOILogger import ZMQHandler
# from DDOILoggerClient import DDOILogger as dl 


def get_mongodb(db_name):
    client = MongoClient(port = 27017)
    return client[db_name] 

def create_logger(config, subsystem, author, progid, semid, fileName, loggername):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    local=True
    zmq_log_handler = ZMQHandler(config, local=local, **{'subsystem':subsystem, 
                                            'author':author, 
                                            'progid':progid, 
                                            'semid':semid, 
                                            'loggername':loggername})
    ch = StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    fl = FileHandler(fileName)
    fl.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(zmq_log_handler)
    logger.addHandler(ch)
    logger.addHandler(fl)
    return logger

def init_logger(loggername):
    subsystem='MOSFIRE'
    config_loc = os.path.join(os.getcwd(), 'logger_cfg.yaml')
    with open(config_loc, 'r') as f:
        config = yaml.safe_load(f)
    author="ttucker"
    progid="2022B"
    semid="1234"
    fileName = "stress_test.log"
    logger = create_logger(config, subsystem, author, progid, semid, fileName, loggername)
    return logger


def init_zmq(url):
    context = zmq.Context()
    socket = context.socket(zmq.DEALER)
    socket.connect(url)
    poll = zmq.Poller()
    poll.register(socket, zmq.POLLIN)
    return socket, poll

if __name__=='__main__':
    db = get_mongodb('logs')
    url="tcp://localhost:5570"
    loggername = 'ddoi'
    logger = init_logger(loggername)
    # url="tcp://10.95.1.94:5570"
    socket, poll = init_zmq(url)
    counter = 0
    while True:
        counter += 1
        msg = f"stress test timestamp: {datetime.timestamp(datetime.now())}"
        logger.warning(msg)
        sleep(.1)

        # request message with zeromq
        reqParams = {'nLogs': 1, 'loggername': loggername}
        request = {'msg_type': 'request_logs', 'body': reqParams}
        socket.send_string(json.dumps(request)) #  zeromq method is faster
        sockets = dict(poll.poll(5000))
        resp = json.loads(socket.recv()) if socket in sockets else {}

        assert resp.get('resp', False) == 200, f"logs not recieved: {resp.get('msg', 'no msg found')}"
        dbMsg = resp['msg'][0]['message']
        assert dbMsg in msg,  f"{msg} not a match!"

