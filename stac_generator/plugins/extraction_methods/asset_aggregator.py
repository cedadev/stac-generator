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


class AssetAggregatorExtract(BaseExtractionMethod):
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

        if not hasattr(self, "list_terms"):
            self.list_terms = []

        if not hasattr(self, "sum_terms"):
            self.sum_terms = []

        if not hasattr(self, "avg_terms"):
            self.avg_terms = []

        if not hasattr(self, "min_terms"):
            self.min_terms = []

        if not hasattr(self, "max_terms"):
            self.max_terms = []


    def run(self, body: dict, **kwargs) -> dict:
        for index, list_term in enumerate(self.list_terms):
            body[list_term["name"]] = []

            if not hasattr(list_term, "key"):
                list_term["key"] = list_term["name"]

            self.list_terms[index] = list_term

        for index, sum_term in enumerate(self.sum_terms):
            body[sum_term["name"]] = 0

            if not hasattr(sum_term, "key"):
                sum_term["key"] = sum_term["name"]
        
            self.sum_terms[index] = sum_term

        len_sum_terms = index + 1
        for index, avg_term in enumerate(self.avg_terms):
            body[avg_term["name"]] = 0

            if not hasattr(avg_term, "key"):
                avg_term["key"] = avg_term["name"]
        
            self.sum_terms.append(avg_term)
            self.avg_terms[index] = avg_term

        for index, min_term in enumerate(self.min_terms):
            if not hasattr(min_term, "key"):
                min_term["key"] = min_term["name"]
        
            min_terms[index] = min_term

            body[min_term["name"]] = body["assets"].values()[0][min_term["key"]]

        for index, max_term in enumerate(self.max_terms):
            if not hasattr(max_term, "key"):
                max_term["key"] = max_term["name"]
        
            max_terms[index] = max_term

            body[max_term["name"]] = body["assets"].values()[0][max_term["key"]]

        for asset in body["assets"].values():
            for list_term in self.list_terms:
                body[list_term["name"]].append(asset[list_term["key"]])

            for sum_term in self.sum_terms:
                body[sum_term["name"]] += asset[sum_term["key"]]
            
            for avg_term in self.avg_terms:
                body[avg_term["name"]] /= len(body["assets"])

            for min_term in self.min_terms:
                if asset[min_term["key"]] < body[min_term["name"]]:
                    body[min_term["name"]] = asset[min_term["key"]]

            for max_term in self.max_terms:
                if asset[max_term["key"]] < body[max_term["name"]]:
                    body[max_term["name"]] = asset[max_term["key"]]

        return body
