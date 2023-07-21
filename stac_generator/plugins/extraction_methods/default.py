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

from stac_generator.core.processor import BaseExtractionMethod

LOGGER = logging.getLogger(__name__)


class DefaultExtract(BaseExtractionMethod):
    """

    .. list-table::

        * - Processor Name
          - ``default``

    Description:
        Takes a set of default facets.

    Configuration Options:
        - ``defaults``: Dictionary of defaults to be added


    Example configuration:
        .. code-block:: yaml

            - method: default
              inputs:
                defaults:
                  mip_era: CMIP6

    """

    def run(self, body: dict, **kwargs) -> dict:

        body = body | self.defaults

        return body
