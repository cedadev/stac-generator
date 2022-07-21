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


class FacetPrefixPostProcessor(BasePostProcessor):
    """

    Processor Name: ``facet_prefix``

    Description:
        In some cases, you may wish add a prefix to some or all of the facets
        based on the vocabulary they're from.

    Configuration Options:
        - ``prefix``: Prefix to be added
        - ``terms``: List of terms that require prefix

    Example Configuration:

    .. code-block:: yaml

        post_processors:
            - method: facet_prefix
              inputs:
                prefix:
                  cmip6
                terms:
                    - start_time
                    - model

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
                if k in self.terms:
                    output[f"{self.prefix}:{k}"] = v
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

        return [
            f"{self.prefix}.{item}" if item in self.terms else item
            for item in term_list
        ]
