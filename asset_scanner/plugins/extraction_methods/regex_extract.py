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

from asset_scanner.core.decorators import accepts_postprocessors, accepts_preprocessors
from asset_scanner.core.processor import BaseProcessor

# Package imports
from .mixins import PropertiesOutputKeyMixin

LOGGER = logging.getLogger(__name__)


class RegexExtract(PropertiesOutputKeyMixin, BaseProcessor):
    """

    .. list-table::

        * - Processor Name
          - ``regex``
        * - Accepts Pre-processors
          - .. fa:: check
        * - Accepts Post-processors
          - .. fa:: check

    Description:
        Takes an input string and a regex with
        named capture groups and returns a dictionary of the values
        extracted using the named capture groups.

    Configuration Options:
        - ``regex``: The regular expression to match against the filepath
        - ``pre_processors``: List of pre-processors to apply
        - ``post_processors``: List of post_processors to apply
        - ``output_key``: When the metadata is returned, this key determines
          where the metadata is fit in the response. Dot separated
          strings can be used to created nested attributes. An empty string can
          be used to return the output with no prefix.
          ``default: 'properties'``


    Example configuration:
        .. code-block:: yaml

            - name: regex
              inputs:
                regex: '^(?:[^_]*_){2}(?P<datetime>\d*)'
              pre_processors:
                - name: filename_reducer
              post_processors:
                - name: isodate_processor
                  inputs:
                    date_key: datetime

    """

    @accepts_preprocessors
    @accepts_postprocessors
    def run(self, filepath: str, source_media: str = "POSIX", **kwargs) -> dict:

        m = re.match(self.regex, filepath)

        if m:
            LOGGER.info("Found matches for regex extract")
            return m.groupdict()

        LOGGER.debug("No matches found for regex extract")
        return {}
