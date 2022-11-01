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
from time import perf_counter

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
            "mod_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "status": "new",
            "properties": {"uri": uri},
        }

        tic = perf_counter()

        # Get dataset description file
        description = self.collection_descriptions.get_description(uri)

        print(f"Descriptions got at {perf_counter() - tic:0.4f} seconds")

        LOGGER.info(
            "Processing uri: %s with description paths: %s", uri, description.paths
        )

        # Get the description path, used for item generation
        relevant_paths = [path for path in description.paths if uri.startswith(path)]

        description_path = max(relevant_paths, key=lambda x: x.count("/"))

        body["description_path"] = description_path

        print(f"Description path selected at {perf_counter() - tic:0.4f} seconds")

        # extract facets, run post extractions and extract ids
        extraction_methods_output = self.run_extraction_methods(
            uri, description, **kwargs
        )

        print(f"Extraction methods finished at {perf_counter() - tic:0.4f} seconds")

        body = dict_merge(body, extraction_methods_output)

        print(f"Body merged at {perf_counter() - tic:0.4f} seconds")

        body = self.run_post_extraction_methods(body, description, **kwargs)

        print(f"Post extraction finished at {perf_counter() - tic:0.4f} seconds")

        ids = self.run_id_extraction_methods(body, description, **kwargs)

        print(f"ID extraction finished at {perf_counter() - tic:0.4f} seconds")

        body["item_id"] = ids["item_id"]

        data = {"id": ids[f"{self.TYPE.value}_id"], "body": body}

        message = {
            f"{self.SURTYPE.value}_id": ids[f"{self.SURTYPE.value}_id"],
            "uri": uri,
        }

        self.output(data, message=message)

        print(f"Output finished at {perf_counter() - tic:0.4f} seconds")
