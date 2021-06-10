# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '07 Jun 2021'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from abc import ABC, abstractmethod


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

    @abstractmethod
    def run(self, filepath: str, media_source: str = 'POSIX', **kwargs) -> dict:
        """
        The action of running the processor and returning an output
        :param filepath: Path to object
        :param media_source: Media type for the target object
        :param kwargs: free kwargs passed to the processor.
        :return: dict
        """
        pass
