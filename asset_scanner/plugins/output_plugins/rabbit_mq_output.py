"""
RabbitMQ Output
-----------------

Uses a `RabbitMQ Queue <https://www.rabbitmq.com/>`_ as a destination for file objects.

**Plugin name:** ``rabbitmq_out``

.. list-table::
    :header-rows: 1

    * - Option
      - Value Type
      - Description
    * - ``connection.host``
      - string
      - ``REQUIRED`` RabbitMQ server host
    * - ``connection.user``
      - string
      - ``REQUIRED`` Username
    * - ``connection.password``
      - string
      - ``REQUIRED`` password
    * - ``connection.vhost``
      - string
      - ``REQUIRED`` `Virtual host <https://www.rabbitmq.com/vhosts.html>`_
    * - ``connection.kwargs``
      - dict
      - connection parameter kwargs `pika.conneciton.ConnectionParameters
        <https://pika.readthedocs.io/en/stable/modules/parameters.html#connectionparameters>`_
    * - ``exchange.source_exchange``
      - dict
      - Dictionary describing the source exchange. `exchange`_
    * - ``exchange.dest_exchange``
      - dict
      - ``REQUIRED`` The final exchange. This is where the queues will be bound. `exchange`_
    * - ``queues``
      - ``list``
      - ``REQUIRED`` Queue parameters. `queues`_


exchange
^^^^^^^^

The source and dest exchange keys comprise:

.. list-table::
    :header-rows: 1

    * - Option
      - Value Type
      - Description
    * - name
      - string
      - ``REQUIRED`` Exchange name
    * - type
      - string
      - ``REQUIRED`` `Exchange type <https://medium.com/trendyol-tech/rabbitmq-exchange-types-d7e1f51ec825>`_

queues
^^^^^^

List of queue objects. Each queue object comprises:

.. list-table::
    :header-rows: 1

    * - Option
      - Value Type
      - Description
    * - name
      - string
      - ``REQUIRED`` Queue name
    * - kwargs
      - dict
      - kwargs passed to `pika.channel.queue_declare <https://pika.readthedocs.io/en/stable/modules/channel.html#pika.channel.Channel.queue_declare>`_
    * - bind_kwargs
      - dict
      - kwargs passed to `pika.channel.queue_bind <https://pika.readthedocs.io/en/stable/modules/channel.html#pika.channel.Channel.queue_bind>`_
    * - consume_kwargs
      - dict
      - kwargs passed to `pika.channel.Channel.basic_consume <https://pika.readthedocs.io/en/stable/modules/channel.html#pika.channel.Channel.basic_consume>`_

header_conf
^^^^^^^^^^^

Configuration for the header options for rabbit.

.. list-table::
    :header-rows: 1

    * - Option
      - Value Type
      - Description
    * - x-delay
      - int
      - Message delay in milliseconds use in kwargs passed to `pika.spec.Basicproperties.headers <https://pika.readthedocs.io/en/stable/modules/spec.html?highlight=headers#pika.spec.BasicProperties>`_

Example Configuration:

    .. code-block:: yaml

        outputs:
            - name: rabbitmq
              connection:
                host: my-rabbit-server.co.uk
                user: user
                password: '*********'
                vhost: my_virtual_host
                kwargs:
                    heartbeat: 300
              exchange:
                source_exchange:
                    name: mysource-exchange
                    type: fanout
                destination_exchange:
                    name: mydest-exchange
                    type: fanout
              queues:
                - name:
                  kwargs:
                    durable: true
                  bind_kwargs:
                    routing_key: my.routing.key
                  consume_kwargs:
                    auto_ack: false
              header_conf:
                x_delay: 30000
"""

import json
from typing import Dict

import pika

from .base import OutputBackend


class RabbitMQOutBackend(OutputBackend):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.connection_conf = kwargs.get("connection", {})
        self.exchange_conf = kwargs.get("exchange", {})
        self.queues_conf = kwargs.get("queues", {})
        self.header_conf = kwargs.get("header_conf", {})

        # Get the username and password for rabbit
        rabbit_user = self.connection_conf.get("user")
        rabbit_password = self.connection_conf.get("password")

        # Get the server variables
        rabbit_server = self.connection_conf.get("host")
        rabbit_vhost = self.connection_conf.get("vhost")

        # Create the credentials object
        credentials = pika.PlainCredentials(rabbit_user, rabbit_password)

        # Start the rabbitMQ connection
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=rabbit_server,
                credentials=credentials,
                virtual_host=rabbit_vhost,
                **self.connection_conf.get("kwargs", {}),
            )
        )

        # Get the exchanges to bind
        self.src_exchange = self.exchange_conf.get("source_exchange")
        self.dest_exchange = self.exchange_conf.get("destination_exchange")

        # Create a new channel
        if self.dest_exchange:
            channel = connection.channel()
            channel.exchange_declare(
                exchange=self.dest_exchange["name"],
                exchange_type=self.dest_exchange["type"],
            )
        if self.src_exchange:
            channel.exchange_declare(
                exchange=self.src_exchange["name"],
                exchange_type=self.src_exchange["type"],
            )
        self.channel = channel

    def build_header(self, **kwargs):
        header = {}
        # Handle the deduplication of messages and add relevant headers
        if kwargs.get("deduplicate", False):
            header["x-delay"] = self.header_conf.get("x-delay", 30000)
            header["x-deduplication-header"] = kwargs.get("id")

        # Possbile dict merge header with header_conf here.
        return pika.BasicProperties(headers=header)

    def export(self, data: Dict, **kwargs):
        """
        Export the data to rabbit.

        :param data: expected data as header dict
        :param kwargs: optional delayed message kwarg
        """
        # Pass kwargs to handle the deduplication and header generation
        message_properties = self.build_header(**kwargs)

        msg = json.dumps(data)

        self.channel.basic_publish(
            exchange=self.dest_exchange["name"],
            body=msg,
            routing_key=self.exchange_conf.get("routing_key", ""),
            properties=message_properties,
        )
