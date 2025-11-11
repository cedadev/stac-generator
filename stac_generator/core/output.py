# encoding: utf-8
""" """
__author__ = "Richard Smith"
__date__ = "01 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

from abc import abstractmethod

from stac_generator.core.baker import Recipe
from stac_generator.core.process_config import SetConfig
from stac_generator.core.utils import load_plugins


class Output(SetConfig):
    """
    Base class to define an output
    """

    def __init__(self, **kwargs):
        """
        Set the kwargs to generate instance attributes of the same name

        :param kwargs:
        """
        self.mappings = (
            load_plugins(kwargs["mappings"], "stac_generator.mappings")
            if "mappings" in kwargs
            else []
        )

        super().__init__(**kwargs)

    @abstractmethod
    def export(self, data: dict, **kwargs) -> None:
        """
        Output the data.

        :param data: data from processor to be output.
        :param kwargs:
        """

    # This allows for bulk outputs
    def run(self, body: dict, recipe: Recipe, **kwargs) -> None:
        """
        Run the output.

        :param data: data from processor to be output.
        :param kwargs:
        """
        output_body = body.copy()

        for mapping in self.mappings:
            output_body = mapping.run(output_body, recipe, **kwargs)

        self.export(output_body, **kwargs)
