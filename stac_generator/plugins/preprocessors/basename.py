# encoding: utf-8
__author__ = "Richard Smith"
__date__ = "11 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import logging
import os

# Package imports
from stac_generator.core.processor import BasePreProcessor

LOGGER = logging.getLogger(__name__)


class BasenamePreProcessor(BasePreProcessor):
    """

    Processor Name: ``basename``

    Description:
        Takes a file path and returns the filename using `os.path.basename`.

    Example Configuration:

    .. code-block:: yaml

          pre_processors:
            - method: basename

    """

    def run(self, uri: str, **kwargs):

        uri = os.path.basename(uri)

        LOGGER.info(f"Identified file name: {uri}")

        return uri, kwargs
