# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '01 Jun 2021'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'


# Framework imports
from asset_scanner.core.generator import BaseGenerator
from asset_scanner.core.utils import dict_merge, generate_id
from asset_scanner.types.generators import ExtractionType
from asset_scanner.types.source_media import StorageType
from asset_scanner.plugins.extraction_methods import utils as item_utils

# Python imports
import logging



LOGGER = logging.getLogger(__name__)


class AssetGenerator(BaseGenerator):
    """
    The central class for the asset extraction process.

    An instance of the class can be used to atomically process files
    passed to its ``process`` method.
    """

    EXTRACTION_TYPE = ExtractionType.ITEM

    def process(self, uri: str, **kwargs) -> None:
        """
        Method to outline the processing pipeline for an asset

        :param uri:
        :param checksum:
        :return:
        """

        body = {}

        # Get dataset description file
        if self.collection_descriptions:

            description = self.collection_descriptions.get_description(uri)
            categories = self.get_categories(uri, description)
            body['categories'] = categories

            # Get facet values
            processor_output = self.run_processors(uri, description, **kwargs)
            properties = processor_output.get('properties', {})

            # Get collection id
            coll_id = self.get_collection_id(description, uri)

            # Generate item id
            item_id = item_utils.generate_item_id_from_properties(
                uri,
                coll_id,
                properties,
                description
            )
            properties = dict_merge(properties, body.get('properties', {}))
            body['properties'] = properties
            body['item_id'] = item_id
            body['type'] = 'asset'

        data = {'id': generate_id(uri), 'body': body}

        self.output(uri, data, namespace="asset")

        # If deduplication enabled, check LRU cache and pass relevant kwargs
        kwargs = {
                    'deduplicate': False,
                    'id': item_id
                }

        if self.header_deduplication:
            # Check if id is in the cache
            if self.item_id_cache.get(item_id):
                kwargs['deduplicate'] = True
            # add a dummy value to the cache of equal to True.
            self.item_id_cache.update({item_id: True})

        message = {
            "item_id": item_id,
            "uri": uri,
        }

        self.output(uri, message, namespace="header", **kwargs)
