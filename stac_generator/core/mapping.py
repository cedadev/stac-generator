# encoding: utf-8
"""

"""
__author__ = "Richard Smith"
__date__ = "07 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

from abc import abstractmethod

from stac_generator.core.baker import Recipe
from stac_generator.core.process_config import SetConfig


class BaseMapping(SetConfig):
    """
    Class to act as a base for all mappings. Defines the basic method signature
    and ensure compliance by all subclasses.
    """

    @abstractmethod
    def run(self, body: dict, recipe: Recipe, **kwargs) -> dict:
        """
        Run the mapping

        :param body:
        :param recipe:
        :param kwargs:

        :return body:
        """
