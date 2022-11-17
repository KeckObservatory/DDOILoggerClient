#from DDOILogger import ZMQHandler
from DDOILoggerClient import DDOILogger as dl
import os
import logging
from logging import StreamHandler, FileHandler
import pdb

def create_logger(subsystem, configLoc, author, progid, semid, fileName):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    zmq_log_handler = dl.ZMQHandler(subsystem, configLoc, author, progid, semid)
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
    config_loc = os.path.join(os.getcwd(), 'logger_cfg.ini')
    subsystem='MOSFIRE'
    configLoc= None 
    author="ttucker"
    progid="2022B"
    semid="1234"
    fileName = "test.log"

    logger = create_logger(subsystem, configLoc, author, progid, semid, fileName)
  
    logger.warning({"msg": "logger handler test2", "level": "warning"})
