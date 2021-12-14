# encoding: utf-8
"""
Collection of functions which can be used to extract metadata from file headers
"""
__author__ = "Richard Smith"
__date__ = "27 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import logging
from functools import lru_cache
from typing import Dict, List

import pkg_resources as pkg

from asset_scanner.core.decorators import accepts_postprocessors
from asset_scanner.core.processor import BaseProcessor
from asset_scanner.plugins.extraction_methods.mixins import PropertiesOutputKeyMixin

LOGGER = logging.getLogger(__name__)


class NoSuitableBackendException(Exception):
    """Returned when backend cannot be found for file"""

    ...


class HeaderExtract(PropertiesOutputKeyMixin, BaseProcessor):
    """

    .. list-table::

        * - Processor Name
          - ``header_extract``
        * - Accepts Pre-processors
          - .. fa:: times
        * - Accepts Post-processors
          - .. fa:: check

    Description:
        Takes a filepath string and a list of attributes
        and returns a dictionary of the values extracted from the
        file header.

    Configuration Options:
        - ``attributes``: A list of attributes to match for from the file header
        - ``post_processors``: List of post_processors to apply
        - ``output_key``: When the metadata is returned, this key determines
          where the metadata is fit in the response. Dot separated
          strings can be used to created nested attributes.
          ``default: 'properties'``

    Example configuration:
        .. code-block:: yaml

            - name: header_extract
              inputs:
                attributes:
                    - institution
                    - sensor
                    - platform


    """

    @accepts_postprocessors
    def run(self, filepath: str, source_media: str = "POSIX", **kwargs) -> dict:

        try:
            backend = self.guess_backend(filepath)
        except NoSuitableBackendException:
            LOGGER.warning(f"Header extract backend not found for {filepath}")
            return {}

        # Use the handler to extract the desired attributes from the header
        data = self.attr_extraction(backend, filepath, self.attributes)

        return data

    @staticmethod
    @lru_cache(maxsize=1)
    def list_backend() -> Dict:
        backend_entrypoints = {}
        for pkg_ep in pkg.iter_entry_points(
            "asset_scanner.extraction_methods.header_extract.backends"
        ):
            name = pkg_ep.name
            try:
                backend = pkg_ep.load()
                backend_entrypoints[name] = backend
            except Exception as ex:
                LOGGER.warning(ex)
        return backend_entrypoints

    def guess_backend(self, filepath: str) -> Dict:
        backends = self.list_backend()
        for engine, backend in backends.items():
            backend = backend()
            if backend.guess_can_open(filepath):
                return backend

        raise (NoSuitableBackendException(f"No backend found for file {filepath}"))

    @staticmethod
    def attr_extraction(backend, file: str, attributes: List) -> dict:
        """
        Takes a filepath and list of attributes and extracts the metadata from the header.

        :param file: file-like object
        :param attributes: Header attributes to extract
        :param kwargs: kwargs to send to xarray.open_dataset(). e.g. engine to
        specify different engines to use with grib data.

        :return: Dictionary of extracted attributes
        """

        return backend.attr_extraction(file, attributes)
