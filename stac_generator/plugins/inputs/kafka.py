"""
Text File
---------

Takes file or directory path, uses the dictionary
in the file(s) to pass into the extractor.

**Plugin name:** ``text_file``

.. list-table::
    :header-rows: 1

    * - Option
      - Value Type
      - Description
    * - ``filepath``
      - ``string``
      - ``REQUIRED`` the path to input file(s)

Example Configuration:
    .. code-block:: yaml

        inputs:
            - method: text_file
              filepath: input_file(s)_location

"""

import logging

from confluent_kafka import Consumer, KafkaError

from stac_generator.core.generator import BaseGenerator
from stac_generator.core.input import BaseInput

LOGGER = logging.getLogger(__name__)


class KafkaInput(BaseInput):
    """
    Use external file(s) as input to enter data to pass to
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
