# encoding: utf-8
"""


Configuration
-------------

.. code-block:: yaml

    item_descriptions:
        root_directory: /path/to/root/descriptions

"""
__author__ = "Richard Smith"
__date__ = "27 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import logging

from stac_generator.core.generator import BaseGenerator
from stac_generator.types.generators import GeneratorType

LOGGER = logging.getLogger(__name__)


class CollectionGenerator(BaseGenerator):
    """
    Class defining the metadata extraction process for an collection.

    An instance of the class can be used to process files.
    """

    TYPE = GeneratorType.COLLECTION

    def _process(self, body: dict, **kwargs) -> None:
        """
        Method to outline the processing pipeline for an collection

        :param body:

        :return:
        """
        recipe = self.recipes.get(
            kwargs.get("recipe_path", body["uri"]), self.TYPE.value
        )

        LOGGER.debug(
            "Generating %s : %s with recipe %s", self.TYPE.value, body["uri"], recipe
        )

        body = self.run_extraction_methods(body, recipe.extraction_methods, **kwargs)

        body = self.run_extraction_methods(body, recipe.id, **kwargs)

        body = self.run_member_of_methods(body, recipe.member_of, **kwargs)

        self.output(body, recipe, **kwargs)
