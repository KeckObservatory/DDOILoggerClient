from datetime import datetime

import os
import configparser
import json
import requests
import zmq
import pdb

"""Instantiable class for logging within the DDOI ecosystem
"""
class DDOILogger():

    def __init__(self, subsystem=None, config=None, author=None, progid=None, semid=None):
        """Constructor function for the DDOI logger

        Parameters
        ----------
        system : str, optional
            subsystem that this logger is serving. If not specified when the logger object is created, it must be entered each time a log event occurs. By default None
        config : str or pathlike, optional
            path to the config file for this logger, if not using default path, by default None
        author : str, optional
            human readable description of who is submitting these logs, by default None
        progid : _type_, optional
            the program ID that led to this log event needing to be submitted, by default None
        semid : _type_, optional
            the semester ID that led to this log event needing to be submitted, by default None
        """

        # Open the config file
        if config is None:
            config = self._get_default_config_loc()
        config_parser = configparser.ConfigParser()
        config_parser.read(config)

        self.config = config_parser['LOGGING_SERVER']

        self.server_interface = ServerInterface(self.config, subsystem)

        if not self.server_interface.check_cfg_url_alive():
            ex_str = "Unable to access backend API at " + self.config['url']
            raise Exception(ex_str)

        # Initialize subsystems
        metadata = self.server_interface.get_meta_options()
        metadata = json.loads(metadata)
        subsystems = metadata.get('subsystems', [])
        levels = metadata.get('levels', [])
        self.subsystems = [subsystem['identifier'] for subsystem in subsystems]

        for sub in self.subsystems:
            setattr(self, sub, sub)
        
        # Initialize event types
        self.levels = levels
        for level in self.levels:
            setattr(self, level, level)

        # Initialize logging levels (e.g. info, debug, warn, ...)

        for level in self.levels:
            setattr(self, level.lower(), self._log_function_factory(level))

        # Initialize "authorship" information
        if not subsystem is None:
            if not subsystem in self.subsystems:
                print(f"Entered an invalid system. Valid options are:")
                for s in self.subsystems:
                    print(f"\t{s}")
                return
            else:
                self.subsystem = subsystem

        if not author is None:
            self.author = str(author)
        else:
            print("No author specified. Author field will be blank")
            self.author = ""
        
        if not semid is None:
            self.semid = str(semid)
        else:
            print("No SemID specified. SemID field will be blank")
            self.semid = ""
        
        if not progid is None:
            self.progid = str(progid)
        else:
            print("No ProgID specified. ProgID field will be blank")
            self.progid = ""



    def _send_message(self, message):
        """Sends a log to the url designated in the config

        Parameters
        ----------
        message : str
            a JSON formatted string containing the information the backend expects
        """
        resp = self.server_interface.send_log(message)
        return resp

    @staticmethod
    def _format_message(message, level, author=None, subsystem=None, semid = None, progid = None):
        """Formats a message into a json string for delivery to the backend

        Parameters
        ----------
        message : str
            Log message
        level : str
            log level (e.g. info, warn, error, ...)
        author : str
            who authored this log
        subsystem : str, optional
            subsystem that this log came from. Should be grabbed from a class property, not manually entered. By default None
        semid : str, optional
            semester ID for the observering run that generated this log, by default None
        progid : str, optional
            program ID for the observing run that generated this log, by default None

        Returns
        -------
        str
            a JSON formatted string containing the log message and metadata, formatted for submisison to the logging backend
        """
        log = {
            'id' : 'UID',
            'utc_sent' : datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%Z'),
            'subsystem' : subsystem,
            'level' : level,
            'author' : author,
            'SEMID' : semid,
            'PROGID' : progid,
            'message' : message
        }
        return log
    
    def _log_function_factory(self, level):
        """Factory to create individual logging functions (e.g. "logger.info(...))

        Parameters
        ----------
        level : str
            logging level that should be used in database entries

        Returns
        -------
        func
            a logging function with a specific logging level set
        """
        
        def f(message, subsystem=None, semid=None, progid=None,):
            
            if self.subsystem is not None:
                # This means that this logger has been initialized with one subsystem
                formatted_message = self._format_message(message, level.upper(), self.author, subsystem=self.subsystem, semid=semid, progid=progid)
            else:
                # This means that we need to check if a subsystem was passed in
                if subsystem is None:
                    print("No subsystem specified for log. Aborting.")
                    return
                if not hasattr(self, subsystem):
                    print("Invalid subsystem entered. Aborting")
                    return
                formatted_message = self._format_message(message,
                                                         level.upper(),
                                                         self.author,
                                                         subsystem = subsystem,
                                                         semid = semid,
                                                         progid = progid)
                
            resp = self._send_message(formatted_message)
        
        return f

    def _get_default_config_loc(self):
        config_loc = os.path.abspath(os.path.dirname(__file__))
        config_loc = os.path.join(config_loc, './configs/logger_cfg.ini')
        return config_loc

    ###
    # HTTP Handler
    ###

class ServerInterface():

    def __init__(self, config, subsystem, poll_timeout=1000):
        self.poll_timeout = poll_timeout 
        self.config = config
        self.subsystem = subsystem
        # initialize zero mq client
        self._init_zmq()

    def _init_zmq(self):
        context = zmq.Context()
        self.socket = context.socket(zmq.DEALER)
        identity = u'worker-%s' % self.subsystem
        self.socket.identity = identity.encode('ascii')
        self.socket.connect(self.config['url'])
        print('Client %s started' % (identity))
        self.poll = zmq.Poller()
        self.poll.register(self.socket, zmq.POLLIN)

    def check_cfg_url_alive(self):
        try:
            print("trying to access server:")
            msg = {'msg_type': 'heartbeat', 'body': None }
            self.socket.send_string(json.dumps(msg)) #  zeromq method is faster
            sockets = dict(self.poll.poll(self.poll_timeout))
            resp = self.socket.recv() if self.socket in sockets else {}
            resp = json.loads(resp)
            return resp.get('resp', None) == 200
        except Exception as err:
            print("Unable to connect to URL")
            print(err)
            return False

    def get_meta_options(self):
        msg = {'msg_type': 'request_metadata_options', 'body': None}
        self.socket.send_string(json.dumps(msg)) #  zeromq method is faster
        sockets = dict(self.poll.poll(self.poll_timeout))
        resp = self.socket.recv() if self.socket in sockets else {}
        return resp
        
    def send_log(self, message):
        msg = {'msg_type': 'log', 'body': message}
        self.socket.send_string(json.dumps(msg))
        # sockets = dict(self.poll.poll(1000))
        # if self.socket in sockets:
        #     resp = self.socket.recv()
        #     return resp


