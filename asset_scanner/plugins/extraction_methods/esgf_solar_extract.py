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


import logging
import os

# Python imports
from functools import lru_cache

import requests

from asset_scanner.core.decorators import accepts_postprocessors, accepts_preprocessors
from asset_scanner.core.processor import BaseProcessor

# Package imports
from .mixins import PropertiesOutputKeyMixin

LOGGER = logging.getLogger(__name__)


class ESGFSolrExtract(PropertiesOutputKeyMixin, BaseProcessor):
    """
    Extracts metadata from files held in ESGF Solr.

    Configuration options:

    .. list-table::
        :header-rows: 1

        * - Option
          - Value Type
          - Description
        * - ```solr_kwargs```
          - ```dict```
          - Parameters to pass into the request URL to the Solr index
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        session_kwargs = getattr(self, "solr_kwargs")
        self.index = session_kwargs.get("index_node")
        self.core = session_kwargs.get("solr_core", "files")

    @staticmethod
    def format_item(solr_item):
        """
        Solr returns metadata as lists, convert the single item
        list to item.
        """
        if type(solr_item) == list and len(solr_item) == 1:
            return solr_item[0]
        return solr_item

    def get_metadata(self, path, index, core):
        """
        Send a request to Solr to get metadata from path id.
        """
        url = f"http://{index}/solr/{core}/select"
        search_params = {
            "indent": "on",
            "q": f"id:{path}",
            "wt": "json",
            "rows": 1,
            "sort": "id asc",
            "cursorMark": "*",
        }

        resp = requests.get(url, search_params).json()
        docs = resp["response"]["docs"][0]
        metadata = dict((k, self.format_item(v)) for k, v in docs.items())
        return metadata

    def extract_timestamp(self, metadata: dict):
        self.info["file_last_modified_timestamp"] = metadata.pop("timestamp")

    def extract_size(self, metadata: dict):
        self.info["size"] = metadata.pop("size")

    def extract_checksum(self, metadata: dict):
        self.info["checksum"] = metadata.pop("checksum")
        self.info["checksum_type"] = metadata.pop("checksum_type")

    def extract_filename(self, metadata: dict):
        filename = metadata.pop("title")
        self.info["filename"] = filename
        self.info["extension"] = os.path.splitext(filename)[1]

    def extract_properties(self, metadata: dict):
        file_id = metadata.pop("id")
        self.info["properties"] = metadata
        self.info["properties"]["file_id"] = file_id

    def extract_url(self, metadata: dict):
        urls = metadata.pop("url")
        self.info["location"] = urls
        hrefs = {method: url for (url, _, method) in [link.split("|") for link in urls]}

        self.info["href"] = hrefs.pop("HTTPServer")
        for method, url in hrefs.items():
            self.info[f"{method}_url"] = url

    def extract_ids(self, metadata: dict):
        self.info["master_id"] = metadata.pop("master_id")
        self.info["instance_id"] = metadata.pop("instance_id")
        self.info["tracking_id"] = metadata.pop("tracking_id")

    @staticmethod
    def remove_fields(metadata: dict):
        """
        Remove metadata that are not mapped to STAC
        """
        keys = ["type", "version", "_timestamp", "score", "_version_"]
        for key in keys:
            try:
                metadata.pop(key)
            except KeyError:
                pass

    @lru_cache(maxsize=3)
    def get_item_metadata(self, dataset_id) -> dict:
        """
        Get additional metadata exclusive to the dataset level of the file.
        """
        metadata = self.get_metadata(dataset_id, self.index, "datasets")
        return metadata

    def get_item_info(self):
        dataset_id = self.info["properties"]["dataset_id"]
        item_metadata = self.get_item_metadata(dataset_id)

        dataset_exclusive_keys = [
            "access",
            "height_units",
            "height_top",
            "height_bottom",
            "instance_id",
            "master_id",
            "url",
        ]

        for key in dataset_exclusive_keys:
            try:
                self.info["properties"][key] = item_metadata[key]
            except KeyError:
                pass

        # If there is geometry data, extract and reformat into bbox
        try:
            bbox = dict(
                min_lat=item_metadata["south_degrees"],
                max_lon=item_metadata["west_degrees"],
                max_lat=item_metadata["north_degrees"],
                min_lon=item_metadata["east_degrees"],
            )
            self.info["properties"].update(bbox)
        except KeyError:
            pass

    @accepts_preprocessors
    @accepts_postprocessors
    def run(self, uri: str, **kwargs) -> dict:

        # Transform the path back to ID form
        uri = uri.replace("/", ".")

        LOGGER.info(f"Extracting metadata for: {uri}")

        metadata = self.get_metadata(uri, self.index, self.core)

        self.extract_url(metadata)
        self.extract_size(metadata)
        self.extract_filename(metadata)
        self.extract_checksum(metadata)
        self.extract_ids(metadata)

        self.remove_fields(metadata)
        self.extract_properties(metadata)

        self.get_item_info()

        return self.info
