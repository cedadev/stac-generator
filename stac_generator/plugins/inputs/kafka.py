# encoding: utf-8
"""
Kafka
-----

An input plufin which polls a kafka event stream.

**Plugin name:** ``kafka``

.. list-table::
    :header-rows: 1

    * - Option
      - Value Type
      - Description
    * - ``config``
      - ``dict``
      - ``REQUIRED`` Configuration for the `Kafka consumer <https://docs.confluent.io/kafka-clients/python/current/overview.html>`_
    * - ``topics``
      - ``list``
      - ``REQUIRED`` The topics to poll for messages.
    * - ``timeout``
      - ``str``
      - ``REQUIRED`` The time between polling the event stream.

Example configuration:
    .. code-block:: yaml

        outputs:
            - method: kafka
              config:
                'bootstrap.servers': 'host1:9092,host2:9092'
              topics:
                - stac
"""

import logging

from confluent_kafka import Consumer, KafkaError, KafkaException

from stac_generator.core.generator import BaseGenerator
from stac_generator.core.input import BaseInput

LOGGER = logging.getLogger(__name__)


class KafkaInput(BaseInput):
    """
    Use Kafka event stream as input to collect messages to pass to
    the processor.
    """

    def __init__(self, **kwargs):
        self.consumer = Consumer(self.conf)

    def run(self, generator: BaseGenerator):
        try:
            self.consumer.subscribe(self.topics)
            while True:
                msg = self.consumer.poll(timeout=self.timeout)
                if msg is None:
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition event
                        LOGGER.error(
                            "%% %s [%d] reached end at offset %d\n"
                            % (msg.topic(), msg.partition(), msg.offset())
                        )
                    elif msg.error():
                        raise KafkaException(msg.error())

                else:
                    data = msg
                    generator.process(**data)
        finally:
            # Close down consumer to commit final offsets.
            self.consumer.close()
