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

    def __init__(self, url, configLoc, **kwargs):
        StreamHandler.__init__(self)
        self.zmq_client_logger = DDOILogger(url, configLoc, **kwargs)

    def emit(self, record):
        msg = self.format(record)
        msg = msg.replace('\'', '\"')
        try:
            msg = json.loads(msg)
            text = msg.get('msg', "")
            self.zmq_client_logger.send_log(text, msg)
        except JSONDecodeError as err:
            pass

"""Instantiable class for logging within the DDOI ecosystem
"""
class DDOILogger():
    """Module that is used to log DDOI messages.
    
    """
    def __init__(self, url, configLoc=None, **kwargs):
        """Constructor function for the DDOI logger
        """

        # Open the config file
        if configLoc is None:
            configLoc = self._get_default_config_loc()
        config_parser = configparser.ConfigParser()
        config_parser.read(configLoc)

        self.config = config_parser

        self.server_interface = ServerInterface(url, **kwargs)

    def _send_message(self, message, sendAck=True):
        """Sends a log to the url designated in the config

        Parameters
        ----------
        message : str
            a JSON formatted string containing the information the backend expects
        sendAck : (bool)
            set to true to enable recieving an acknoledgement. 
            note that it takes much longer for the ack to arrive.
        """
        resp = json.loads(self.server_interface._send_log(message, sendAck))
        return resp

    @staticmethod
    def _format_message(message, logSchema, **kwargs):
        """Formats a message into a dict for delivery to the backend

        Parameters
        ----------
        message : str
            Log message

        Returns
        -------
        Dict 
            a Dict containing the log message and metadata, formatted for submisison to the logging backend
        """
        log = {
            'utc_sent' : datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%Z'),
            'message' : message
            **{ key: kwargs.get(key) for key in logSchema},
        }
        return log
    
        
    def send_log(self, message, sendAck=True, **kwargs):
        formatted_message = self._format_message(message, 
                                                    self.config['log_schema']['log_schema'],
                                                    **kwargs
                                                )
        resp = self._send_message(formatted_message, sendAck)
        return resp
    

    def _get_default_config_loc(self):
        config_loc = os.path.abspath(os.path.dirname(__file__))
        config_loc = os.path.join(config_loc, './logger_cfg.ini')
        return config_loc

    def add_level(self, level):
        resp = self.server_interface.send_level(level)
        return json.loads(resp)

    def add_subsystem(self, subsystem, iden):
        resp = self.server_interface.send_subsystem(subsystem, iden)
        return json.loads(resp)

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

    def __init__(self, url, poll_timeout=1000, **kwargs):
        self.poll_timeout = poll_timeout 
        self.url = url 
        self.subsystem = kwargs.get('subsystem', 'unknown')
        # initialize zero mq client
        self._init_zmq()

    def _init_zmq(self):
        context = zmq.Context()
        self.socket = context.socket(zmq.DEALER)
        now = datetime.now().strftime('%Y%m%dT%H%M%S%Z'),
        identity = f"{self.subsystem}-{os.getpid()}-{now}"
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