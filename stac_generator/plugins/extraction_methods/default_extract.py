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

from stac_generator.core.decorators import accepts_postprocessors, accepts_preprocessors
from stac_generator.core.processor import BaseProcessor

# Package imports
from .mixins import PropertiesOutputKeyMixin

LOGGER = logging.getLogger(__name__)


class DefaultExtract(PropertiesOutputKeyMixin, BaseProcessor):
    """

    .. list-table::

        * - Processor Name
          - ``default``
        * - Accepts Pre-processors
          - .. fa:: check
        * - Accepts Post-processors
          - .. fa:: check

    Description:
        Takes a set of default facets.

    Configuration Options:
        - ``defaults``: Dictionary of defaults to be added
        - ``pre_processors``: List of pre-processors to apply
        - ``post_processors``: List of post_processors to apply
        - ``output_key``: When the metadata is returned, this key determines
          where the metadata is fit in the response. Dot separated
          strings can be used to created nested attributes. An empty string can
          be used to return the output with no prefix.
          ``default: 'properties'``


    Example configuration:
        .. code-block:: yaml

            - method: default
              inputs:
                defaults:
                  mip_era: CMIP6

    """

    @accepts_preprocessors
    @accepts_postprocessors
    def run(self, uri: str, **kwargs) -> dict:

        return self.defaults
