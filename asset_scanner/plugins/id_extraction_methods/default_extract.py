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

from asset_scanner.core.decorators import accepts_postprocessors, accepts_preprocessors
from asset_scanner.core.processor import BaseProcessor

LOGGER = logging.getLogger(__name__)


class DefaultExtract(BaseProcessor):
    """

    .. list-table::

        * - Processor Name
          - ``default``
        * - Accepts Pre-processors
          - .. fa:: check
        * - Accepts Post-processors
          - .. fa:: check

    Description:
        Extracts default id.

    Configuration Options:
        - ``value``: id value
        - ``pre_processors``: List of pre-processors to apply
        - ``post_processors``: List of post_processors to apply

    Example configuration:
        .. code-block:: yaml

          id:
            method: default
            inputs:
              value: cmip6

    """

    @accepts_preprocessors
    @accepts_postprocessors
    def run(
        self,
        body: dict,
        **kwargs,
    ) -> dict:

        return self.value
