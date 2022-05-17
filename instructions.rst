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

If the logger cant connect to that URL, it is possible that the server crashed.
Please let me know if that happens (that's the whole point of this testing!)
Logging Metadata
----------------

Each log contains the following information:

- UID*
- utc_sent*
- subsystem
- level
- author (optional)
- SEMID (optional)
- PROGID (optional)
- message

\* set automatically

Level
~~~~~
This denotes the severity level of the log. Think "debug, info, warn, error" in
standard log parlance. The only difference here is that we as DDOI admins are
able to add logging levels dynamically. For example, if we decided that a new
subsystem required a "superduperimportant" level, we can add it to the logging 
DB, and all logging objects will be created with a "superduperimportant()" 
logging function automatically.

Subsystem
~~~~~~~~~
This is the subsystem that this log came from. The subsystem must match an entry
in the subsystems database (this ensures that all logs from the same subsystem
share exactly the same tag.

Author
~~~~~~
This is a more fluid field than subsystem. It is intended to be used to specify
exactly where this log came from within a subsystem. For example, if a logger is
istantiated by a translator module, the author field could be the name of that
module. 

SEMID/PROGID
~~~~~~~~~~~~
These are pretty obvious. There isn't always a logical SEMID or PROGID to
associate with a message (e.g. an automatic process that turns on the KPF solar
calibrator wouldn't have a progid)

Message
~~~~~~~
This also pretty self-explanitory. This is the actual message that you want to
log.

Using the Logger
----------------

When you create a logger, you have the opportunity to set the authorship fields
above (`subsystem`, `author`, `SEMID`, `PROGID`). If you do this, you don't need
to specify this information each time you invoke a logging call.

.. code-block:: python
 
 #import the logger
 from ddoiloggerclient import DDOILogger

 # Create a logging instance. There are several arguments that can be set.
 logger = DDOILogger.DDOILogger(subsystem="NIRES", author="__name__", SEMID="U256")

Submitting a log is then a simple method invocation:

.. code-block:: python

 logger.debug("a debug message")
 logger.info("a logging message", system="nires", author="Luke Skywalker")
 logger.warn("a warning message")
 logger.error("an error message")


At the moment, NIRES is the only subsystem availible. There is an API that
exists only for DDOI admins that allows the adding of subsystems (and logging 
levels):

- /api/meta/add_subsystem: POST expects {"name" : NAME, "identifier" : ID (e.g. NIRES)}
- /api/meta/add_level: POST expects {"level" : LEVEL (e.g. "warn")}

Adding another subsystem or level is currently not a protected action, but it
will be when we deploy this system. To see the systems and levels available, use
GET /api/meta/valid_[levels,subsystems]

GET /api/log/get_logs returns all submitted logs. I will be adding a more
developed API for querying these once we get further along in the process, for
now the only option is to get a dump of all of them.