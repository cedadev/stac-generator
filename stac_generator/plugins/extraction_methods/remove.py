__author__ = "Richard Smith"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import logging

# Package imports
from stac_generator.core.extraction_method import BaseExtractionMethod

LOGGER = logging.getLogger(__name__)


class RemoveExtract(BaseExtractionMethod):
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

        - method: string_template
          template: {hello}/{goodbye}/{hello}/bonjour.html
          output_key: manifest_url

    """

    def run(self, body: dict, **kwargs):
        for key in self.keys:
            if key in body:
                del body[key]

        return body
