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

from asset_scanner.core.generator import BaseGenerator
from asset_scanner.core.utils import dict_merge

from asset_scanner.types.generators import ExtractionType

LOGGER = logging.getLogger(__name__)


class ItemGenerator(BaseGenerator):

    EXTRACTION_TYPE = ExtractionType.COLLECTION
    
    def process(self, uri: str, **kwargs) -> None:
        """
        Method to outline the processing pipeline for an asset

        :param uri:
        :param checksum:
        :return:
        """

        body = {
            'type': self.EXTRACTION_TYPE.value
        }

        # Get dataset description file

        description = self.collection_descriptions.get_description(uri)

        # extract data
        extraction_methods_output = self.run_extraction_methods(uri, description, **kwargs)
        body = dict_merge(body, extraction_methods_output)

        body = self.run_post_extraction_methods(body, description, **kwargs)

        ids = self.run_id_extraction_methods(body, description, **kwargs)

        data = {'id': ids["collection_id"], 'body': body}

        self.output(data)
