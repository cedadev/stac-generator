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

import pkg_resources as pkg

from stac_generator.core.decorators import (
    BaseExtractionMethod_postprocessors,
    accepts_postprocessors,
)
from stac_generator.core.extraction_method import BaseExtractionMethod

LOGGER = logging.getLogger(__name__)


class NoSuitableBackendException(Exception):
    """Returned when backend cannot be found for file"""

    ...


class HeaderExtract(BaseExtractionMethod):
    """

    .. list-table::

        * - Processor Name
          - ``header``

    Description:
        Takes a uri string and a list of attributes
        and returns a dictionary of the values extracted from the
        file header.

    Configuration Options:
        - ``attributes``: A list of attributes to match for from the file header
        - ``backend``: Specify which backend
        - ``backend_kwargs``: A dictionary of kwargs for the extractor

    Example configuration:
        .. code-block:: yaml

            - method: header
              inputs:
                attributes:
                  - institution
                  - sensor
                  - platform
                backend: xarray
                backend_kwargs:
                  decode_times: False

    """

    def run(self, body: dict, **kwargs) -> dict:
        try:
            backend = self.guess_backend(body["uri"])
        except NoSuitableBackendException:
            LOGGER.warning(f"Header extract backend not found for {body['uri']}")
            return {}

        # Use the handler to extract the desired attributes from the header
        body = self.attr_extraction(backend, body, self.attributes, self.backend_kwargs)

        return body

    @staticmethod
    @lru_cache(maxsize=1)
    def list_backend() -> dict:
        backend_entrypoints = {}
        for pkg_ep in pkg.iter_entry_points(
            "stac_generator.extraction_methods.header.backends"
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
            entry_points = pkg.iter_entry_points(
                "stac_generator.extraction_methods.header.backends",
                self.backend,
            )

            entry_points = list(entry_points)
            backend = None
            if len(entry_points) > 0:
                backend = entry_points[0].load()

            if backend and backend().guess_can_open(uri):
                backend = backend()
                backend.guess_can_open(uri)
                return backend

        backends = self.list_backend()
        for _, backend in backends.items():
            if backend().guess_can_open(uri):
                return backend

        raise (NoSuitableBackendException(f"No backend found for file {uri}"))

    @staticmethod
    def attr_extraction(
        backend, body: dict, attributes: list, backend_kwargs: dict
    ) -> dict:
        """
        Takes a uri and list of attributes and extracts the metadata from the header.

        :param file: file-like object
        :param attributes: Header attributes to extract
        :param kwargs: kwargs to send to xarray.open_dataset(). e.g. engine to
        specify different engines to use with grib data.

        :return: dictionary of extracted attributes
        """

        return backend.attr_extraction(body, attributes, backend_kwargs)
