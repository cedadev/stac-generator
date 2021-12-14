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
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import ParseError

# Package imports
from asset_scanner.core.decorators import accepts_postprocessors, accepts_preprocessors
from asset_scanner.core.processor import BaseProcessor

from .mixins import PropertiesOutputKeyMixin

LOGGER = logging.getLogger(__name__)


class XMLExtract(PropertiesOutputKeyMixin, BaseProcessor):
    """
    .. list-table::

        * - Processor Name
          - ``xml_extract``
        * - Accepts Pre-processors
          - .. fa:: check
        * - Accepts Post-processors
          - .. fa:: check

    Description:
        Processes XML documents to extract metadata

    Configuration Options:
        - ``extraction_keys``: List of keys to retrieve from the document.
        - ``filter_expr``: Regex to match against files to limit the attempts to known files
        - ``namespaces``: Map of namespaces
        - ``pre_processors``: List of pre-processors to apply
        - ``post_processors``: List of post_processors to apply
        - ``output_key``: When the metadata is returned, this key determines
          where the metadata is fit in the response. Dot separated
          strings can be used to created nested attributes.
          ``default: 'properties'``

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

                  - name: start_datetime
                    key: './/gml:beginPosition'

    Example configuration:
        .. code-block:: yaml

            - name: xml_extract
              inputs:
                filter_expr: '\.manifest$'
                extraction_keys:
                  - name: start_datetime
                    key: './/gml:beginPosition'
    """

    @accepts_preprocessors
    @accepts_postprocessors
    def run(self, filepath: str, source_media: str = "POSIX", **kwargs) -> dict:

        # Extract the keys
        metadata = {}

        try:
            xml_file = ET.parse(filepath)
        except ParseError:
            return {}

        for key in self.extraction_keys:
            name = key["name"]
            location = key["key"]
            attribute = key.get("attribute")

            value = xml_file.find(location, self.namespaces)
            if value is not None:
                if attribute:
                    v = value.get(attribute, "")
                else:
                    v = value.text
                metadata[name] = v

        return metadata


if __name__ == "__main__":
    kwargs = {
        "filter_expr": "\.manifest$",
        "extraction_keys": [
            {"name": "instrument", "key": ".//safe:instrument/safe:familyName"},
            {
                "name": "short_instrument",
                "key": ".//safe:instrument/safe:familyName",
                "attribute": "abbreviation",
            },
        ],
        "namespaces": {
            "ns0": "http://www.w3.org/2001/XMLSchema-instance",
            "gml": "http://www.opengis.net/gml",
            "xfdu": "urn:ccsds:schema:xfdu:1",
            "safe": "http://www.esa.int/safe/sentinel-1.0",
            "s1": "http://www.esa.int/safe/sentinel-1.0/sentinel-1",
            "s1sar": "http://www.esa.int/safe/sentinel-1.0/sentinel-1/sar",
            "s1sarl1": "http://www.esa.int/safe/sentinel-1.0/sentinel-1/sar/level-1",
            "s1sarl2": "http://www.esa.int/safe/sentinel-1.0/sentinel-1/sar/level-2",
            "gx": "http://www.google.com/kml/ext/2.2",
        },
    }

    xe = XMLExtract(**kwargs)
    metadata = xe.run(
        "/neodc/sentinel1a/data/IW/L1_SLC/IPF_v2/2014/10/03/S1A_IW_SLC__1SDV_20141003T165117_20141003T165146_002668_002F8B_79FE.manifest"
    )
    print(metadata)
    # metadata = xe.run('/neodc/sentinel1a/data/IW/L1_SLC/IPF_v2/2014/10/03/S1A_IW_SLC__1SDV_20141003T165117_20141003T165146_002668_002F8B_79FE_checksum')
    # print(metadata)
