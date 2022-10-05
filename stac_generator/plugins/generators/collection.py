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
from datetime import datetime

from stac_generator.core.generator import BaseGenerator
from stac_generator.core.utils import dict_merge
from stac_generator.types.generators import GeneratorType

LOGGER = logging.getLogger(__name__)


class CollectionGenerator(BaseGenerator):

    TYPE = GeneratorType.COLLECTION
    SUBTYPE = GeneratorType.ITEM

    def process(self, uri: str, **kwargs) -> None:
        """
        Method to outline the processing pipeline for an asset

        :param uri:
        :param checksum:
        :return:
        """

        body = {
            "type": self.TYPE.value,
            "mod_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "status": "new",
        }

        # Get the description path, used for collection generation
        description_path = kwargs.get("description_path")

        if description_path:
            body["description_path"] = description_path

        else:
            description_path = uri

        # Get dataset description file
        description = self.collection_descriptions.get_description(description_path)

        # extract data
        extraction_methods_output = self.run_extraction_methods(
            uri, description, **kwargs
        )
        body = dict_merge(body, extraction_methods_output)

        body = self.run_post_extraction_methods(body, description, **kwargs)

        ids = self.run_id_extraction_methods(body, description, **kwargs)

        data = {"id": ids[f"{self.TYPE.value}_id"], "body": body}

        self.output(data)
