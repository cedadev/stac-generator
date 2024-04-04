# encoding: utf-8
"""
Intake Input
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
    * - ``skip``
      - ``int``
      - Optional value to skip the first n rows


Example Configuration:
    .. code-block:: yaml

        inputs:
            - method: intake_catalog
              uri: test_directory

"""
__author__ = "Richard Smith"
__date__ = "23 Sep 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

# Python imports
import logging
from datetime import datetime

# Thirdparty imports
import intake

from stac_generator.core.generator import BaseGenerator

# Package imports
from stac_generator.core.input import BaseInput

LOGGER = logging.getLogger(__name__)


class IntakeESMInput(BaseInput):
    """
    Performs an os.walk to provide a stream of paths for procesing.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.uri = kwargs["uri"]

        self.object_attr = kwargs["object_path_attr"]
        self.skip = kwargs.get("skip", -1)

        self.intake_kwargs = kwargs.get("catalog_kwargs", {})
        self.search_kwargs = kwargs.get("search_kwargs")

    def open_catalog(self, uri, intake_kwargs):
        """Open the ESM catalog."""
        LOGGER.info(f"Opening catalog {uri}")
        return intake.open_esm_datastore(uri, **intake_kwargs)

    def search_catalog(self, catalog, search_kwargs):
        """Perform a search ESM catalog."""
        LOGGER.info("Searching catalog")

        if self.search_kwargs:
            catalog = catalog.search(**search_kwargs)

        LOGGER.info(f"Found {len(catalog.df)} items")
        return catalog

    def run(self, generator: BaseGenerator):
        total_files = 0
        start = datetime.now()

        catalog = self.open_catalog(self.uri, self.intake_kwargs)

        if self.search_kwargs:
            catalog = self.open_catalog(catalog, self.search_kwargs)

        count = 0
        for _, row in catalog.df.iterrows():
            if count > self.skip:
                uri = getattr(row, self.object_attr)

                if self.should_process(uri):
                    generator.process(uri)
                    LOGGER.debug(f"Input processing: {uri}")
                else:
                    LOGGER.debug(f"Input skipping: {uri}")

                total_files += 1

            count += 1

        end = datetime.now()
        print(f"Processed {total_files} files from {self.uri} in {end-start}")
