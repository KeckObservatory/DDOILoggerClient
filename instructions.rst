============================
Using the Logger (Prototype)
============================

This is a stripped down, proof of concept for the logger. It is missing core
features like offline running and generation of local logs, but those are simple
to implement and aren't in need of testing. The deployed version will have those
features, and not require as much fiddling to get running as this one.

These instructions will only work for a server already on Keck's internal
network, since the server is not secured and isn't configured for real use yet.


Setup
---------------------

Clone this repo:

.. code-block:: bash

 git clone https://github.com/KeckObservatory/DDOILoggerClient.git

Edit the server address in the config to testing url (10.96.10.116:5005):

.. code-block:: bash

 vi DDOILoggerClient/ddoiloggerclient/configs
 
 >>>url=http://10.96.10.116:5005

Install the package:

.. code-block:: bash

 cd DDOILoggerBuild
 pip install .


Using the Logger
----------------

.. code-block:: python
 
 #import the logger
 from ddoiloggerclient import DDOILogger

 # Create a logging instance. There are several arguments that can be set.
 # See the docstring for this class for more info. 
 logger = DDOILogger.DDOILogger(subsystem="NIRES", author="Luke Skywalker")

 logger.info("a logging message")