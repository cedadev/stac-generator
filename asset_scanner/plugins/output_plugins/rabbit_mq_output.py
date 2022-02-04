import json

from .base import OutputBackend

import pika
from typing import Dict


class RabbitMQOutBackend(OutputBackend):

    def __init__(self, **kwargs):
        super().__init__(self, **kwargs)
        self.connection_conf = kwargs.get("connection", {})
        self.exchange_conf = kwargs.get("exchange", {})
        self.queues_conf = kwargs.get("queues", {})

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
        src_exchange = self.exchange_conf.get("source_exchange")
        self.dest_exchange = self.exchange_conf.get("destination_exchange")

        # Create a new channel
        channel = connection.channel()
        channel.exchange_declare(
            exchange=self.dest_exchange["name"], exchange_type=self.dest_exchange["type"]
        )
        channel.exchange_declare(
            exchange=src_exchange["name"], exchange_type=src_exchange["type"]
        )
        self.channel = channel

    @staticmethod
    def build_header(header_kwargs: Dict):
        header = {}
        if header_kwargs.get('x-delay'):
            header['x-delay'] = header_kwargs['x-delay']
        return pika.BasicProperties(headers=header)

    def export(self, data: Dict, **kwargs):
        """
        Export the data to rabbit.

        :param data: expected data as header dict
        :param kwargs: optional delayed message kwarg
        """
        message_properties = self.build_header(header_kwargs=kwargs)

        msg = json.dumps(data)

        self.channel.basic_publish(
            exchange=self.dest_exchange["name"],
            routing_key=self.queues_conf.get('bind_kwargs', {}).get('routing_key', ''),
            body=msg,
            properties=message_properties
        )
