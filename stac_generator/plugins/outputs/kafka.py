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

Example configuration:
    .. code-block:: yaml

        outputs:
            - method: kafka
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
        Print the received data.

        :param data: Data from extraction process
        :param kwargs: Not used
        """
        message = json.dumps(data).encode("utf8")
        self.producer.produce(self.topic, self.key, message, callback=self.delivery_callback)
