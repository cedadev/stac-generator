# encoding: utf-8
"""

"""
__author__ = "Richard Smith"
__date__ = "01 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


# Python imports
import logging

# Framework imports
from stac_generator.core.generator import BaseGenerator
from stac_generator.types.generators import GeneratorType

LOGGER = logging.getLogger(__name__)


class AssetGenerator(BaseGenerator):
    """
    Class defining the metadata extraction process for an asset.

    An instance of the class can be used to process files.
    """

    TYPE = GeneratorType.ASSET

    def _process(self, body: dict, **kwargs) -> None:
        """
        Method to outline the processing pipeline for an asset

        :param body:

        :return:
        """
        recipe = self.recipes.get(kwargs.get("recipe_path", body["uri"]), self.TYPE.value)

        LOGGER.debug(
            "Generating %s : %s with recipe %s", self.TYPE.value, body["uri"], recipe
        )

        body = self.run_extraction_methods(body, recipe.extraction_methods, **kwargs)

        body = self.run_extraction_methods(body, recipe.id, **kwargs)

        body = self.run_member_of_methods(body, recipe.member_of, **kwargs)

        self.output(body, recipe, **kwargs)
