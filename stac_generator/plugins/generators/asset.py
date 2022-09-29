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
from datetime import datetime

# Framework imports
from stac_generator.core.generator import BaseGenerator
from stac_generator.core.utils import dict_merge
from stac_generator.types.generators import GeneratorType

LOGGER = logging.getLogger(__name__)


class AssetGenerator(BaseGenerator):
    """
    The central class for the asset extraction process.

    An instance of the class can be used to atomically process files
    passed to its ``process`` method.
    """

    SURTYPE = GeneratorType.ITEM
    TYPE = GeneratorType.ASSET

    def process(self, uri: str, **kwargs) -> None:
        """
        Method to outline the processing pipeline for an asset

        :param uri:
        :param checksum:
        :return:
        """

        body = {
            "type": self.TYPE.value,
            "mod_time": datetime.now().strftime("%Y-%m-%d'T'%H%:M:%S.%fZ"),
            "status": "new",
            "properties": {"uri": uri},
        }

        # Get dataset description file
        description = self.collection_descriptions.get_description(uri)

        # extract facets, run post extractions and extract ids
        extraction_methods_output = self.run_extraction_methods(
            uri, description, **kwargs
        )

        body = dict_merge(body, extraction_methods_output)

        body = self.run_post_extraction_methods(body, description, **kwargs)

        ids = self.run_id_extraction_methods(body, description, **kwargs)

        body["item_id"] = ids["item_id"]

        data = {"id": ids[f"{self.TYPE.value}_id"], "body": body}

        message = {
            f"{self.SURTYPE.value}_id": ids[f"{self.SURTYPE.value}_id"],
            "uri": uri,
        }

        self.output(data, message=message)
