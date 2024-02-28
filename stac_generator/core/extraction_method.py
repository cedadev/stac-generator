# encoding: utf-8
"""

"""
__author__ = "Richard Smith"
__date__ = "07 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

from abc import ABC, abstractmethod


class BaseExtractionMethod(ABC):
    """
    Class to act as a base for all extracion methods. Defines the basic method signature
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

        if not hasattr(self, "exists_key"):
            self.exists_key = "$"

    def _set_attrs(self, conf: dict) -> None:
        """
        Set instance attributes

        :param conf:
        """
        for key, value in conf.items():
            setattr(self, key, value)

    @abstractmethod
    def run(self, body: dict, **kwargs) -> dict:
        """
        Run the extration method

        :param body:
        :param kwargs:

        :return body:
        """
