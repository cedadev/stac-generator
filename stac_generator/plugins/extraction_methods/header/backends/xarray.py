# encoding: utf-8
"""
Collection of functions which can be used to extract metadata from file headers
"""
__author__ = "Richard Smith"
__date__ = "27 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import xarray as xr
from xarray.backends.plugins import guess_engine


class XarrayBackend:
    """
    Xarray
    ------

    Backend Name: ``Xarray``

    Description:
        Takes an input string and returns a boolean on whether this
        backend can open that file.
    """

    def guess_can_open(self, filepath: str) -> bool:
        """Return a boolean on whether this backend can open that file."""
        try:
            self.engine = guess_engine(filepath)
            return True
        except ValueError:
            return False

    def attr_extraction(
        self, body: dict, attributes: list, backend_kwargs: dict
    ) -> dict:
        """
        Takes a dictionary and list of attributes and extracts the metadata.

        :param body: current extracted properties
        :param attributes: attributes to extract
        :param kwargs: kwargs to send to xarray.open_dataset(). e.g. engine to
        specify different engines to use with grib data.

        :return: Dictionary of extracted attributes
        """

        ds = xr.open_dataset(body["uri"], engine=self.engine, **backend_kwargs)

        extracted_metadata = {}
        for attr in attributes:

            value = ds.attrs.get(attr)
            if value:
                extracted_metadata[attr] = value

        return body | extracted_metadata
