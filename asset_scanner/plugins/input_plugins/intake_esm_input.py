# encoding: utf-8
"""
Intake Input
-----------------

Uses an `Intake catalog <https://intake.readthedocs.io/>`_ as a source for file objects.

**Plugin name:** ``intake_esm``

.. list-table::
    :header-rows: 1

    * - Option
      - Value Type
      - Description
    * - ``uri``
      - ``string``
      - ``REQUIRED`` The URI of a path or URL to an ESM collection JSON file.
    * - ``object_path_attr``
      - ``string``
      - ``REQUIRED`` The column header which contains the URI to the file object.
    * - ``catalog_kwargs``
      - ``dict``
      - Optional kwargs to pass to `intake.open_esm_datastore <https://intake-esm.readthedocs.io/en/latest/api.html#intake_esm.core.esm_datastore>`_
    * - ``search_kwargs``
      - ``dict``
      - Optional kwargs to pass to `esm_datastore.search <https://intake-esm.readthedocs.io/en/latest/api.html#intake_esm.core.esm_datastore.search>`_


Example Configuration:
    .. code-block:: yaml

        inputs:
            - name: intake_catalog
              uri: test_directory

"""
__author__ = 'Richard Smith'
__date__ = '23 Sep 2021'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

# Package imports
from .base import BaseInputPlugin

# Framework imports
from asset_scanner.types.source_media import StorageType

# Thirdparty imports
import intake


# Python imports
from datetime import datetime
import logging
from urllib.parse import urlparse
from typing import Optional, Tuple


logger = logging.getLogger(__name__)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from asset_scanner.core import BaseExtractor


class IntakeESMInputPlugin(BaseInputPlugin):
    """
    Performs an os.walk to provide a stream of paths for procesing.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.uri = kwargs['uri']
        self.object_attr = kwargs['object_path_attr']

        self.intake_kwargs = kwargs.get('catalog_kwargs', {})
        self.search_kwargs = kwargs.get('search_kwargs')

    def open_catalog(self):
        """Open the ESM catalog and perform a search, if required."""
        logger.info('Opening catalog')
        catalog = intake.open_esm_datastore(self.uri, **self.intake_kwargs)

        if self.search_kwargs:
            catalog = catalog.search(**self.search_kwargs)

        logger.info(f'Found {len(catalog.df)} items')
        return catalog

    def run(self, extractor: 'BaseExtractor'):
        total_files = 0
        start = datetime.now()
        
        catalog = self.open_catalog()

        for index, row in catalog.df.iterrows():
            filepath = getattr(row, self.object_attr)

            parse_result = urlparse(filepath)

            # Set media type
            media_type = StorageType.OBJECT_STORE
            if not parse_result.netloc:
                media_type = StorageType.POSIX

            if self.should_process(filepath, media_type):
                extractor.process_file(filepath, media_type, uri_parse=parse_result)
                logger.debug(f'Input processing: {filepath}')
            else:
                logger.debug(f'Input skipping: {filepath}')

            total_files += 1

        end = datetime.now()
        print(f'Processed {total_files} files from {self.uri} in {end-start}')