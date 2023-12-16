from datetime import datetime

import os
import configparser
import json
from json import JSONDecodeError
import zmq
import pdb
from logging import StreamHandler

class ZMQHandler(StreamHandler):
    """

    Args:
        StreamHandler (_type_): _description_
    """

    def __init__(self, url, config=None, **kwargs):
        StreamHandler.__init__(self)
        self.set_name('ZMQHandler')

        if config is None:
            configLoc = self._get_default_config_loc()
            config = configparser.ConfigParser()
            config.read(configLoc)
            config = dict(config)

        self.logSchema = [*config['LOGGER']['LOG_SCHEMA_BASE'].replace(' ', '').split(','),
                    *config['LOGGER']['LOG_SCHEMA'].replace(' ', '').split(',') ]
        self.zmq_client_logger = DDOILogger(url, config, **kwargs)

    def emit(self, record):
        msg = self.format(record)
        msg = msg.replace('\'', '\"')
        try:
            msg = json.loads(msg)
            text = msg.get('msg', "")
            self.zmq_client_logger.send_log(text, self.logSchema, kwargs=msg)
        except JSONDecodeError as err:
            pass

"""Instantiable class for logging within the DDOI ecosystem
"""
class DDOILogger():
    """Module that is used to log DDOI messages.
    
    """
    def __init__(self, url, logSchema=None, **kwargs):
        """Constructor function for the DDOI logger
        """

        # Open the config file
        self.DATE_FORMAT = '%Y-%m-%d %H:%M:%S.%Z'
        self.server_interface = ServerInterface(url, idName=kwargs.get('subsystem', 'unknown'))
        self.kwargs = kwargs

    def send_log(self, message, logSchema, sendAck=True, **kwargs):

        log = dict()
        for key in logSchema:
            log[key] = kwargs[key] if kwargs.get(key, False) else self.kwargs.get(key, None)
        log['utc_sent'] = datetime.utcnow().strftime(self.kwargs.get('dateFormat', self.DATE_FORMAT))
        log['message'] = message
        resp = json.loads(self.server_interface._send_log(log, sendAck))
        return resp
    
    def _get_default_config_loc(self):
        config_loc = os.path.abspath(os.path.dirname(__file__))
        config_loc = os.path.join(config_loc, './logger_cfg.ini')
        return config_loc

    @staticmethod
    def handle_response(resp, log, path='./failedLogs.txt'):
        """sends failed logs to local storage to be ingested later 

        Parameters
        ----------
        resp : dict 
            response from logger server 
        log : dict 
            the msg sent to the logger server 
        path : str
            path to write log files
        """
        try: 
            if not resp.get('resp', None) == 200:
                    
                with open(path, 'a+') as f:
                    msgResp = {'resp': resp, 'log': log}
                    msgRespStr = json.dumps(msgResp) + '\r'
                    f.write(msgRespStr)
        except Exception as err:
            print(f'handle_response error: {err}')
    
class ServerInterface():
    """ZeroMQ client that interfaces with the server
    """

    def __init__(self, url, poll_timeout=1000, idName='unknown'):
        self.poll_timeout = poll_timeout 
        self.url = url 
        self.idName = idName 
        # initialize zero mq client
        self._init_zmq()

    def _init_zmq(self):
        context = zmq.Context()
        self.socket = context.socket(zmq.DEALER)
        now = datetime.now().strftime('%Y%m%dT%H%M%S%Z')
        identity = f"{self.idName}-{os.getpid()}-{now}"
        self.socket.identity = identity.encode('ascii')
        self.socket.connect(self.url)
        print('Client %s started' % (identity))
        self.poll = zmq.Poller()
        self.poll.register(self.socket, zmq.POLLIN)

    def _check_cfg_url_alive(self):
        """Sends a heartbeat message to server and checks that message returns

        Returns
        -------
            boolean : If True then message was recieved, otherwise False
        """
        try:
            msg = {'msg_type': 'heartbeat', 'body': None }
            self.socket.send_string(json.dumps(msg)) #  zeromq method is faster
            sockets = dict(self.poll.poll(self.poll_timeout))
            resp = self.socket.recv() if self.socket in sockets else {}
            resp = json.loads(resp)
            return resp.get('resp', None) == 200
        except Exception as err:
            return False

    def _send_log(self, body, sendAck=True):
        """Sends a log request message to the server

        Parameters
        ---------- 
            body (dict): the log message body that is to be sent to the server
            sendAck (bool): set to true to enable recieving an acknoledgement. 
            note that it takes much longer for the ack to arrive.

        Returns
        -------
            dict: an acknowledgment message from the server
        """
        msg = {'msg_type': 'log', 'body': body}
        self.socket.send_string(json.dumps(msg))
        if sendAck:
            sockets = dict(self.poll.poll(1000))
            if self.socket in sockets:
                resp = self.socket.recv()
                return resp
        else:
            return b"{}"