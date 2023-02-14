import configparser
import pdb
import json
import zmq
import sys
import os
import pytest
import sys
sys.path.append('../DDOILoggerClient')
from DDOILogger import DDOILogger


subsystem='MOSFIRE'
config=None
author="ttucker"
progid="2022B"
semid="1234"
rs = 'test log' 

config_parser = configparser.ConfigParser()

config_loc = os.path.join(os.getcwd(), 'logger_cfg.ini')

@pytest.mark.client
def test_logger_client():

    logger = DDOILogger(subsystem, config_loc, author, progid, semid)
    alive = logger.server_interface._check_cfg_url_alive()
    assert alive, 'heartbeat failing'

    metadata = logger.server_interface._get_meta_options()
    subsystems = metadata.get('subsystems', [])
    levels = metadata.get('levels', [])
    assert len(subsystems) > 0, 'subsystems not found'
    assert len(levels) > 0, 'levels not found'

    msg = 'test msg'
    ack = logger.warn(msg)
    resp = ack.get('resp', 400)
    msg = ack.get('msg', None)
    assert resp == 200, 'message not sent'
    assert 'log submitted to database' in msg, 'message not added to database'

    level = 'test'
    ack = logger.add_level(level)
    assert ack.get('resp', False) == 200, f"did not set level. {ack}"
    subsys = 'testinst'
    iden= 'TESTINST'
    ack = logger.add_subsystem(subsys, iden)
    assert ack.get('resp', False) == 200, f"did not set subsystem. {ack}"

# @pytest.mark.client
# def test_request_metadata_options():

#     logger = DDOILogger(subsystem, config_loc, author, progid, semid)
#     metadata = logger._get_meta_options()
#     subsystems = metadata.get('subsystems', [])
#     levels = metadata.get('levels', [])
#     assert len(subsystems) > 0, 'subsystems not found'
#     assert len(levels) > 0, 'levels not found'

# @pytest.mark.client
# def test_log():

#     logger = DDOILogger(subsystem, config_loc, author, progid, semid)
#     msg = 'test msg'
#     ack = logger.warn(msg)
#     resp = ack.get('resp', 400)
#     msg = ack.get('msg', None)
#     assert resp == 200, 'message not sent'
#     assert 'log submitted to database' in msg, 'message not added to database'

@pytest.mark.client
def test_request_logs():

    context = zmq.Context()
    socket = context.socket(zmq.DEALER)
    url = "tcp://localhost:5570"
    socket.connect(url)
    poll = zmq.Poller()
    poll.register(socket, zmq.POLLIN)

    nLogs = 10
    reqParams = {'nLogs': nLogs }
    msg = {'msg_type': 'request_logs', 'body': reqParams}
    socket.send_string(json.dumps(msg)) #  zeromq method is faster

    sockets = dict(poll.poll(1000))
    resp = json.loads(socket.recv()) if socket in sockets else {}
    assert resp.get('resp', False) == 200, f"logs not recieved: {resp.get('msg', 'no msg found')}"
    logs = resp.get('msg')
    assert len(logs) == nLogs, f'logs not returned, nLogs {nLogs}!={len(logs)}'

if __name__ == '__main__':
    testCmd = 'python -m pytest -m client'
    os.system(testCmd)
