.. DDOILoggerClient documentation master file, created by
   sphinx-quickstart on Thu Oct 13 15:10:11 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to DDOILoggerClient's documentation!
============================================

Overview:
---------
The DDOI Logger comprises of a single server, 
and multiple clients. The client sends message logs to the server, 
which are then processed and stored in the database. 
This implementation of the logger described in the Logging Tool 
Design Document handles messages quickly and to scale with TCP 
protocol, handled by the ZeroMQ library. 

Architecture
------------
The ZeroMQ pattern uses a asynchronous server model by the logging
 makes use of Dealer and Server sockets, described here. 
 See below for client-server architecture diagram.

.. image:: _static/async_server.png
  :width: 600
  :alt: Alternative text

The logger allows for multiple clients to connect at one time. 
Messages from the clients are routed to a pool of workers that 
process them. Passing a message from client to a worker and vice 
versa requires a broker. 



.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules
   build
   api

Scalability and Performance
---------------------------

The DDOI Logger is designed to be scalable for hundreds of clients,
sending hundreds of logs per second but in practice will only 
really be working with 10 clients, sending 10 logs per second. 
Since there are multiple workers, routing through a single broker,
it is possible to add more workers to handle additional loads 
should the need arise.                         

Security
--------

The DDOI Logger does not implement any access control, 
authentication, or encryption. It should not be used where 
security is required.

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
