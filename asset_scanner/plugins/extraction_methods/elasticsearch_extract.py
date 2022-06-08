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

# Python imports
from collections import defaultdict
import logging

# Third party imports
from elasticsearch import Elasticsearch

from asset_scanner.core.decorators import accepts_postprocessors, accepts_preprocessors

# Package imports
from asset_scanner.core.processor import BaseProcessor

from .mixins import PropertiesOutputKeyMixin

LOGGER = logging.getLogger(__name__)


class ElasticsearchExtract(PropertiesOutputKeyMixin, BaseProcessor):
    """
    Description:
        Using an ID. Generate a summary of information for higher level entities.

    Configuration Options:
        - ``index``: ``REQUIRED`` Name of the index holding the STAC entities
        - ``connection_kwargs``: ``REQUIRED`` Connection parameters passed to
        `elasticsearch.Elasticsearch<https://elasticsearch-py.readthedocs.io/en/7.10.0/api.html>`_

    Configuration Example:

        .. code-block:: yaml

                name: elasticsearch
                inputs:
                    index: ceda-index
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

    @staticmethod
    def bbox_query(facet: str) -> dict:
        """
        Query to retrieve the BBOX from items
        """
        return {
            "bbox": {
                "geo_bounds": {
                    "field": facet,    
                    "wrap_longitude": True  
                }
            }
        }

    @staticmethod
    def facet_composite_query(facet: str) -> dict:
        """
        Generate the composite aggregation for the facet
        :param facet: Facet to aggregate on
        """
        return {
            facet: {
                "composite": {
                    "sources": [
                        {
                            facet: {
                                "terms": {
                                    "field": f"properties.{facet}.keyword"
                                }
                            }
                        }
                    ],
                    "size": 100
                }
            }
        }

    @staticmethod
    def min_query(facet: str) -> dict:
        """
        Query to retrieve the minimum value from docs
        """
        return {
            facet: {
                "min": {"field": f"properties.{facet}"}
            }
        }
    
    @staticmethod
    def max_query(facet: str) -> dict:
        """
        Query to retrieve the maximum value from docs
        """
        return {
            facet: {
                "max": {"field": f"properties.{facet}"}
            }
        }
    
    @staticmethod
    def sum_query(facet: str) -> dict:
        """
        Query to retrieve the sum of the values from docs
        """
        return {
            facet: {
                "sum": {"field": f"properties.{facet}"}
            }
        }

    def extract_facet(self, facets: list):
        """
        Function to extract the given facets from the aggregation
        """
        for facet in facets:

            if facet in self.aggregations.keys():

                if "value_as_string" in self.aggregations[facet].keys():
                    value = self.aggregations[facet]["value_as_string"]

                else:
                    value = self.aggregations[facet]["value"]
                    
                self.metadata[facet] = value
    
    def extract_default_facet(self, facets: list):
        """
        Function to extract the given default facets from the first hit
        """
        properties = self.hits[0]['_source']["properties"]

        for facet in facets:

            if facet in properties.keys():
                self.metadata[facet] = properties[facet]
    
    def extract_facet_list(self, facets: list):
        """
        Function to extract the lists of given facets from the aggregation
        """
        next_query = self.base_query
        items = self.aggregations

        while True:

            for facet in facets:

                if facet in items.keys():

                    aggregation = items[facet]

                    self.metadata[facet].extend([bucket['key'][facet] for bucket in aggregation["buckets"]])

                    if hasattr(aggregation, "after_key"):
                        next_query["aggs"] |= self.query["aggs"][facet] 
                        next_query["aggs"][facet]["composite"]["sources"]["after"] = {facet: aggregation["after_key"][facet]}
        
            if next_query == self.base_query:
                break

            else:
                result = self.es.search(index=self.index, body=next_query)
                items = result['aggregations'].items()
            
    def construct_base_query(self, key: str, id: str) -> dict:
        """
        Base query to filter the results to a single collection

        :param file_id: Collection to restrict results to
        """
        self.base_query = {
            "query": {
                "bool": {
                "must_not": [
                    {
                    "term": {
                        "categories.keyword": {
                        "value": "hidden"
                        }
                    }
                    }
                ],
                "must": [
                    {
                    "term": {
                        f"{key}.keyword": {
                        "value": id
                        }
                    }
                    }
                ]
                }
            },
            "aggs": {}
        }
    
    def construct_query(self):
        """
        Function to create the initial elasticsearch query
        """
        self.query = self.base_query

        if hasattr(self, "bbox"):
            for bbox in self.bbox:
                self.query["aggs"] |= self.bbox_query(bbox)
        
        if hasattr(self, "min"):
            for min in self.min:
                self.query["aggs"] |= self.min_query(min)

        if hasattr(self, "max"):
            for max in self.max:
                self.query["aggs"] |= self.max_query(max)
        
        if hasattr(self, "sum"):
            for sum_term in self.sum:
                self.query["aggs"] |= self.sum_query(sum_term)

        if hasattr(self, "list"):
            for list_term in self.list:
                self.query["aggs"] |= self.facet_composite_query(list_term)
        
    def extract_metadata(self):
        """
        Function to extract the required metadata from the returned query result
        """
        if hasattr(self, "default"):
            self.extract_default_facet(self.default)
        
        if hasattr(self, "bbox"):
            self.extract_facet(self.bbox)
        
        if hasattr(self, "min"):
            self.extract_facet(self.min)

        if hasattr(self, "max"):
            self.extract_facet(self.max)

        if hasattr(self, "sum"):
            self.extract_facet(self.sum)
        
        if hasattr(self, "list"):
            self.extract_facet_list(self.list)

        
    @accepts_preprocessors
    @accepts_postprocessors
    def run(self, filepath: str, source_media: str = "POSIX", **kwargs) -> dict:

        self.metadata = defaultdict(list)

        self.es = Elasticsearch(**self.connection_kwargs)

        self.construct_base_query(filepath)

        self.construct_query()

        # Run query
        result = self.es.search(index=self.index, body=self.query)

        self.hits = result['hits']["hits"]

        self.aggregations = result['aggregations']

        # Extract metadata
        self.extract_metadata()

        return self.metadata
