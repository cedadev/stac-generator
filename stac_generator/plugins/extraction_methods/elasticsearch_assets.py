# encoding: utf-8
"""
..  _elasticsearch-extract:

Elasticsearch Extract
------------------
"""
__author__ = "Rhys Evans"
__date__ = "24 May 2022"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "rhys.r.evans@stfc.ac.uk"

import logging

# Third party imports
from elasticsearch import Elasticsearch
from datetime import datetime
from pathlib import Path

import magic

from stac_generator.core.extraction_method import BaseExtractionMethod

LOGGER = logging.getLogger(__name__)


class ElasticsearchAssetExtract(BaseExtractionMethod):
    """
    Description:
        Using an ID. Generate a summary of information for higher level entities.

    Configuration Options:
        - ``index``: Name of the index holding the STAC entities
        - ``id_term``: Term used for agregating the STAC entities
        - ``session_kwargs``: Session parameters passed to
        `elasticsearch.Elasticsearch<https://elasticsearch-py.readthedocs.io/en/7.10.0/api.html>`_
        - ``bbox``: list of terms for which their aggregate bbox should be returned.
        - ``min``: list of terms for which the minimum of their aggregate should be returned.
        - ``max``: list of terms for which the maximum of their aggregate should be returned.
        - ``sum``: list of terms for which the sum of their aggregate should be returned.
        - ``list``: list of terms for which a list of their aggregage should be returned.

    Configuration Example:

        .. code-block:: yaml

                name: elasticsearch
                inputs:
                    index: ceda-index
                    id_term: item_id
                    connection_kwargs:
                      hosts: ['host1:9200','host2:9200']
                    fields:
                      - roles
                      -
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if hasattr(self, "connection_kwargs"):
            self.es = Elasticsearch(**self.connection_kwargs)

        if not hasattr(self, "request_tiemout"):
            self.request_tiemout = 15

        if not hasattr(self, "fields"):
            self.fields = []

        self.field_keys = []

        for index, field in enumerate(self.fields):
            if "key" not in field:
                field["key"] = field["name"]

            self.field_keys.append(field["key"])
            self.fields[index] = field

    def hit_to_asset(self, hit: dict, asset: dict):
        """Convert elasticsearch hit to asset"""
        for term_key, term_value in hit.items():
            if term_key == "properties":
                asset = self.hit_to_asset(asset, term_value)

            else:
                asset[term_key] = term_value

        return asset

    def run(self, body: dict, **kwargs) -> dict:

        if not hasattr(self, "regex"):
            self.regex = body[self.regex_term]
        
        query = {
            "query": {
                "regexp": {
                    f"{self.search_field}.keyword": {
                        "value": self.regex,
                    }
                },
            },
            "_source": [self.search_field] + self.field_keys,
        }

        # Run query
        result = self.es.search(
            index=self.index, body=query, timeout=f"{self.request_tiemout}s"
        )

        assets = body.get("assets", {})

        for hit in result["hits"]["hits"]:
            source = hit["_source"]
            path = source["path"]
            asset = {
                "href": path,
            }

            for field in self.fields:
                if field["key"] in source:
                    asset[field["name"]] = source[field["key"]]

            if hasattr(self, "extraction_methods"):
                for extraction_method in self.extraction_methods:
                    asset = extraction_method.run(asset)

            assets[Path(path).name] = asset

        body["assets"] = assets

        return body
