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

from stac_generator.core.decorators import (
    accepts_output_key,
    accepts_postprocessors,
    accepts_preprocessors,
    expected_terms_postprocessors,
)
from stac_generator.core.processor import BaseExtractionMethod

LOGGER = logging.getLogger(__name__)


class PathPartsExtract(BaseExtractionMethod):
    """

    .. list-table::

        * - Processor Name
          - ``path_parts``
        * - Accepts Pre-processors
          - .. fa:: check
        * - Accepts Post-processors
          - .. fa:: check

    Description:
        Extracts the parts of a given path skipping ``skip`` number
        of top level parts.

    Configuration Options:
        - ``skip``: The number of path parts to skip
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
                skip: 2

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, "skip"):
            self.skip = 0

    @accepts_output_key
    @accepts_preprocessors
    @accepts_postprocessors
    def run(self, uri: str, **kwargs) -> list:
        path = Path(uri)

        parts = list(path.parts)[self.skip :]

        output = {"filename": parts.pop()}

        dir_level = 1
        for part in parts:
            output[f"_dir{dir_level}"] = part
            dir_level += 1

        return output

    @expected_terms_postprocessors
    def expected_terms(self, **kwargs) -> list:
        """
        The expected terms to be returned from running the extraction method with the given Collection Description
        :param collection_descrition: CollectionDescription for extraction method
        :param kwargs: free kwargs passed to the processor.
        :return: list
        """

        return "list of path parts"
