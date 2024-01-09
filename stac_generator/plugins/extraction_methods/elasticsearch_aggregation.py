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
from collections import defaultdict

from stac_generator.core.extraction_method import BaseExtractionMethod

LOGGER = logging.getLogger(__name__)


class ElasticsearchAggregationExtract(BaseExtractionMethod):
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

                name: elasticsearch_aggregation
                inputs:
                    index: ceda-index
                    id_term: item_id
                    connection_kwargs:
                      hosts: ['host1:9200','host2:9200']
                    bbox:
                      - bbox
                    min:
                      - start_time
                    max:
                      - end_time
                    sum:
                      - size
                    list:
                      - term1
                      - term2
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if hasattr(self, "connection_kwargs"):
            self.es = Elasticsearch(**self.connection_kwargs)

        if not hasattr(self, "request_tiemout"):
            self.request_tiemout = 15

        for position, geo_bound_term in enumerate(self.geo_bounds):
            if "name" not in geo_bound_term:
                self.geo_bounds[position]["name"] = geo_bound_term["key"]

        for position, min_term in enumerate(self.min):
            if "name" not in min_term:
                self.min[position]["name"] = min_term["key"]

        for position, max_term in enumerate(self.max):
            if "name" not in max_term:
                self.max[position]["name"] = max_term["key"]

        for position, sum_term in enumerate(self.sum):
            if "name" not in sum_term:
                self.sum[position]["name"] = sum_term["key"]

        for position, list_term in enumerate(self.list):
            if "name" not in list_term:
                self.list[position]["name"] = list_term["key"]

    @staticmethod
    def geo_bounds_query(facet_key: str, facet_name: str) -> dict:
        """
        Query to retrieve the BBOX from items
        """
        return {facet_name: {"geo_bounds": {"field": facet_key}}}

    @staticmethod
    def facet_composite_query(facet_key: str, facet_name: str) -> dict:
        """
        Generate the composite aggregation for the facet
        :param facet: Facet to aggregate on
        """
        return {
            facet_name: {
                "composite": {
                    "sources": [{facet_name: {"terms": {"field": facet_key}}}],
                    "size": 100,
                }
            }
        }

    @staticmethod
    def min_query(facet_key: str, facet_name: str) -> dict:
        """
        Query to retrieve the minimum value from docs
        """
        return {facet_name: {"min": {"field": facet_key}}}

    @staticmethod
    def max_query(facet_key: str, facet_name: str) -> dict:
        """
        Query to retrieve the maximum value from docs
        """
        return {facet_name: {"max": {"field": facet_key}}}

    @staticmethod
    def sum_query(facet_key: str, facet_name: str) -> dict:
        """
        Query to retrieve the sum of the values from docs
        """
        return {facet_name: {"sum": {"field": facet_key}}}

    def extract_facet(self, facets: list):
        """
        Function to extract the given facets from the aggregation
        """
        for facet in facets:
            if facet["name"] in self.aggregations.keys():

                if "value_as_string" in self.aggregations[facet["name"]].keys():
                    value = self.aggregations[facet["name"]]["value_as_string"]

                elif "bounds" in self.aggregations[facet["name"]].keys():
                    value = self.aggregations[facet["name"]]["bounds"]

                else:
                    value = self.aggregations[facet["name"]]["value"]

                self.metadata[facet["name"]] = value

    def extract_first_facet(self, facets: list):
        """
        Function to extract the given default facets from the first hit
        """
        properties = self.hits[0]["_source"]["properties"]

        for facet in facets:
            if facet["key"] in properties.keys():
                self.metadata[facet["name"]] = properties[facet["key"]]

    def extract_facet_list(self, facets: list):
        """
        Function to extract the lists of given facets from the aggregation
        """
        next_query = self.base_query
        current_aggregations = self.aggregations

        while True:
            for facet in facets:
                if facet["name"] in current_aggregations.keys():
                    aggregation = current_aggregations[facet["name"]]

                    self.metadata[facet["name"]].extend(
                        [
                            bucket["key"][facet["name"]]
                            for bucket in aggregation["buckets"]
                        ]
                    )

                    if hasattr(aggregation, "after_key"):
                        next_query["aggs"] |= self.query["aggs"][facet["name"]]
                        next_query["aggs"][facet["name"]]["composite"]["sources"][
                            "after"
                        ] = {facet["name"]: aggregation["after_key"][facet["name"]]}

            if next_query == self.base_query:
                break

            else:
                result = self.es.search(index=self.index, body=next_query)
                current_aggregations = result["aggregations"].items()

    def construct_base_query(self, key: str, uri: str) -> dict:
        """
        Base query to filter the results to a single collection

        :param uri: Collection to restrict results to
        """
        self.base_query = {
            "query": {
                "bool": {
                    "must_not": [{"term": {"categories.keyword": {"value": "hidden"}}}],
                    "must": [{"term": {f"{key}": {"value": uri}}}],
                }
            },
            "aggs": {},
        }

    def construct_query(self):
        """
        Function to create the initial elasticsearch query
        """
        self.query = self.base_query

        if hasattr(self, "geo_bounds"):
            for geo_term in self.geo_bounds:
                self.query["aggs"].update(
                    self.geo_bounds_query(geo_term["key"], geo_term["name"])
                )

        if hasattr(self, "min"):
            for min_term in self.min:
                self.query["aggs"].update(
                    self.min_query(min_term["key"], min_term["name"])
                )

        if hasattr(self, "max"):
            for max_term in self.max:
                self.query["aggs"].update(
                    self.max_query(max_term["key"], max_term["name"])
                )

        if hasattr(self, "sum"):
            for sum_term in self.sum:
                self.query["aggs"].update(
                    self.sum_query(sum_term["key"], sum_term["name"])
                )

        if hasattr(self, "list"):
            for list_term in self.list:
                self.query["aggs"].update(
                    self.facet_composite_query(list_term["key"], list_term["name"])
                )

    def extract_metadata(self):
        """
        Function to extract the required metadata from the returned query result
        """
        if hasattr(self, "first"):
            self.extract_first_facet(self.first)

        if hasattr(self, "geo_bounds"):
            self.extract_facet(self.geo_bounds)

        if hasattr(self, "min"):
            self.extract_facet(self.min)

        if hasattr(self, "max"):
            self.extract_facet(self.max)

        if hasattr(self, "sum"):
            self.extract_facet(self.sum)

        if hasattr(self, "list"):
            self.extract_facet_list(self.list)

    def run(self, body: dict, **kwargs) -> dict:
        self.metadata = defaultdict(list)

        self.construct_base_query(self.id_term, body["uri"])

        self.construct_query()

        LOGGER.info("Elasticsearch query: %s", self.query)

        # Run query
        result = self.es.search(
            index=self.index, body=self.query, timeout=f"{self.request_tiemout}s"
        )

        self.hits = result["hits"]["hits"]

        self.aggregations = result["aggregations"]

        # Extract metadata
        self.extract_metadata()

        return body | self.metadata
