# encoding: utf-8
"""
RabbitMQ Input
-----------------

Uses a `RabbitMQ Queue <https://www.rabbitmq.com/>`_ as a source for file objects.

**Plugin name:** ``rabbitmq``

.. list-table::
    :header-rows: 1

    * - Option
      - Value Type
      - Description
    * - ``connection``
      - ``dict``
      - ``REQUIRED`` The URI of a path or URL to an ESM collection JSON file.
    * - ``object_path_attr``
      - ``string``
      - ``REQUIRED`` The column header which contains the URI to the file object.
    * - ``catalog_kwargs``
      - ``dict``
      - Optional kwargs to pass to `intake.open_esm_datastore <https://intake-esm.readthedocs.io/en/latest/api.html#intake_esm.core.esm_datastore>`_
    * - ``search_kwargs``
      - ``dict``
      - Optional kwargs to pass to `esm_datastore.search <https://intake-esm.readthedocs.io/en/latest/api.html#intake_esm.core.esm_datastore.search>`_

Example Configuration:
    .. code-block:: yaml

        inputs:
            - name: rabbitmq
              connection:
                host: my-rabbit-server.co.uk
                user: user
                password: *********
                vhost: my_virtual_host
                kwargs: 
                    heartbeat: 300
              exchange:
                source_exchange: 
                    name: mysource-exchange
                    type: fanout
                destination_exchange: 
                    name: mysource-exchange
                    type: fanout
                prefetch_count: 1
              queues:
                - name:
                  kwargs:
                  bind_kwargs:


"""
__author__ = 'Richard Smith'
__date__ = '29 Sep 2021'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from .base import BaseInputPlugin

# Third-party imports
import pika

# Python imports
import functools
import logging

LOGGER = logging.getLogger(__name__)


class RabbitMQInputPlugin(BaseInputPlugin):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connection_conf = kwargs.get('connection', {})
        self.exchange_conf = kwargs.get('exchange', {})
        self.queues_conf = kwargs.get('queues', [])

    def _connect(self) -> pika.channel.Channel:
        """
        Start Pika connection to server. This is run in each thread.

        :return: pika channel
        """

        # Get the username and password for rabbit
        rabbit_user = self.connection_conf.get('user')
        rabbit_password = self.connection_conf.get('password')

        # Get the server variables
        rabbit_server = self.connection_conf.get('host')
        rabbit_vhost = self.connection_conf.get('vhost')

        # Create the credentials object
        credentials = pika.PlainCredentials(rabbit_user, rabbit_password)

        # Start the rabbitMQ connection
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=rabbit_server,
                credentials=credentials,
                virtual_host=rabbit_vhost,
                **self.connection_conf.get('kwargs', {})
            )
        )

        # Get the exchanges to bind
        src_exchange = self.exchange_conf.get('source_exchange')
        dest_exchange = self.exchange_conf.get('destination_exchange')

        # Create a new channel
        channel = connection.channel()
        channel.basic_qos(self.exchange_conf.get('prefetch_count', 1))

        # Declare relevant exchanges
        channel.exchange_declare(exchange=src_exchange['name'], exchange_type=src_exchange['type'])
        channel.exchange_declare(exchange=dest_exchange['name'], exchange_type=dest_exchange['type'])

        # Bind source exchange to dest exchange
        channel.exchange_bind(destination=dest_exchange['name'], source=src_exchange['name'])

        # Declare queue and bind queue to the dest exchange
        queues = self.queues_conf.get('queues')
        for queue in queues:
            declare_kwargs = queue.get('kwargs', {})
            bind_kwargs = queue.get('bind_kwargs', {})

            channel.queue_declare(queue=queue['name'], **declare_kwargs)
            channel.queue_bind(exchange=dest_exchange['name'], queue=queue['name'], **bind_kwargs)

            # Set callback
            callback = functools.partial(self.callback, connection=connection)
            channel.basic_consume(queue=queue['name'], on_message_callback=callback, auto_ack=False)

        return channel

    def should_process(self, filepath, source_media: StorageType) -> bool:
        """
        Should the path be sent for processing?

        Will run through any filter plugins. All plugins must pass for a True
        response. Any False will short circuit the logic and return False

        :param filepath: Filepath to test
        :param source_media: Source media

        :return: Bool, ``default: True``
        """
        if self.filters:
            return any((filter.run(filepath, source_media) for filter in self.filters))

        return True

    def callback(self,
                 ch: pika.channel.Channel,
                 method: pika.frame.Method,
                 properties: pika.frame.Header,
                 body: bytes,
                 connection: pika.connection.Connection) -> None:
        ...

    def run(self, extractor: BaseExtractor):
        
        while True:
            channel = self._connect()

            try:
                LOGGER.info('READY')
                channel.start_consuming()

            except KeyboardInterrupt:
                channel.stop_consuming()
                break

            except pika.exceptions.StreamLostError as e:
                # Log problem
                LOGGER.error('Connection lost, reconnecting', exc_info=e)
                continue

            except Exception as e:
                LOGGER.critical(e)

                channel.stop_consuming()
                break
