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
      - dictionary describing the source exchange. `exchange`_
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
            - method: rabbitmq
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
              deduplication:
                x_delay: 30000
              cache:
                max_size: 10
                max_age: 30
"""

import json

import pika
from cachetools import TTLCache

from .base import OutputBackend


class RabbitMQOutBackend(OutputBackend):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.id_cache = TTLCache(
            maxsize=self.cache.get("max_size", 10), ttl=self.cache.get("max_age", 30)
        )

        if not hasattr(self, "deduplication"):
            self.deduplication = False

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

    def build_properties(self, id):
        header = {}
        # Handle the deduplication of messages and add relevant headers
        if self.deduplication:
            header["x-delay"] = self.deduplication.get("x-delay", 30000)
            header["x-deduplication-header"] = id

        return pika.BasicProperties(headers=header)

    def export(self, data: dict, **kwargs):
        """
        Export the data to rabbit.

        :param data: expected data as header dict
        """
        id = data["id"]
        msg = json.dumps(self.message)

        if self.deduplication:
            # Check if id is in the cache
            if self.id_cache.get(id):
                self.deduplicate = True
            # add a dummy value to the cache of equal to True.
            self.id_cache.update({id: True})

        properties = self.build_properties(id)

        self.channel.basic_publish(
            exchange=self.exchange["name"],
            body=msg,
            routing_key=self.exchange.get("routing_key", ""),
            properties=properties,
        )
