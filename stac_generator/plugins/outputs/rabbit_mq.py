import json

import pika
from pydantic import BaseModel, Field

from stac_generator.core.output import Output


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
    vhost: str = Field(
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


class RabbitMQConf(BaseModel):
    """RabbitMQ config model."""

    connection: RabbitMQConnection = Field(
        description="RabbitMQ connection kwargs.",
    )
    exchange: RabbitMQExchange = Field(
        description="RabbitMQ exchange info.",
    )


class RabbitMQOutput(Output):
    """
    Output to a `RabbitMQ Queue <https://www.rabbitmq.com/>`_.

    **Plugin name:** ``rabbitmq_out``

    Example Configuration:
        .. code-block:: yaml

            - name: rabbitmq
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

    def export(self, data: dict, **kwargs) -> None:
        """
        Export the data to rabbit.

        :param data: expected data as header dict
        """

        message = {
            f"{data['surtype'].value}_id": data[f"{data['surtype'].value}_id"],
            "uri": data["uri"],
        }

        self.channel.basic_publish(
            exchange=self.conf.exchange.name,
            body=json.dumps(message),
            routing_key=self.conf.exchange.routing_key,
        )
