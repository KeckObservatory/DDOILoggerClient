#from DDOILogger import ZMQHandler
from DDOILoggerClient import DDOILogger as dl
import os
import logging
from logging import StreamHandler, FileHandler
import pdb

def create_logger(subsystem, configLoc, author, progid, semid, fileName, loggername):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    kwargs = {'subsystem':subsystem, 'author':author, 'progid':progid, 'semid':semid, 'loggername': loggername}
    zmq_log_handler = dl.ZMQHandler(configLoc, local=True, **kwargs)
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

if __name__=='__main__':
    subsystem='MOSFIRE'
    configLoc= None 
    author="ttucker"
    progid="2022B"
    semid="1234"
    fileName = "test.log"
    loggername = 'ddoi'

    logger = create_logger(subsystem, configLoc, author, progid, semid, fileName, loggername)
  
    logger.warning('test', extra={'subsystem': 'example subsystem', 'author': 'tyler'})
