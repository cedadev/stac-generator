# encoding: utf-8
"""
Kafka
-----

An output backend which outputs the generated metadata to a kafka event stream.

**Plugin name:** ``kafka``

.. list-table::
    :header-rows: 1

    * - Option
      - Value Type
      - Description
    * - ``config``
      - ``dict``
      - ``REQUIRED`` Configuration for the `Kafka producer <https://docs.confluent.io/kafka-clients/python/current/overview.html>`_
    * - ``topic``
      - ``str``
      - ``REQUIRED`` The topic to post the message to.
    * - ``key_term``
      - ``str``
      - Term to be used as the kafka messages key.

Example configuration:
    .. code-block:: yaml

        outputs:
            - method: kafka
              config:
                'bootstrap.servers': 'host1:9092,host2:9092'
              topic: stac
              key_term: item_id
"""
__author__ = "Richard Smith"
__date__ = "01 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import json

from confluent_kafka import Producer

from stac_generator.core.output import BaseOutput


class KafkaOutput(BaseOutput):
    """
    Simple print backend which can be used
    for testing and debugging.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Create the credentials object
        if not hasattr(self, "input_term"):
            self.key_term = "uri"
        self.producer = Producer(self.config)

    def delivery_callback(err, msg):
        if err:
            print("ERROR: Message failed delivery: {}".format(err))
        else:
            print(
                "Produced event to topic {topic}: key = {key:12} value = {value:12}".format(
                    topic=msg.topic(),
                    key=msg.key().decode("utf-8"),
                    value=msg.value().decode("utf-8"),
                )
            )

    def export(self, data: dict, **kwargs) -> None:
        """
        Post the message to the kafka server.

        :param data: Data from extraction processes
        :param kwargs: Not used
        """
        key = data.get(self.key_term, None)
        message = json.dumps(data).encode("utf8")
        self.producer.produce(self.topic, key=key, value=message)

        self.producer.flush()
