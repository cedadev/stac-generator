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
import json
import logging
from typing import Optional

from stac_generator.core.decorators import (
    accepts_output_key,
    accepts_postprocessors,
    accepts_preprocessors,
    expected_terms_postprocessors,
)
from stac_generator.core.processor import BaseExtractionMethod
from stac_generator.core.types import SpatialExtent, TemporalExtent

LOGGER = logging.getLogger(__name__)


class JsonFileExtract(BaseExtractionMethod):
    """

    .. list-table::

        * - Processor Name
          - ``json``
        * - Accepts Pre-processors
          - .. fa:: check
        * - Accepts Post-processors
          - .. fa:: check

    Description:
        Takes an input list of string to extract from the json file.

    Configuration Options:
        - ``terms``: List of terms to extract
        - ``pre_processors``: List of pre-processors to apply
        - ``post_processors``: List of post_processors to apply
        - ``output_key``: When the metadata is returned, this key determines
          where the metadata is fit in the response. Dot separated
          strings can be used to created nested attributes. An empty string can
          be used to return the output with no prefix.
          ``default: 'properties'``


    Example configuration:
        .. code-block:: yaml

            - method: json
              inputs:
                filepath: /path/to/file.json
                terms:
                  - mip_era

    """

    def get_facet_values(self, facet: str, id: str) -> list:

        facet_values = []

        with open(self.filepath, "r") as file:
            file_data = json.load(file)

            for item in file_data:
                if item["body"][f"{self.TYPE.value}_id"] == id:
                    values = item["body"]["properties"][facet]

                    if isinstance(values, list):
                        facet_values.extend(values)

                    else:
                        facet_values.append(values)

        return list(set(facet_values))

    @staticmethod
    def get_spatial_extent(item_list: list) -> Optional[SpatialExtent]:
        ...

    @staticmethod
    def get_temporal_extent(item_list: list) -> Optional[TemporalExtent]:
        start_datetime = []
        end_datetime = []
        datetime = []

        for item in item_list:
            start_datetime.append(item["properties"].get("start_datetime"))
            end_datetime.append(item["properties"].get("end_datetime"))
            datetime.append(item["properties"].get("datetime"))

        start_datetime = list(set(start_datetime))
        end_datetime = list(set(end_datetime))
        datetime = list(set(datetime))

    def get_extent(self, file_id: str) -> dict:
        item_list = []
        with open(self.filepath, "r") as file:
            file_data = json.load(file)

            for item in file_data:
                if item["body"]["collection_id"] == file_id:
                    item_list.append(item)

        # spatial_extent = self.get_spatial_extent(item_list)
        # temporal_extent = self.get_temporal_extent(item_list)

    @accepts_output_key
    @accepts_preprocessors
    @accepts_postprocessors
    def run(self, uri: str, **kwargs) -> dict:

        metadata = {}

        for facet in self.terms:
            values = self.get_facet_values(
                facet, getattr(self, f"{self.TYPE.value}_id")
            )
            if values:
                metadata[facet] = values

        # No need to include extents since the example scanner has none.

        return metadata

    @expected_terms_postprocessors
    def expected_terms(self, **kwargs) -> list:
        """
        The expected terms to be returned from running the extraction method with the given Collection Description
        :param collection_descrition: CollectionDescription for extraction method
        :param kwargs: free kwargs passed to the processor.
        :return: list
        """

        return self.terms
