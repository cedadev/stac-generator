# encoding: utf-8
"""


Configuration
-------------

.. code-block:: yaml

    item_descriptions:
        root_directory: /path/to/root/descriptions

"""
__author__ = 'Richard Smith'
__date__ = '27 May 2021'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

import logging
from string import Template

from asset_scanner.core.generator import BaseGenerator
from asset_scanner.core.utils import dict_merge, generate_id

from asset_scanner.types.source_media import StorageType
from asset_scanner.types.generators import ExtractionType

from asset_scanner.plugins.extraction_methods import utils as item_utils

LOGGER = logging.getLogger(__name__)


class ItemGenerator(BaseGenerator):

    EXTRACTION_TYPE = ExtractionType.COLLECTION
    
    def process(self, uri: str, **kwargs):
        """
        Method to outline the processing pipeline for an individual file
        :param uri:
        :return:
        """
        # Generate file ID
        uri = generate_id(uri)

        LOGGER.info(f'Processing: {uri}')

        # Get dataset description file
        description = self.collection_descriptions.get_description(uri)

        generator_description = description.get

        # processor_output = self.run_processors(filepath, description, source_media, **kwargs)

        # properties = processor_output.get('properties', {})
        properties = {}

        # Generate title and description properties from templates
        templates = description.facets.templates

        if templates:
            if templates.title:
                title_template = templates.title
                title = Template(title_template).safe_substitute(properties)
                properties['title'] = title
            if templates.description:
                desc_template = templates.description
                desc = Template(desc_template).safe_substitute(properties)
                properties['description'] = desc

        # Get collection id
        coll_id = description.collections.id

        # Generate item id
        if kwargs.get('item_id'):
            item_id = kwargs['item_id']
        # This can be removed, properties no longer needed for id if passed in kwargs
        else:
            item_id = item_utils.generate_item_id_from_properties(
                uri,
                coll_id,
                properties,
                description
            )

        body = {
                'item_id': item_id,
                'type': 'item',
                'collection_id': coll_id,
                'properties': properties
            }

        merged_body = dict_merge(body, summaries)

        output = {
            'id': item_id,
            'body': merged_body
        }

        # Output the item
        self.output(uri, output, namespace='items')

        # If deduplication enabled, check LRU cache and pass relevant kwargs
        kwargs = {
                    'deduplicate': False,
                    'id': coll_id
                }
        if self.header_deduplication:
            # Check if id is in the cache
            if self.collection_id_cache.get(coll_id):
                kwargs['deduplicate'] = True
            # add a dummy value to the cache of equal to True.
            self.collection_id_cache.update({coll_id: True})

        message = {
            'collection_id': coll_id,
            'uri': uri,
        }

        # Output the header
        self.output(uri, message, namespace='header', **kwargs)
