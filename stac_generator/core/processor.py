# encoding: utf-8
"""

"""
__author__ = "Richard Smith"
__date__ = "07 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

from abc import ABC, abstractmethod
from typing import Optional


class BaseProcessor(ABC):
    """
    Class to act as a base for all processors. Defines the basic method signature
    and ensure compliance by all subclasses.
    """

    def __init__(self, **kwargs):
        """
        Set the kwargs to generate instance attributes of the same name
        :param kwargs:
        """
        # Set default processor settings
        if "default_conf" in kwargs:
            self._set_attrs(kwargs["default_conf"])
        # Override with specific processor settings
        self._set_attrs(kwargs)

    def _set_attrs(self, conf: dict) -> None:
        for k, v in conf.items():
            setattr(self, k, v)


class BaseExtractionMethod(BaseProcessor):
    @abstractmethod
    def run(
        self,
        uri: str,
        **kwargs,
    ) -> dict:
        pass

    @abstractmethod
    def expected_terms(self, **kwargs) -> list:
        pass


class BasePostExtractionMethod(BaseProcessor):
    @abstractmethod
    def run(
        self,
        uri: str,
        body: dict,
        **kwargs,
    ) -> dict:
        pass

    @abstractmethod
    def expected_terms(
        self,
        term_list: Optional[list] = [],
    ) -> dict:
        pass


class BaseIdExtractionMethod(BaseProcessor):
    @abstractmethod
    def run(
        self,
        body: dict,
        **kwargs,
    ) -> dict:
        pass


class BasePreProcessor(BaseProcessor):
    @abstractmethod
    def run(self, uri: str, **kwargs) -> dict:
        pass


class BasePostProcessor(BaseProcessor):
    @abstractmethod
    def run(
        self,
        uri: str,
        source_dict: Optional[dict] = {},
        **kwargs,
    ) -> dict:
        pass

    @abstractmethod
    def expected_terms(
        self,
        term_list: Optional[list] = [],
    ) -> dict:
        pass
