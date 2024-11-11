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
            - name: intake_esm
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
from extraction_methods.core.extraction_method import KeyOutputKey
from pydantic import BaseModel, Field

# Package imports
from stac_generator.core.input import Input

LOGGER = logging.getLogger(__name__)


class IntakeESMConf(BaseModel):
    """IntakeESM config."""

    url: str = Field(
        description="URL of datastore.",
    )
    uri_term: str = Field(
        description="Attritube to use as uri.",
    )
    extra_terms: list[KeyOutputKey] = Field(
        default=[],
        description="List of extra attributes.",
    )
    skip: int = Field(
        default=-1,
        description="Number of rows to skip.",
    )
    catalog_kwargs: dict = Field(
        default={},
        description="catalog kwargs.",
    )
    search_kwargs: dict = Field(
        default={},
        description="search kwargs.",
    )


class IntakeESMInput(Input):
    """
    Performs an os.walk to provide a stream of paths for procesing.
    """

    config_class = IntakeESMConf

    def run(self):
        total_files = 0
        start = datetime.now()

        LOGGER.info("Opening catalog %s", self.conf.url)
        catalog = intake.open_esm_datastore(self.conf.url, **self.conf.catalog_kwargs)

        if self.conf.search_kwargs:
            LOGGER.info("Searching catalog")
            catalog = catalog.search(**self.conf.search_kwargs)

        LOGGER.info("Found %s items", len(catalog.df))

        count = 0
        for _, row in catalog.df.iterrows():
            if count > self.conf.skip:
                output = {"uri": getattr(row, self.conf.uri_term)}
                LOGGER.debug("Input processing: %s", output["uri"])

                for extra_term in self.conf.extra_terms:
                    output[extra_term.output_key] = getattr(row, extra_term.key)

                yield output
                total_files += 1

            count += 1

        end = datetime.now()
        print(f"Processed {total_files} files from {self.conf.url} in {end-start}")
