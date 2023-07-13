__author__ = "Richard Smith"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import logging

# Package imports
from stac_generator.core.processor import BaseExtractionMethod

LOGGER = logging.getLogger(__name__)


class StringJoinExtract(BaseExtractionMethod):
    """

    Processor Name: ``string_join``

    Description:
        Accepts a dictionary. String values are popped from the dictionary and
        are put back into the dictionary with the ``key`` specified.

    Configuration Options:
        - ``key_list``: ``REQUIRED`` list of keys to convert to bbox array. Ordering is respected.
        - ``delimiter``: ``REQUIRED`` text delimiter to put between strings
        - ``key``: ``REQUIRED`` name of the key you would like to output
        - ``destructive``: Optional boolean false to retain original terms. ``DEFAULT``: True

    Example Configuration:


    .. code-block:: yaml

        - method: string_join
          inputs:
          key_list:
            - year
            - month
            - day
          delimiter: "-"
          key: datetime

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, "destructive"):
            self.destructive = True

    def run(self, uri: str, body: dict, **kwargs):
        try:

            if self.destructive:
                string_elements = [str(body.pop(key)) for key in self.key_list]
            else:
                string_elements = [str(body.get(key)) for key in self.key_list]

            body[self.key] = self.delimiter.join(string_elements)

        except KeyError:
            LOGGER.warning(f"Unable merge strings. file: {uri}", exc_info=True)

        return body
