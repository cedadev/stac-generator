# encoding: utf-8
__author__ = "Richard Smith"
__date__ = "29 Sep 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

# Python imports
import ast
import functools
import json
import logging
from typing import Callable

# Third-party imports
import pika
from extraction_methods.core.types import KeyOutputKey
from pydantic import BaseModel, Field

from stac_generator.core.input import BlockingInput

LOGGER = logging.getLogger(__name__)


class RabbitMQConnection(BaseModel):
    """RabbitMQ Connection model."""

    user: str = Field(
        description="RabbitMQ user.",
    )
    password: str = Field(
        description="RabbitMQ password.",
    )
    host: str = Field(
        description="RabbitMQ host.",
    )
    vhost: str = Field(
        description="RabbitMQ vhost.",
    )
    kwargs: dict = Field(
        default={},
        description="RabbitMQ additional kwargs.",
    )


class RabbitMQExchange(BaseModel):
    """RabbitMQ Exchange model."""

    name: str = Field(
        description="RabbitMQ exchange name.",
    )
    type: str = Field(
        default="topic",
        description="RabbitMQ exchange type.",
    )
    kwargs: dict = Field(
        default={},
        description="RabbitMQ exchange kwargs.",
    )


class RabbitMQQueue(BaseModel):
    """RabbitMQ Queue model."""

    name: str = Field(
        description="RabbitMQ queue name.",
    )
    declare_kwargs: dict = Field(
        default={},
        description="RabbitMQ declare kwargs.",
    )
    bind_kwargs: dict = Field(
        default={},
        description="RabbitMQ bind kwargs.",
    )
    consume_kwargs: dict = Field(
        default={},
        description="RabbitMQ consume kwargs.",
    )


class RabbitMQConf(BaseModel):
    """RabbitMQ config model."""

    connection: RabbitMQConnection = Field(
        description="RabbitMQ connection kwargs.",
    )
    exchange: RabbitMQExchange = Field(
        description="RabbitMQ exchange info.",
    )
    queues: list[RabbitMQQueue] = Field(
        default=[],
        description="RabbitMQ queues to bind.",
    )
    uri_term: str = Field(description="Attritube to use as uri.", default="uri")
    extra_terms: list[KeyOutputKey] = Field(
        default=[],
        description="List of extra attributes.",
    )


class RabbitMQInput(BlockingInput):
    """
    Uses a `RabbitMQ Queue <https://www.rabbitmq.com/>`_ as a source for events.

    **Plugin name:** ``rabbitmq``

    Example Configuration:
        .. code-block:: yaml

            name: rabbitmq
            conf:
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
                - kwargs:
                    durable: true
                  bind_kwargs:
                    routing_key: my.routing.key
                  consume_kwargs:
                    auto_ack: false

    """

    config_class = RabbitMQConf

    @staticmethod
    def decode_message(body: bytes) -> dict:
        """
        Takes the message and turns into a dictionary.
        String message format when split on :
            date_hour = split_line[0]
            min = split_line[1]
            sec = split_line[2]
            path = split_line[3]
            action = split_line[4]
            filesize = split_line[5]
            message = ":".join(split_line[6:])

        :param body: Message body, either a json string or text

        """

        # Decode the byte string to utf-8
        body = body.decode("utf-8")

        LOGGER.info("RabbitMQ message recieved: %s", body)

        try:
            msg = json.loads(body)

        except json.JSONDecodeError:
            try:
                msg = ast.literal_eval(body)

            except (ValueError, SyntaxError):
                # Assume the message is in the old format and split on :
                split_line = body.strip().split(":")

                msg = {
                    "datetime": ":".join(split_line[:3]),
                    "uri": split_line[3],
                    "action": split_line[4],
                    "filesize": split_line[5],
                    "message": ":".join(split_line[6:]),
                }

        if "uri" not in msg:
            msg["uri"] = msg["filepath"]

        return msg

    def _connect(self) -> pika.channel.Channel:
        """
        Start Pika connection to server. This is run in each thread.

        :return: pika channel
        """

        # Create the credentials object
        credentials = pika.PlainCredentials(
            self.conf.connection.user, self.conf.connection.password
        )

        # Start the rabbitMQ connection
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.conf.connection.host,
                credentials=credentials,
                virtual_host=self.conf.connection.vhost,
                **self.conf.connection.kwargs,
            )
        )

        # Create a new channel
        channel = connection.channel()

        channel.exchange_declare(
            exchange=self.conf.exchange.name,
            exchange_type=self.conf.exchange.type,
            **self.conf.exchange.kwargs,
        )
        channel.basic_qos(prefetch_count=1)

        # Declare queue and bind queue to the dest exchange
        for queue in self.conf.queues:
            channel.queue_declare(queue=queue.name, **queue.declare_kwargs)

            channel.queue_bind(
                exchange=self.conf.exchange.name, queue=queue.name, **queue.bind_kwargs
            )

            # Set callback
            callback = functools.partial(self.callback, connection=connection)
            channel.basic_consume(
                queue=queue.name, on_message_callback=callback, **queue.consume_kwargs
            )

        return channel

    @staticmethod
    def _acknowledge_message(channel: pika.channel.Channel, delivery_tag: str):
        """
        Acknowledge message

        :param channel: Channel which message came from
        :param delivery_tag: Message id
        """

        LOGGER.debug("Acknowledging message: %s", delivery_tag)
        if channel.is_open:
            channel.basic_ack(delivery_tag)

    def acknowledge_message(
        self,
        channel: pika.channel.Channel,
        delivery_tag: str,
        connection: pika.connection.Connection,
    ):
        """
        Acknowledge message and move onto the next. All of the required
        params come from the message callback params.

        :param channel: callback channel param
        :param delivery_tag: from the callback method param. eg. method.delivery_tag
        :param connection: connection object from the callback param
        """
        cb = functools.partial(self._acknowledge_message, channel, delivery_tag)
        connection.add_callback_threadsafe(cb)

    def callback(
        self,
        ch: pika.channel.Channel,
        method: pika.frame.Method,
        properties: pika.frame.Header,
        body: bytes,
        connection: pika.connection.Connection,
    ) -> None:

        # Get message
        try:
            message = self.decode_message(body)

        except IndexError:
            # Acknowledge message if the message is not compliant
            LOGGER.error("Unable to decode input message: %s", body)
            self.acknowledge_message(ch, method.delivery_tag, connection)
            return

        # Extract uri
        output = {"uri": message[self.conf.uri_term]}

        for extra_term in self.conf.extra_terms:
            output[extra_term.output_key] = message[extra_term.key]

        LOGGER.info("Input processing: %s message: %s", message[self.conf.uri_term], message)

        self.process_method(output)
        self.acknowledge_message(ch, method.delivery_tag, connection)

    def run(self, process_method: Callable):

        self.process_method = process_method

        while True:
            channel = self._connect()

            try:
                LOGGER.info("READY")
                channel.start_consuming()

            except KeyboardInterrupt:
                channel.stop_consuming()
                break

            except pika.exceptions.StreamLostError as e:
                # Log problem
                LOGGER.error("Connection lost, reconnecting", exc_info=e)
                continue

            except Exception as e:
                LOGGER.critical(e, exc_info=True)

                channel.stop_consuming()
                break
