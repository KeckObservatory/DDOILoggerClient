API
---

The ZeroMQ pattern used is an asynchronous Request-Reply pattern. 
Client sends request messages, and a response is sent back to 
the server. Should the server be down for any reason, the client 
will attempt to send messages and receives no response from the 
server, these messages can be cached and resent as soon as the 
server is restored. 

The server runs a cluster of workers, each running in background
thread, waiting to receive messages. ZeroMQ routes messages
to this cluster, and an idle worker is passed a message.
When a message is received, the worker checks the message's 
``msg_type`` value and processes the request based off of its contents.
I.E. If ``msg_type`` is ``heartbeat`` then a heartbeat 
response is sent. If it is ``request_metadata_options`` then
the server sends log level and subsystem arrays as a response.
If it is ``log`` the server adds the log to the database and
sends back a acknowledgment message, detailing if it was successful
or not. 

The server depends on the configuration file located at 
``./configs/server_cfg.yaml``.
Messages sent to the server are sent as serialized 
JSON objects with the following schema:

.. code-block:: python

    {
    "msg_type": enumerable "log" or "heartbeat" or "request_metadata_options",
    "body": dict or None
    }

in the case of msg_type: ``log``
The log body is a dict with the following schema 

.. code-block:: python

    {
    "id": str,
    "utc_sent": date str formatted as YYYY-MM-DD HH:MM:SS.ZZ,
    "subsystem": str,
    "level": str either "debug" or "info" or "warn", or "err",
    "author": str,
    "SEMID": str,
    "PROGID": str,
    "message": str,
    }

For msg_type: ``handle_metadata_options`` the body is a dict
with the following schema

.. code-block:: python

    {
    'subsystems': str[],
    'levels': str[] 
    }

In the case of msg_type: ``request_logs``, 
the body is a dict with the following schema

.. code-block:: python

    {
    "startDate": str | None,
    "endDate": str | None,
    "nLogs": int | None,
    "subsystem": str | None,
    "dateFormat": str | None           
    }

.. csv-table:: API Syntax 
   :file: _static/api_table.csv
   :widths: 1, 2, 2, 2 
   :header-rows: 1
   :class: longtable
   :delim: @

For each message the sever returns an acknowledgment message with the following schema:
``{resp: 200 || 400, log?: dict, msg: string || dict}`` 
Successful messages get a response of 200 and messages that fail for whatever reason return a 400.
Failed log messages also include the log dictionary. More information should be found in the message value.