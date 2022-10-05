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
from string import Template

from stac_generator.core.generator import BaseGenerator
from stac_generator.core.utils import dict_merge
from stac_generator.types.generators import GeneratorType

LOGGER = logging.getLogger(__name__)


class ItemGenerator(BaseGenerator):

    SURTYPE = GeneratorType.COLLECTION
    TYPE = GeneratorType.ITEM
    SUBTYPE = GeneratorType.ASSET

    def process_template(self, uri: str, **kwargs):
        """
        Method to outline the processing pipeline for an item

        :param uri:
        :return:
        """
        properties = {}

        # Generate title and description properties from templates
        description = self.collection_descriptions.get_description(uri)
        templates = description.facets.templates

        if templates:
            if templates.title:
                title_template = templates.title
                title = Template(title_template).safe_substitute(properties)
                properties["title"] = title
            if templates.description:
                desc_template = templates.description
                desc = Template(desc_template).safe_substitute(properties)
                properties["description"] = desc

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

        body["collection_id"] = ids["collection_id"]
        body["item_id"] = ids["item_id"]

        data = {"id": ids[f"{self.TYPE.value}_id"], "body": body}

        message = {
            f"{self.SURTYPE.value}_id": ids[f"{self.SURTYPE.value}_id"],
            "uri": uri,
        }

        self.output(data, message=message)
