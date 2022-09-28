# encoding: utf-8
"""
Collection of functions which can be used to extract file stats information
"""
__author__ = "Richard Smith"
__date__ = "27 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import logging
from functools import lru_cache

import pkg_resources as pkg

from stac_generator.core.decorators import (
    accepts_postprocessors,
    expected_terms_postprocessors,
)
from stac_generator.core.processor import BaseExtractionMethod

LOGGER = logging.getLogger(__name__)


class NoSuitableBackendException(Exception):
    """Returned when backend cannot be found for file"""

    ...


class FileStatsExtract(BaseExtractionMethod):
    """

    .. list-table::

        * - Processor Name
          - ``file_stats``
        * - Accepts Pre-processors
          - .. fa:: times
        * - Accepts Post-processors
          - .. fa:: check

    Description:
        Takes a uri string and returns a dictionary of
        the file stats extracted.

    Configuration Options:
        - ``backend``: Specify which backend
        - ``backend_kwargs``: A dictionary of kwargs for the backend
        - ``post_processors``: List of post_processors to apply
        - ``output_key``: When the metadata is returned, this key determines
          where the metadata is fit in the response. Dot separated
          strings can be used to created nested attributes.
          ``default: 'properties'``

    Example configuration:
        .. code-block:: yaml

            - method: file_stats
              inputs:
                backend: os

    """

    @accepts_postprocessors
    def run(self, uri: str, **kwargs) -> dict:

        backend_kwargs = getattr(self, "backend_kwargs", {})

        try:
            backend = self.guess_backend(uri, **backend_kwargs)
        except NoSuitableBackendException:
            LOGGER.warning(f"File stat extract backend not found for {uri}")
            return {}

        # Use the handler to extract the desired attributes from the header
        data = backend.run(uri, **backend_kwargs)

        return data

    @staticmethod
    @lru_cache(maxsize=1)
    def list_backend() -> dict:
        backend_entrypoints = {}
        for pkg_ep in pkg.iter_entry_points(
            "stac_generator.extraction_methods.file_stats.backends"
        ):
            name = pkg_ep.name
            try:
                backend = pkg_ep.load()
                backend_entrypoints[name] = backend
            except Exception as ex:
                LOGGER.warning(ex)
        return backend_entrypoints

    def guess_backend(self, uri: str) -> dict:

        if hasattr(self, "backend"):
            entry_points = list(
                pkg.iter_entry_points(
                    "stac_generator.extraction_methods.file_stats.backends",
                    self.backend,
                )
            )

            backend = None
            if len(entry_points) > 0:
                backend = entry_points[0].load()
                print(backend)

            if backend and backend().guess_can_open(uri):
                return backend

        backends = self.list_backend()
        for _, backend in backends.items():

            if backend().guess_can_open(uri):
                return backend

        raise (NoSuitableBackendException(f"No backend found for file {uri}"))

    @expected_terms_postprocessors
    def expected_terms(self, **kwargs) -> list:
        """
        The expected terms to be returned from running the extraction method with the given Collection Description
        :param collection_descrition: CollectionDescription for extraction method
        :param kwargs: free kwargs passed to the processor.
        :return: list
        """

        return ["uri", "filename", "extension", "size", "modified_time", "magic_number"]
