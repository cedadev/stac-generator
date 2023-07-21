# encoding: utf-8
"""
..  _regex:

Regex
------
"""
__author__ = "Richard Smith"
__date__ = "27 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


# Python imports
import hashlib
import logging

from stac_generator.core.processor import BaseExtractionMethod

LOGGER = logging.getLogger(__name__)


class HashExtract(BaseExtractionMethod):
    """

    .. list-table::

        * - Processor Name
          - ``hash``

    Description:
        Hashes input string.

    Configuration Options:
        - ``input_key``: Key for term to be hashed
        - ``output_key``: Key for result to be saved as

    Example configuration:
        .. code-block:: yaml

          id:
            method: hash
            inputs:
              input_key: model
              output_key: hashed_terms

    """

    def hash(self, input_str: str):
        return hashlib.md5(input_str.encode("utf-8")).hexdigest()

    def run(self, uri: str, body: dict, **kwargs) -> dict:

        str_to_hash = uri if self.input_key == "uri" else body[self.input_key]

        body[self.output_key] = self.hash(str_to_hash)

        return body
