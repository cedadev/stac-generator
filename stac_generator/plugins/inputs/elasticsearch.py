# encoding: utf-8
"""
Elasticsearch Input
-------------------

Uses an `Elasticsearch index <https://www.elastic.co/>`_
as a source for file objects.

**Plugin name:** ``elasticsearch``

.. list-table::
    :header-rows: 1

    * - Option
      - Value Type
      - Description
    * - ``id``
      - ``string``
      - ``REQUIRED`` The property which contains the URI of the object that
        is to be created.
    * - ``connection_kwargs``
      - ``dict``
      - Connection kwargs passed to
        `elasticsearch.Elasticsearch
        <https://elasticsearch-py.readthedocs.io/en/7.10.0/api.html>`_
    * - ``search_kwargs``
      - ``dict``
      - Optional search kwargs passed to
        `elasticsearch.Elasticsearch
        <https://elasticsearch-py.readthedocs.io/en/v8.8.1/api.html>`_


Example Configuration:
    .. code-block:: yaml

        name: elasticsearch
        id_term: item_id
        connection_kwargs:
          index: ceda-index
          hosts: ['host1:9200','host2:9200']
          request_timeout: 60


"""
__author__ = "Rhys Evans"
__date__ = "28 Jun 2023"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "rhys.r.evans@stfc.ac.uk"

# Python imports
import logging
from datetime import datetime

# Thirdparty imports
from elasticsearch import Elasticsearch

from stac_generator.core.generator import BaseGenerator

# Package imports
from stac_generator.core.input import BaseInput

LOGGER = logging.getLogger(__name__)


class ElasticsearchInput(BaseInput):
    """
    Performs an os.walk to provide a stream of paths for procesing.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id_term = kwargs["id_term"]
        self.index = kwargs["index"]

        self.connection_kwargs = kwargs.get("connection_kwargs", {})
        self.search_kwargs = kwargs.get("search_kwargs")

    def run(self, generator: BaseGenerator):
        start = datetime.now()
        total_generated = 0

        es_client = Elasticsearch(**self.connection_kwargs)

        query = {
            "aggs": {
                "bucket": {
                    "composite": {
                        "sources": [
                            {
                                "uri": {
                                    "terms": {"field": f"{self.id_term}.keyword"},
                                }
                            },
                            {
                                "description_path": {
                                    "terms": {"field": "description_path.keyword"},
                                }
                            },
                        ],
                        "size": 100,
                    }
                }
            },
            "size": 0,
        }

        if self.search_kwargs:
            query["query"] = self.search_kwargs

        while True:

            result = es_client.search(index=self.index, body=query)

            aggregation = result["aggregations"]["bucket"]

            print(aggregation)

            for bucket in aggregation["buckets"]:
                print(bucket)
                uri = bucket["key"]["uri"]
                if self.should_process(uri):
                    generator.process(**bucket["key"])
                    total_generated += 1

            if "after_key" not in aggregation.keys():
                break

            query["aggs"]["bucket"]["composite"]["after"] = aggregation["after_key"]

        end = datetime.now()
        print(f"Processed {total_generated} elasticsearch records in {end-start}")
