# encoding: utf-8
__author__ = "Richard Smith"
__date__ = "01 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

from pydantic import BaseModel, Field

from stac_generator.core.output import Output
from stac_generator.core.utils import load_yaml
from stac_generator.plugins.bulk_outputs.elasticsearch import Elasticsearch


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
    client_kwargs: dict = Field(
        default={},
        description="Elasticsearch connection kwargs.",
    )
    request_timeout: int = Field(
        default=60,
        description="Request timeout for search.",
    )


class ElasticsearchOutput(Output):
    """
    Output generated meta data to elasticsearch.

    **Plugin name:** ``elasticsearch``

    Example Configuration:
        .. code-block:: yaml

            - name: elasticsearch
                conf:
                  client_kwargs:
                    hosts: ['host1','host2']
                  index:
                    name: 'assets-2021-06-02'
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

    def export(self, data: dict, **kwargs) -> None:

        self.es.update(
            index=self.conf.index.name,
            id=data["id"],
            body={"doc": data, "doc_as_upsert": True},
            request_timeout=self.conf.request_timeout,
        )
