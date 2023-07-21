__author__ = "Richard Smith"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import logging

# Package imports
from stac_generator.core.processor import BaseExtractionMethod

LOGGER = logging.getLogger(__name__)


class FacetPrefixExtract(BaseExtractionMethod):
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

        - method: facet_prefix
          inputs:
          prefix:
            cmip6
          terms:
            - start_time
            - model

    """

    def run(self, body: dict, **kwargs) -> dict:
        output = {}
        if body:

            for k, v in body.items():
                if k in self.terms:
                    output[f"{self.prefix}:{k}"] = v
                else:
                    output[k] = v

        return output
