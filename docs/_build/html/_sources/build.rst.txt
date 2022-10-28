

Client Dev Build
----------------
The DDOILoggerClient Python module is found on Github. It is installed by first cloning the 
repository to the server where it is to be run. Then the module is installed with the 
pip command `pip install .` while in the DDOILoggerClient directory. This installs 
the client to the current working python’s pip wheel. 

Deployment (Kroot) Build
------------------------

1. SVN Checkout `/kroot/src/util/loggerclient/`
2. Run `make clean && make` to clone the repo from git hub
3. CD to `/kroot/src/util/loggerclient/DDOILoggerClient`
4. run `make clean && make && make install`

Running the Logger Client
-------------------------

The logger client is imported and run just as any Python module. See the code below for an example client.


.. code-block:: python 

    from ddoiloggerclient import DDOILoggerClient

    subsystem="MOSFIRE"
    config=None
    author="authorNameHere"
    progid="AProgid"
    semid="Asemid"
    logger = DDOILogger.DDOILogger(subsystem, config, author, progid, semid)
    msg = "an example message"
    logger.debug(msg) 
                

Logger has levels: debug, info, warn, and error.
The Upon creation, the client sends a heartbeat message to the server, checking that it is alive. 
If it is not, the logger returns an error. The logger then requests valid subsystems 
and log levels. The logger looks for the server running on port 5570, or whatever is written in 
the configuration file located at ./DDOILoggerClient/logger_cfg.ini.


Server Deployment
-----------------

The server depends on the configuration file located at 
./configs/server_cfg.ini. This describes the host address,
port number, and number of workers. Server is deployed by 
first installing the libraries written in ``requirements.txt``
file with the pip command 
  
.. code-block:: console 

    conda activate logger && pip -e requirements.txt 
  
The server running on vm-ddoiloggerbuild-new uses the ``logger``
virtual environment. 

Deployment
----------

The Server that spawns and runs the workers runs as a daemon 
using the Linux process manager Systemd. Scripts are run as 
daemons and restarted should they unexpectedly exit.  
Systemd configuration files are stored 
in ``/etc/systemd/system/zmq_server.service``, shown below.



.. code-block:: console 

    [Unit]
    Description=ZMQ Logger Server
    After=multi-user.target

    [Service]
    Type=simple
    Restart=always
    ExecStart=/home/dsieng/.conda/envs/logger/bin/python /home/dsieng/DDOILoggerServer/zmq_server.py
                                    
    [Install]
    WantedBy=multi-user.target    

You can start, stop, and check the status of the daemon with the command
``systemd start/stop/status zmq_server``  
Note how the service uses a Conda environment to run a python instance. 
