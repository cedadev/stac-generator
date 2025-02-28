# encoding: utf-8
"""
Elasticsearch
-------------

An output backend which outputs the content generated to elasticsearch
using the Elasticsearch API

**Plugin name:** ``elasticsearch_bulk``

.. list-table::
    :header-rows: 1

    * - Option
      - Value Type
      - Description
    * - ``connection_kwargs``
      - ``dict``
      - ``REQUIRED`` Connection kwargs passed to the `elasticsearch client  <https://elasticsearch-py.readthedocs.io/en/latest/api.html#elasticsearch>`_
    * - ``index.name``
      - ``str``
      - ``REQUIRED`` The index to output the content.
    * - ``index.mapping``
      - ``str``
      - Path to a yaml file which defines the mapping for the index

Example Configuration:
    .. code-block:: yaml

        outputs:
            - method: elasticsearch_bulk
              connection_kwargs:
                hosts: ['host1','host2']
              index:
                name: 'assets-2021-06-02'
"""
__author__ = "Richard Smith"
__date__ = "01 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import logging
from collections.abc import Iterator

from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk
from pydantic import BaseModel, Field

from stac_generator.core.bulk_output import BulkOutput, BulkOutputConf
from stac_generator.core.utils import load_yaml

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


class ElasticsearchConf(BulkOutputConf):
    """Elasticsearch config model."""

    index: ElasticsearchIndex = Field(
        description="Elasticsearch index to post to.",
    )
    client_kwargs: dict = Field(
        default={},
        description="Elasticsearch connection kwargs.",
    )
    request_timeout: int = Field(
        default=60,
        description="Request timeout for search.",
    )


class ElasticsearchBulkOutput(BulkOutput):
    """
    Connects to an elasticsearch instance and exports the
    documents to elasticsearch.

    """

    config_class = ElasticsearchConf

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.es = Elasticsearch(**self.conf.client_kwargs)

        # Create the index, if it doesn't already exist
        if mapping := self.conf.index.mapping:
            if not self.es.indices.exists(self.conf.index.name):
                if isinstance(mapping, str):
                    mapping = load_yaml(mapping)
                self.es.indices.create(self.conf.index.name, body=mapping)

    def action_iterator(self, data_list: list) -> Iterator[dict]:
        """
        Generate an iterator of elasticsearch actions.

        :param data_list: List of output data

        :returns: elasticsearch action
        """
        for data in data_list:

            yield {
                "_op_type": "update",
                "_index": self.conf.index.name,
                "_id": data["id"],
                "doc": data["body"],
                "doc_as_upsert": True,
            }

    def export(self, data_list: list) -> None:
        """
        Export using elasticsearch bulk helper.
        """
        for okay, info in streaming_bulk(self.es, self.action_iterator(data_list), yield_ok=False):
            if not okay:
                LOGGER.error(
                    "Unable to index %s: %s",
                    info["update"]["_id"],
                    info["update"]["error"],
                )
