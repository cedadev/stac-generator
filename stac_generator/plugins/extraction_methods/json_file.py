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

from stac_generator.core.processor import BaseExtractionMethod
from stac_generator.core.types import SpatialExtent, TemporalExtent

LOGGER = logging.getLogger(__name__)


class JsonFileExtract(BaseExtractionMethod):
    """

    .. list-table::

        * - Processor Name
          - ``json``

    Description:
        Takes an input list of string to extract from the json file.

    Configuration Options:
        - ``terms``: List of terms to extract


    Example configuration:
        .. code-block:: yaml

            - method: json
              inputs:
                filepath: /path/to/file.json
                terms:
                  - mip_era

    """

    def get_facet_values(self, facet: str, uri: str) -> list:

        facet_values = []

        with open(self.filepath, "r") as file:
            file_data = json.load(file)

            for item in file_data:
                if item["body"][f"{self.TYPE.value}_id"] == id:
                    values = []

                    if facet in item["body"]["properties"]:
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

    def run(self, uri: str, body: dict, **kwargs) -> dict:

        for facet in self.terms:
            values = self.get_facet_values(facet, uri)
            if values:
                body[facet] = values

        # No need to include extents since the example scanner has none.

        return body
