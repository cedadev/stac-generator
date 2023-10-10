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
from collections import defaultdict
import json
import logging
from typing import Optional

from stac_generator.core.extraction_method import BaseExtractionMethod
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
                dirpath: /path/to/file.json
                terms:
                  - mip_era

    """

    def get_facet_values(self) -> list:
        output = defaultdict(list)

        for filepath in os.listdir(self.dirpath):

            with open(filepath, "r") as file:
                item = json.load(file)

                item_properties = item["body"]["properties"]

                for facet in self.terms:
                    if facet in item_properties:
                        output[facet].extend(item_properties[facet])

        return output

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

    def run(self, body: dict, **kwargs) -> dict:
        output = self.get_facet_values()

        if values:
            body |= output

        # No need to include extents since the example scanner has none.

        return body
