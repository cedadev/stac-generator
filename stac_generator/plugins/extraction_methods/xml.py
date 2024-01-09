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

import logging

# Python imports
from collections import defaultdict
from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError

from stac_generator.core.extraction_method import BaseExtractionMethod

# Package imports


LOGGER = logging.getLogger(__name__)


class XMLExtract(BaseExtractionMethod):
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

    def run(self, body: dict, **kwargs) -> dict:
        # Extract the keys
        try:
            if isinstance(body[self.input_term], str):
                xml_file = ElementTree.parse(body[self.input_term])

            else:
                xml_file = ElementTree.XML(body[self.input_term])

        except (ParseError, FileNotFoundError, TypeError):
            return body

        output = defaultdict(list)

        for key in self.extraction_keys:
            values = xml_file.findall(key["key"], self.namespaces)

            for value in values:
                if value is not None:
                    attribute = key.get("attribute")

                    if attribute:
                        v = value.get(attribute, "")

                    else:
                        v = value.text

                    if v and v not in output[key["name"]]:
                        output[key["name"]].append(v.strip())

            if output[key["name"]] and len(output[key["name"]]) == 1:
                output[key["name"]] = output[key["name"]][0]

            if not output[key["name"]]:
                output[key["name"]] = None

        body |= output

        return body
