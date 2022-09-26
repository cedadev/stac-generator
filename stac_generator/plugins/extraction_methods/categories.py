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
import logging
import re

from stac_generator.core.decorators import (
    accepts_output_key,
    accepts_postprocessors,
    accepts_preprocessors,
    expected_terms_postprocessors,
)
from stac_generator.core.processor import BaseExtractionMethod

LOGGER = logging.getLogger(__name__)


class CategoriesExtract(BaseExtractionMethod):
    """

    .. list-table::

        * - Processor Name
          - ``catagories``
        * - Accepts Pre-processors
          - .. fa:: check
        * - Accepts Post-processors
          - .. fa:: check

    Description:
        Takes a list of catagory label and associated regex.

    Configuration Options:
        - ``catagories``: list of dictionaries containing label and regex
        - ``pre_processors``: List of pre-processors to apply
        - ``post_processors``: List of post_processors to apply
        - ``output_key``: When the metadata is returned, this key determines
          where the metadata is fit in the response. Dot separated
          strings can be used to created nested attributes. An empty string can
          be used to return the output with no prefix.
          ``default: 'properties'``


    Example configuration:
        .. code-block:: yaml

            - method: catagories
              inputs:
                catagories:
                  - label: metadata
                    regex: README
                  - label: hidden
                    regex: /\/.

    # noqa: W605
    """

    def get_category(self, uri, label, regex):
        """

        :param uri:
        :param label:
        :param regex:
        :return:

        """

        m = re.search(regex, uri)

        if not m:
            label = None

        return label

    @accepts_output_key
    @accepts_preprocessors
    @accepts_postprocessors
    def run(self, uri: str, **kwargs) -> dict:

        result = set()

        for category in self.categories:
            label = self.get_category(uri, **category)
            if label:
                result.add(label)

        return {"catagories": list(result) or ["data"]}

    @expected_terms_postprocessors
    def expected_terms(self, **kwargs) -> list:
        """
        The expected terms to be returned from running the extraction method with the given Collection Description
        :param collection_descrition: CollectionDescription for extraction method
        :param kwargs: free kwargs passed to the processor.
        :return: list
        """

        return list(self.defaults.keys())
