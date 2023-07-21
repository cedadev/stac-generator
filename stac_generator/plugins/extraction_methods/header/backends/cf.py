# encoding: utf-8
"""
Collection of functions which can be used to extract metadata from file headers
"""
__author__ = "Richard Smith"
__date__ = "27 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import cf
from cf.read_write.read import file_type


class CfBackend:
    """
    Cf
    ------

    Backend Name: ``Cf``

    Description:
        Takes an input string and returns a boolean on whether this
        backend can open that file.
    """

    def guess_can_open(self, filepath: str) -> bool:
        """Return a boolean on whether this backend can open that file."""
        try:
            file_type(filepath)
            return True
        except IOError:
            return False

    def attr_extraction(
        self, body: dict, attributes: list, backend_kwargs: dict
    ) -> dict:
        """
        Takes a dictionary and list of attributes and extracts the metadata.

        :param body: current extracted properties
        :param attributes: attributes to extract
        :param kwargs: kwargs to send to cf.read().

        :return: Dictionary of extracted attributes
        """

        field_list = cf.read(body["uri"], **backend_kwargs)

        properties = {}
        for field in field_list:
            properties.update(field.properties())
            if field.nc_global_attributes():
                properties["global_attributes"] = field.nc_global_attributes()

        extracted_metadata = {}
        for attr in attributes:
            if (
                "global_attributes" in properties
                and properties["global_attributes"][attr]
            ):
                extracted_metadata[attr] = properties["global_attributes"][attr]
            elif attr in properties:
                extracted_metadata[attr] = properties[attr]

        return body | extracted_metadata
