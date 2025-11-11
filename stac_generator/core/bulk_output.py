# encoding: utf-8
""" """
__author__ = "Richard Smith"
__date__ = "01 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

from abc import abstractmethod

from cachetools import Cache
from pydantic import BaseModel, Field

from stac_generator.core.process_config import SetConfig


class BulkOutputConf(BaseModel):
    """Elasticsearch config model."""

    cache_max_size: str = Field(
        description="Max size of cache.",
    )


class BulkOutput(SetConfig):
    """
    Base class to define an bulk output
    """

    config_class = BulkOutputConf

    def __init__(self, **kwargs):
        """
        Set the kwargs to generate instance attributes of the same name and create cache

        :param kwargs:
        """
        super().__init__(**kwargs)

        self.data_cache = Cache(maxsize=self.conf.cache_max_size + 1)

    def __del__(self):
        self.clear_cache()

    @property
    def data_list(self):
        """
        Extract the data from the cache into a list.
        """
        return dict(self.data_cache.items()).values()

    @abstractmethod
    def export(self, data_list: list) -> None:
        """
        Output the data.

        :param data: list of data from processor to be output.
        """

    def data_to_cache(self, data: dict) -> None:
        """
        Convert the data into a data to  be stored in cache.

        :param data: data from processor to be output.
        :param kwargs:
        """
        return {data["id"]: data}

    def run(self, data: dict) -> None:
        """
        Add data to cache and if cache is full export data.

        :param data: data to be exported
        """
        # add to cache
        self.data_cache.update(self.data_to_cache(data))

        if self.data_cache.currsize >= self.conf.cache_max_size:
            self.clear_cache()

    def clear_cache(self) -> None:
        """
        Run after input is finished to clear remaining data.
        """
        self.export(self.data_list)
        self.data_cache.clear()
