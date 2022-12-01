import configparser
import pdb
import json
from pymongo import MongoClient
import zmq
import os
import sys
from datetime import datetime
import logging 
from logging import StreamHandler, FileHandler
from time import sleep
sys.path.append('../DDOILoggerClient')

#from DDOILogger import ZMQHandler
from DDOILoggerClient import ZMQHandler


def get_mongodb():
    client = MongoClient(port = 27017)
    return client['logs'] 

def create_logger(subsystem, configLoc, author, progid, semid, fileName):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    zmq_log_handler = ZMQHandler(subsystem, configLoc, author, progid, semid)
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

def init_logger():
    subsystem='MOSFIRE'
    configLoc= None 
    author="ttucker"
    progid="2022B"
    semid="1234"
    fileName = "stress_test.log"
    logger = create_logger(subsystem, configLoc, author, progid, semid, fileName)
    return logger

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

def init_zmq(url):
    context = zmq.Context()
    socket = context.socket(zmq.DEALER)
    socket.connect(url)
    poll = zmq.Poller()
    poll.register(socket, zmq.POLLIN)
    return socket, poll

if __name__=='__main__':
    logger = init_logger()
    db = get_mongodb()
    # url="tcp://localhost:5570"
    url="tcp://10.95.1.94:5570"
    socket, poll = init_zmq(url)
    counter = 0
    while True:
        counter += 1
        msg = f"stress test timestamp: {datetime.timestamp(datetime.now())}"
        logger.warning({"msg": msg, "level": "warning"})
        sleep(.1)

        # request message with zeromq
        reqParams = get_logs(nLogs=1)
        request = {'msg_type': 'request_logs', 'body': reqParams}
        socket.send_string(json.dumps(request)) #  zeromq method is faster
        sockets = dict(poll.poll(5000))
        resp = json.loads(socket.recv()) if socket in sockets else {}

        assert resp.get('resp', False) == 200, f"logs not recieved: {resp.get('msg', 'no msg found')}"
        dbMsg = resp['msg'][0]['message']
        assert dbMsg in msg,  f"{msg} not a match!"

