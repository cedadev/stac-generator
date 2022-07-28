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


class BaseOutput(ABC):
    def __init__(self, **kwargs):
        """
        Set the kwargs to generate instance attributes of the same name
        :param kwargs:
        """

        for k, v in kwargs.items():
            setattr(self, k, v)

    @abstractmethod
    def export(self, data, **kwargs):
        pass


class BaseBulkOutput(BaseOutput):
    def __init__(self, **kwargs):
        """
        Create Cache
        :param kwargs:
        """
        super().__init__(**kwargs)
        self.message_cache = Cache(maxsize=getattr(self, "cache_max_size", 100) + 1)

    @abstractmethod
    def clear_cache(self):
        pass

    def finished(self):
        self.clear_cache()
