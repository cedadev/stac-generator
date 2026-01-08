# encoding: utf-8
__author__ = "Rhys Evans"
__date__ = "28 Jun 2023"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "rhys.r.evans@stfc.ac.uk"
# Python imports
import logging
from datetime import datetime

from extraction_methods.core.types import KeyOutputKey
from pydantic import BaseModel, Field

# Package imports
from stac_generator.core.input import Input

# Thirdparty imports
from stac_generator.plugins.bulk_outputs.elasticsearch import Elasticsearch

LOGGER = logging.getLogger(__name__)


class ElasticsearchIndex(BaseModel):
    """Elasticsearch index model."""

    name: str = Field(
        description="Name of index.",
    )
    mapping: str | dict = Field(
        default={},
        description="Index initial mapping.",
    )


class ElasticsearchConf(BaseModel):
    """Elasticsearch config model."""

    index: ElasticsearchIndex = Field(
        description="Elasticsearch index to post to.",
    )
    uri_term: str = Field(
        default="uri.keyword",
        description="Term to use as uri.",
    )
    client_kwargs: dict = Field(
        default={},
        description="Elasticsearch connection kwargs.",
    )
    extra_terms: list[KeyOutputKey] = Field(
        default=[],
        description="List of extra terms.",
    )
    query: dict = Field(
        default={},
        description="Elasticsearch search query.",
    )
    request_timeout: int = Field(
        default=60,
        description="Request timeout for search.",
    )


class ElasticsearchAggregationInput(Input):
    """
    Preforms an [Elasticsearch Aggregation](https://www.elastic.co/)
    to provide a stream of events for procesing.

    **Plugin name:** ``elasticsearch``

    Example Configuration:
        .. code-block:: yaml

            name: elasticsearch
            conf:
              id_term: item_id
              connection_kwargs:
              index: ceda-index
              hosts: ['host1:9200','host2:9200']
              request_timeout: 60
    """

    config_class = ElasticsearchConf

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id_term = kwargs["id_term"]
        self.index = kwargs["index"]

        self.search_kwargs = kwargs.get("search_kwargs")

    def run(self):
        start = datetime.now()
        total_generated = 0

        es_client = Elasticsearch(**self.conf.client_kwargs)

        body = {
            "query": self.conf.query,
            "aggs": {
                "bucket": {
                    "composite": {
                        "sources": [
                            {
                                "uri": {
                                    "terms": {"field": {self.conf.uri_term}},
                                }
                            },
                            {
                                "recipe_path": {
                                    "terms": {"field": "recipe_path.keyword"},
                                }
                            },
                        ],
                        "size": 100,
                    }
                }
            },
            "size": 0,
        }

        for extra_term in self.conf.extra_terms:
            body["bucket"]["composite"][extra_term.key] = {
                "terms": {"field": f"{extra_term.key}"},
            }

        while True:
            result = es_client.search(
                index=self.index, body=body, request_timeout=self.conf.request_timeout
            )

            aggregation = result["aggregations"]["bucket"]

            for bucket in aggregation["buckets"]:
                output = {"uri": bucket["key"]["uri"]}

                for extra_term in self.conf.extra_terms:
                    output[extra_term.output_key] = bucket["key"][extra_term.key]

                yield output
                total_generated += 1

            if "after_key" not in aggregation.keys():
                break

            body["aggs"]["bucket"]["composite"]["after"] = aggregation["after_key"]

        end = datetime.now()
        print(f"Processed {total_generated} elasticsearch records in {end-start}")
