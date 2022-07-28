"""
RabbitMQ Output
-----------------

Uses a `RabbitMQ Queue <https://www.rabbitmq.com/>`_ as a destination for parent
generation messages.

**Plugin name:** ``rabbitmq_out_bulk``

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
      - dictionary describing the source exchange. `exchange`_
    * - ``exchange.dest_exchange``
      - dict
      - ``REQUIRED`` The final exchange. This is where the queues will be bound. `exchange`_
    * - ``queues``
      - ``list``
      - ``REQUIRED`` Queue parameters. `queues`_
    * - ``max_cache_size``
      - ``int``
      - Maximum number of messages before cache is emptied.


exchange
^^^^^^^^

The source and dest exchange keys comprise:

.. list-table::
    :header-rows: 1

    * - Option
      - Value Type
      - Description
    * - method
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
    * - method
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

Example Configuration:

    .. code-block:: yaml

        outputs:
            - method: rabbitmq_bulk
              connection:
                host: my-rabbit-server.co.uk
                user: user
                password: '*********'
                vhost: my_virtual_host
                kwargs:
                  heartbeat: 300
              exchange:
                name: mydest-exchange
                type: fanout
                routing_key: asset
              cache_max_size: 10
"""

import json

import pika
from cachetools import Cache

from stac_generator.core.output import BaseBulkOutput


class RabbitMQBulkOutput(BaseBulkOutput):
    """
    RabbitMQ Bulk output for sending grouped messages.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Add 1
        self.message_cache = Cache(maxsize=getattr(self, "cache_max_size", 100) + 1)

        # Create the credentials object
        credentials = pika.PlainCredentials(
            self.connection["user"], self.connection["password"]
        )

        # Start the rabbitMQ connection
        rabbit_connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.connection["host"],
                credentials=credentials,
                virtual_host=self.connection["vhost"],
                **self.connection.get("kwargs", {}),
            )
        )

        # Create a new channel
        self.channel = rabbit_connection.channel()
        self.channel.exchange_declare(
            exchange=self.exchange["name"],
            exchange_type=self.exchange["type"],
        )

    def clear_cache(self, **kwargs):
        """
        Export the data to rabbit.

        :param data: expected data as header dict
        """
        self.channel.basic_publish(
            exchange=self.exchange["name"],
            body=json.dumps(dict(self.message_cache.items())),
            routing_key=self.exchange.get("routing_key", ""),
        )

        self.message_cache.clear()

    def export(self, data: dict, **kwargs):
        """
        Export the data to rabbit.

        :param data: expected data as header dict
        """
        id = data["id"]

        # add to cache
        self.message_cache.update({id: kwargs["message"]})

        if self.message_cache.currsize >= getattr(self, "cache_max_size", 100):
            # empty cache
            self.clear_cache()
