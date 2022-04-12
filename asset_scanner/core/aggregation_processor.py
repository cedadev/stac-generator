# encoding: utf-8
"""

"""
__author__ = "Richard Smith"
__date__ = "07 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

from abc import abstractmethod
from .item_describer import ItemDescription
from .processor import BaseProcessor


class BaseAggregationProcessor(BaseProcessor):
    """
    Modify the run method signature as the aggregation processor requires
    different information.
    """

    @abstractmethod
    def run(self, id: str, description: ItemDescription) -> dict:
        ...
