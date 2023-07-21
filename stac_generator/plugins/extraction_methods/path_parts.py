# encoding: utf-8
"""
..  _path_parts:

Path Parts
------
"""
__author__ = "Richard Smith"
__date__ = "27 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


# Python imports
import logging
from pathlib import Path

from stac_generator.core.processor import BaseExtractionMethod

LOGGER = logging.getLogger(__name__)


class PathPartsExtract(BaseExtractionMethod):
    """

    .. list-table::

        * - Processor Name
          - ``path_parts``

    Description:
        Extracts the parts of a given path skipping ``skip`` number
        of top level parts.

    Configuration Options:
        - ``skip``: The number of path parts to skip. ``default: 1``


    Example configuration:
        .. code-block:: yaml

            - method: default
              inputs:
                skip: 2

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, "skip"):
            self.skip = 1

    def run(self, body: dict, **kwargs) -> list:
        path = Path(body["uri"])

        parts = list(path.parts)[self.skip :]

        body["filename"] = parts.pop()

        dir_level = 1
        for part in parts:
            body[f"_dir{dir_level}"] = part
            dir_level += 1

        return body
