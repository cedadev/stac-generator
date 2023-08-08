__author__ = "Richard Smith"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import logging

# Package imports
from stac_generator.core.extraction_method import BaseExtractionMethod

LOGGER = logging.getLogger(__name__)


class FacetMapExtract(BaseExtractionMethod):
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

        - method: facet_map
          inputs:
          term_map:
            time_coverage_start: start_time

    """

    def run(self, body: dict, **kwargs) -> dict:
        output = {}
        for k, v in body.items():
            new_key = self.term_map.get(k)
            if new_key:
                output[new_key] = v
            else:
                output[k] = v

        return output
