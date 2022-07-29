# encoding: utf-8
"""

"""
__author__ = "Richard Smith"
__date__ = "01 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

from abc import ABC, abstractmethod


class BaseOutput(ABC):
    """
    Base class to define an output
    """

    def __init__(self, **kwargs):
        """
        Set the kwargs to generate instance attributes of the same name

        :param kwargs:
        """

        for k, v in kwargs.items():
            setattr(self, k, v)

    @abstractmethod
    def export(self, data: dict) -> None:
        """
        Output the data.

        :param data: data from processor to be output.
        :param kwargs:
        """

    def run(self, data: dict) -> None:
        """
        Run the output.

        :param data: data from processor to be output.
        :param kwargs:
        """
        self.export(data)
