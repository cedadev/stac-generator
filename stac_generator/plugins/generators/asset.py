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

from stac_generator.core.collection_describer import CollectionDescription

# Framework imports
from stac_generator.core.generator import BaseGenerator
from stac_generator.types.generators import GeneratorType

LOGGER = logging.getLogger(__name__)


class AssetGenerator(BaseGenerator):
    """
    The central class for the asset extraction process.

    An instance of the class can be used to atomically process files
    passed to its ``process`` method.
    """

    TYPE = GeneratorType.ASSET

    def run_id_extraction_methods(
        self, body: dict, description: CollectionDescription, **kwargs: dict
    ) -> dict:
        """
        Extract the raw facets from the listed extraction methods

        :param body: Dict of current extracted data
        :param description: CollectionDescription
        :return: dictionary containing ids
        """

        ids = {}

        # item_description = description.item

        # if item_description and item_description.id:
        #     item_id_description = item_description.id

        # else:
        #     item_id_description = self.DEFAULT_ID_EXTRACTION_METHODS["item_id"]

        # ids["item_id"] = self._run_extraction_method(
        #     item_id_description, body, **kwargs
        # )

        asset_description = description.asset

        if asset_description.id:
            asset_id_method = asset_description.id

        else:
            asset_id_method = self.DEFAULT_ID_EXTRACTION_METHODS["asset_id"]

        output = self._run_extraction_method(body, asset_id_method, **kwargs)

        ids["asset_id"] = output.pop("asset_id")

        return ids

    def _process(self, body: dict, **kwargs) -> None:
        """
        Method to outline the processing pipeline for an asset

        :param body:

        :return:
        """

        # Get dataset description file
        description = self.collection_descriptions.get_description(
            body["uri"], **kwargs
        )

        body = self.run_extraction_methods(body, description, **kwargs)

        ids = self.run_id_extraction_methods(body, description, **kwargs)

        data = self.map(ids, body, description, **kwargs)

        self.output(data, description=description, **kwargs)
