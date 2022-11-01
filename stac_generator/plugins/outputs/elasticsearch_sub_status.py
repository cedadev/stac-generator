# encoding: utf-8
"""
Elasticsearch
-------------

An output backend which outputs the content generated to elasticsearch
using the Elasticsearch API

**Plugin name:** ``elasticsearch``

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
            - method: elasticsearch
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

from typing import Dict

from elasticsearch import Elasticsearch

from stac_generator.core.output import BaseOutput
from stac_generator.core.utils import Coordinates, load_yaml


class ElasticsearchOutput(BaseOutput):
    """
    Connects to an elasticsearch instance and updates the
    states of sub documents in elasticsearch.

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        index_conf = kwargs["index"]

        self.es = Elasticsearch(**kwargs["connection_kwargs"])
        self.index_name = index_conf["name"]
        self.id_key = index_conf["id_key"]

    def export(self, data, **kwargs):

        body = {
            "script": {
                "inline": "ctx._source.status = params.status",
                "lang": "painless",
                "params": {"status": "aggregated"},
            },
            "query": {
                "term": {
                    self.id_key: {"value": data[self.id_key]},
                }
            },
        }

        self.es.update_by_query(index=self.index_name, body=body)
