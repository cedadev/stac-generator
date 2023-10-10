# encoding: utf-8
"""
..  _xml-extract:

XML Extract
------------
"""
__author__ = "Richard Smith"
__date__ = "19 Aug 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

# Python imports
import logging
import os
from pathlib import Path
import xarray
import cf_xarray

from stac_generator.core.extraction_method import BaseExtractionMethod

# Package imports


LOGGER = logging.getLogger(__name__)


class NetCDFfExtract(BaseExtractionMethod):
    """
    .. list-table::

        * - Processor Name
          - ``xml``

    Description:
        Processes XML documents to extract metadata

    Configuration Options:
        - ``extraction_keys``: List of keys to retrieve from the document.
        - ``filter_expr``: Regex to match against files to limit the attempts to known files
        - ``namespaces``: Map of namespaces

    Extraction Keys:
        Extraction keys should be a map.

        .. list-table::

            * - Name
              - Description
            * - ``name``
              - Name of the outputted attribute
            * - ``key``
              - Access key to extract the required data. Passed to
                `xml.etree.ElementTree.find() <https://docs.python.org/3/library/xml.etree.elementtree.html?highlight=find#xml.etree.ElementTree.ElementTree.find>`_
                and also supports `xpath formatted <https://docs.python.org/3/library/xml.etree.elementtree.html#xpath-support>`_ accessors
            * - ``attribute``
              - Allows you to select from the element attribute. In the absence of this value, the default behaviour is to access the text value of the key.
                In some cases, you might want to access and attribute of the element.

        Example:
            .. code-block:: yaml

                  - method: start_datetime
                    key: './/gml:beginPosition'

    Example configuration:
        .. code-block:: yaml

            - method: xml
              inputs:
                filter_expr: '\.manifest$'
                extraction_keys:
                  - name: start_datetime
                    key: './/gml:beginPosition'
                    attribute: start

    # noqa: W605
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if not hasattr(self, "input_term"):
            self.input_term = "uri"

        if not hasattr(self, "exists_key"):
            self.exists_key = "$"

        if not hasattr(self, "variable_id"):
            self.variable_id = ""

        if not hasattr(self, "variable_terms"):
            self.variable_terms = []

        if not hasattr(self, "global_terms"):
            self.global_terms = []

        if not hasattr(self, "cf_terms"):
            self.cf_terms = []

    def run(self, body: dict, **kwargs) -> dict:
        # Extract the keys
        dataset = xarray.open_dataset(body[self.input_term])

        if self.variable_id:
            if self.variable_id[0] == self.exists_key:
                self.variable_id = body[self.variable_id[1:]]

            variable = dataset[self.variable_id]

            if self.variable_terms:
                variable_attributes = variable.attrs

                for variable_term in self.variable_terms:
                    name = variable_term.get("name")
                    key = variable_term.get("key", name)

                    body[name] = variable_attributes.get(key, None)

        if self.global_terms:
            global_attributes = dataset.attrs

            for global_term in self.global_terms:
                name = global_term.get("name")
                key = global_term.get("key", name)

                body[name] = global_attributes.get(key, None)

        if self.cf_terms:
            cf_attributes = dataset.cf

            for cf_term in self.cf_terms:
                name = cf_term.get("name")
                key = cf_term.get("key", name)

                body[name] = cf_attributes[key]

        return body
