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

    def hit_to_asset(self, hit: dict, asset: dict):
        """Convert elasticsearch hit to asset"""
        for term_key, term_value in hit.items():
            if term_key == "properties":
                asset = self.hit_to_asset(asset, term_value)

            else:
                asset[term_key] = term_value

        return asset

    def run(self, body: dict, **kwargs) -> dict:
        query = {
            "query": {
                "bool": {
                    "must_not": [{"term": {"categories.keyword": {"value": "hidden"}}}],
                    "must": [
                        {"term": {f"{self.id_term}.keyword": {"value": body["uri"]}}}
                    ],
                }
            },
            "_source": self.fields + [f"properties.{field}" for field in self.fields],
        }

        # Run query
        result = self.es.search(
            index=self.index, body=query, timeout=self.request_tiemout
        )

        assets = {}
        for hit in result["hits"]["hits"]:
            asset = hit_to_asset(hit, {})

            assets[hit["_id"]] = asset

        body["assets"] = assets

        return body
