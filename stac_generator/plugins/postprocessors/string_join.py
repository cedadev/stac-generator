__author__ = "Richard Smith"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import logging

# Python imports
from typing import Optional

# Package imports
from stac_generator.core.processor import BasePostProcessor

LOGGER = logging.getLogger(__name__)


class StringJoinPostProcessor(BasePostProcessor):
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

        post_processors:
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

    def run(
        self,
        uri: str,
        source_dict: Optional[dict] = {},
        **kwargs,
    ):
        if source_dict:

            try:

                if self.destructive:
                    string_elements = [
                        str(source_dict.pop(key)) for key in self.key_list
                    ]
                else:
                    string_elements = [
                        str(source_dict.get(key)) for key in self.key_list
                    ]

                source_dict[self.key] = self.delimiter.join(string_elements)

            except KeyError:
                LOGGER.warning(f"Unable merge strings. file: {uri}", exc_info=True)

        return source_dict

    def expected_terms(
        self,
        term_list: Optional[list] = [],
    ) -> list:
        """
        The expected terms to be returned from running the extraction method with the given Collection Description
        :param collection_descrition: CollectionDescription for extraction method
        :param kwargs: free kwargs passed to the processor.
        :return: list
        """

        return term_list.append(self.key)
