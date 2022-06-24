# encoding: utf-8
"""

"""
__author__ = "Richard Smith"
__date__ = "02 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

from abc import ABC, abstractmethod

from stac_generator.core.generator import BaseGenerator
from stac_generator.core.utils import load_plugins


class BaseInputPlugin(ABC):
    def __init__(self, **kwargs):
        self.filters = None
        if kwargs.get("filters"):
            self.filters = load_plugins(
                kwargs, "stac_generator.plugin_filters", "filters"
            )

    def should_process(self, uri) -> bool:
        """
        Should the path be sent for processing?

        Will run through any filter plugins. All plugins must pass for a True
        response. Any False will short circuit the logic and return False

        :param uri: uri to test

        :return: Bool, ``default: True``
        """
        if self.filters:
            return any((filter.run(uri) for filter in self.filters))

        return True

    @abstractmethod
    def run(self, generator: BaseGenerator):
        ...
