# encoding: utf-8
"""
Thredds Input
-----------------

Uses an `Intake catalog <https://intake.readthedocs.io/>`_
as a source for file objects.

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
      - ``REQUIRED`` The column header which contains the URI to
        the file object.
    * - ``catalog_kwargs``
      - ``dict``
      - Optional kwargs to pass to
        `intake.open_esm_datastore
        <https://intake-esm.readthedocs.io/en/latest
        /api.html#intake_esm.core.esm_datastore>`_
    * - ``search_kwargs``
      - ``dict``
      - Optional kwargs to pass to `esm_datastore.search
        <https://intake-esm.readthedocs.io/en/latest
        /api.html#intake_esm.core.esm_datastore.search>`_


Example Configuration:
    .. code-block:: yaml

        inputs:
            - name: intake_catalog
              uri: test_directory

"""
__author__ = "Mathieu Provencher"
__date__ = "3 Dec 2021"
__copyright__ = "Copyright 2021 Computer Research Institute of Montréal"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "mathieu.provencher@crim.ca"

# Python imports
import functools
import logging
from datetime import datetime
from typing import TYPE_CHECKING
from urllib.parse import urlparse

# Thirdparty imports
from siphon.catalog import TDSCatalog

# Framework imports
from asset_scanner.types.source_media import StorageType

# Package imports
from .base import BaseInputPlugin

logger = logging.getLogger(__name__)

from siphon.catalog import CaseInsensitiveDict


if TYPE_CHECKING:
    from asset_scanner.core import BaseExtractor


class ThreddsInputPlugin(BaseInputPlugin):
    """
    Performs an os.walk to provide a stream of paths for procesing.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.uri = kwargs["uri"]
        self.object_attr = kwargs["object_path_attr"]

        self.thredds_kwargs = kwargs.get("catalog_kwargs", {})
        self.search_kwargs = kwargs.get("search_kwargs")

    def open_catalog(self):
        """Open the Thredds catalog and perform a search, if required."""
        logger.info("Opening catalog")
        catalog = TDSCatalog(self.uri, **self.thredds_kwargs)

        # if self.search_kwargs:
        #     catalog = catalog.search(**self.search_kwargs)

        logger.info(f"Found {len(catalog.datasets.items())} items")

        return catalog


    def getsubattr(self, obj, path: str):
        """
        :param obj: Object
        :param path: 'attr1.attr2.etc'
        :return: obj.attr1.attr2.etc
        """
        attrs = path.split(".")

        for attr in attrs:
            if type(obj) == CaseInsensitiveDict:
                obj = obj[attr]
                continue

            obj = getattr(obj, attr)

        return obj




    def run(self, extractor: "BaseExtractor"):
        total_files = 0
        start = datetime.now()

        catalog = self.open_catalog()

        for index, row in catalog.datasets.items():
            filepath = self.getsubattr(row, self.object_attr)

            parse_result = urlparse(filepath)

            # Set media type
            media_type = StorageType.OBJECT_STORE
            if not parse_result.netloc:
                media_type = StorageType.POSIX

            if self.should_process(filepath, media_type):
                extractor.process_file(filepath, media_type)
                logger.debug(f"Input processing: {filepath}")
            else:
                logger.debug(f"Input skipping: {filepath}")

            total_files += 1

        end = datetime.now()
        print(f"Processed {total_files} files from {self.uri} in {end-start}")
