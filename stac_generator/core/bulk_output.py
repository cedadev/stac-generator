# encoding: utf-8
"""

"""
__author__ = "Richard Smith"
__date__ = "01 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

from abc import ABC, abstractmethod

from cachetools import Cache


class BaseBulkOutput(ABC):
    """
    Base class to define an bulk output
    """

    def __init__(self, **kwargs):
        """
        Set the kwargs to generate instance attributes of the same name and create cache

        :param kwargs:
        """
        for k, v in kwargs.items():
            setattr(self, k, v)

        self.data_cache = Cache(maxsize=getattr(self, "cache_max_size", 100) + 1)

    @property
    def data_list(self):
        """
        Extract the data from the cache into a list.
        """
        return [data for _, data in dict(self.data_cache.items()).items()]

    @abstractmethod
    def export(self, data_list: list) -> None:
        """
        Output the data.

        :param data: list of data from processor to be output.
        :param kwargs:
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
        Export the data to rabbit.

        :param data: expected data as header dict
        """
        # add to cache
        self.data_cache.update(self.data_to_cache(data))

        if self.data_cache.currsize >= getattr(self, "cache_max_size", 100):
            self.clear_cache()

    def clear_cache(self) -> None:
        """
        Run after input is finished to clear remaining data.
        """
        self.export(self.data_list)
        self.data_cache.clear()
