# encoding: utf-8
import json

import pika
from pydantic import BaseModel, Field

from stac_generator.core.bulk_output import BulkOutput, BulkOutputConf


class RabbitMQConnection(BaseModel):
    """JSON config model."""

    user: str = Field(
        description="RabbitMQ user.",
    )
    password: str = Field(
        description="RabbitMQ password.",
    )
    host: str = Field(
        description="RabbitMQ host.",
    )
    host: str = Field(
        description="RabbitMQ vhost.",
    )
    kwargs: dict = Field(
        default={},
        description="RabbitMQ additional kwargs.",
    )


class RabbitMQExchange(BaseModel):
    """JSON config model."""

    name: str = Field(
        description="RabbitMQ exchange name.",
    )
    type: str = Field(
        description="RabbitMQ exchange type.",
    )
    routing_key: str = Field(
        default="",
        description="RabbitMQ exchange routing key.",
    )


class RabbitMQConf(BulkOutputConf):
    """RabbitMQ config model."""

    connection: RabbitMQConnection = Field(
        default={},
        description="RabbitMQ connection kwargs.",
    )
    exchange: RabbitMQExchange = Field(
        description="RabbitMQ exchange info.",
    )


class RabbitMQBulkOutput(BulkOutput):
    """
    Uses a `RabbitMQ Queue <https://www.rabbitmq.com/>`_ as a destination for parent
    generation messages.

    **Plugin name:** ``rabbitmq_out_bulk``

    Example Configuration:
        .. code-block:: yaml

            - name: rabbitmq_bulk
              conf:
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

    config_class = RabbitMQConf

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Create the credentials object
        credentials = pika.PlainCredentials(
            self.conf.connection.user, self.conf.connection.password
        )

        # Start the rabbitMQ connection
        rabbit_connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.conf.connection.host,
                credentials=credentials,
                virtual_host=self.conf.connection.vhost,
                **self.conf.connection.kwargs,
            )
        )

        # Create a new channel
        self.channel = rabbit_connection.channel()
        self.channel.exchange_declare(
            exchange=self.conf.exchange.name,
            exchange_type=self.conf.exchange.type,
        )

    def data_to_cache(self, data: dict) -> None:
        """
        Convert the data into a data to  be stored in cache.

        :param data: data from processor to be output.
        :param kwargs:
        """
        return {
            data["body"][f"{data['surtype']}_id"]: {
                f"{data['surtype']}_id": data["body"][f"{data['surtype']}_id"],
                "uri": data["uri"],
            }
        }

    def export(self, data_list: list) -> None:
        """
        Export the data to rabbit.

        :param data: expected data as header dict
        """

        self.channel.basic_publish(
            exchange=self.conf.exchange.name,
            body=json.dumps(data_list),
            routing_key=self.conf.exchange.routing_key,
        )
