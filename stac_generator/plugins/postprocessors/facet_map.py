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


class FacetMapPostProcessor(BasePostProcessor):
    """

    Processor Name: ``facet_map``

    Description:
        In some cases, you may wish to map the header attributes to different
        facets. This method takes a map and converts the facet labels into those
        specified.

    Configuration Options:
        - ``term_map``: Dictionary of terms to map

    Example Configuration:

    .. code-block:: yaml

        post_processors:
            - method: facet_map
              inputs:
                term_map:
                    time_coverage_start: start_time

    """

    def run(
        self,
        uri: str,
        source_dict: Optional[dict] = {},
        **kwargs,
    ) -> dict:
        output = {}
        if source_dict:

            for k, v in source_dict.items():

                new_key = self.term_map.get(k)
                if new_key:
                    output[new_key] = v
                else:
                    output[k] = v

        return output

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

        return [self.term_map.get(item, item) for item in term_list]
