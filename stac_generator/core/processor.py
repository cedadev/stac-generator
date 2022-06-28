# encoding: utf-8
"""

"""
__author__ = "Richard Smith"
__date__ = "07 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

from abc import ABC, abstractmethod

from stac_generator.core.decorators import accepts_output_key


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

        for k, v in kwargs.items():
            setattr(self, k, v)

    @accepts_output_key
    @abstractmethod
    def run(self, uri: str) -> dict:
        """
        The action of running the processor and returning an output
        :param uri: URI for object
        :param kwargs: free kwargs passed to the processor.
        :return: dict
        """
        pass
