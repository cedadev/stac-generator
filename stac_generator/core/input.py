# encoding: utf-8
""" """
__author__ = "Richard Smith"
__date__ = "02 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

from abc import abstractmethod
from collections.abc import Callable

from stac_generator.core.process_config import SetConfig


class Input(SetConfig):
    """
    Base class to define an input
    """

    blocking: bool = False

    @abstractmethod
    def run(self):
        """
        Run the input plugin.
        """


class BlockingInput(Input):
    """
    Base class to define an input
    """

    blocking: bool = True

    @abstractmethod
    def run(self, process_method: Callable):
        """
        Run the input plugin.
        """
