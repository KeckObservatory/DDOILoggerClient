from datetime import datetime
import os
import json
import zmq
import yaml
import pdb
from logging import StreamHandler


class ZMQHandler(StreamHandler):
    """

    Args:
        StreamHandler (_type_): _description_
    """

    def __init__(self, config=None, local=False, **kwargs):
        StreamHandler.__init__(self)
        self.set_name('ZMQHandler')

        if config is None:
            configLoc = self._get_default_config_loc()
            with open(configLoc, 'r') as f:
                config = yaml.safe_load(f)
        

        self.logSchema = [*config[kwargs.get('loggername').upper()]['LOG_SCHEMA_BASE'],
                    *config[kwargs.get('loggername').upper()]['LOG_SCHEMA']]
        url = config['ZMQ_LOGGING_SERVER']['url'] if not local else config['LOCAL_ZMQ_LOGGING_SERVER']['url'] 
        self.zmq_client_logger = Logger(url, config, **kwargs)
    
    @staticmethod
    def _get_default_config_loc():
        config_loc = os.path.abspath(os.path.dirname(__file__))
        config_loc = os.path.join(config_loc, './logger_cfg.yaml')
        return config_loc

    def emit(self, record):
        self.zmq_client_logger.send_log(record.msg, self.logSchema, record=record)

"""Instantiable class for logging within the DDOI ecosystem
"""
class Logger():
    """Module that is used to log DDOI messages.
    
    """
    def __init__(self, url, logSchema=None, **kwargs):
        """Constructor function for the DDOI logger
        """

        # Open the config file
        self.DATE_FORMAT = '%Y-%m-%d %H:%M:%S.%Z'
        self.server_interface = ServerInterface(url, idName=kwargs.get('subsystem', 'unknown'))
        self.kwargs = kwargs

    def send_log(self, message, logSchema, sendAck=True, record=None, test=False):

        log = dict()
        recordDict = record.__dict__ if record else dict() 
        for key in logSchema:
            log[key] = recordDict.get(key, self.kwargs.get(key, None))
        log['utc_sent'] = datetime.utcnow().strftime(self.kwargs.get('dateFormat', self.DATE_FORMAT))
        log['message'] = message
        if test:
            log['level'] = 'debug'
            log['loggername'] = 'DDOI'
        else:
            lvl = recordDict.get('levelname', self.kwargs.get('level', None))
            if not lvl:
                raise NotImplementedError('log level not specified')
            log['level'] = lvl.lower()
            loggername = recordDict.get('loggername', self.kwargs.get('loggername', None))
            if not loggername:
                raise NotImplementedError('loggername not specified')
            log['loggername'] = loggername.lower()
        resp = self.server_interface._send_log(log, sendAck)
        return json.loads(resp)
    
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
        return b"{}"
