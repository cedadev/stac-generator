# encoding: utf-8
"""
..  _iso19115-extract:

ISO 19115 Extract
------------------
"""
__author__ = "Richard Smith"
__date__ = "28 Jul 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

# Python imports
import logging
from string import Template
from xml.etree import ElementTree as ET

# Third party imports
import requests

# Package imports
from stac_generator.core.processor import BaseExtractionMethod

LOGGER = logging.getLogger(__name__)

iso19115_ns = {
    "gmd": "http://www.isotc211.org/2005/gmd",
    "gml": "http://www.opengis.net/gml/3.2",
    "gco": "http://www.isotc211.org/2005/gco",
    "gmx": "http://www.isotc211.org/2005/gmx",
    "srv": "http://www.isotc211.org/2005/srv",
    "xlink": "http://www.w3.org/1999/xlink",
}


class ISO19115Extract(BaseExtractionMethod):
    """
    .. list-table::

        * - Processor Name
          - ``iso19115``

    Description:
        Takes a URL template and calls out to URL to retrieve the
        iso19115 record. Use pre-processors to inject additional kwargs
        which are passed to the URL template.

    Configuration Options:
        - ``url_template``: ``REQUIRED`` String template to build the URL.
          Template uses the `python string template <https://docs.python.org/3/library/string.html#template-strings>`_ format.
        - ``extraction_keys``: List of keys to retrieve from the response.

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

        Example:
            .. code-block:: yaml

                  - method: start_datetime
                    key: './/gml:beginPosition'

    Example configuration:
        .. code-block:: yaml

            - method: iso19115
              inputs:
                url_template: 'api.catalogue.ceda.ac.uk/export/xml/$uri'
                extraction_keys:
                  - name: start_datetime
                    key: './/gml:beginPosition'
    """

    def run(self, uri: str, body: dict, **kwargs) -> dict:

        # Build the template
        url = Template(self.url_template)

        try:
            url = url.substitute(kwargs)
        except KeyError:
            LOGGER.warning(
                f"URL templating failed. Template: {self.url_template} key not found in kwargs: {uri}"
            )
            return {}

        # Retrieve the ISO 19115 record
        response = requests.get(url)

        if not response.status_code == 200:
            LOGGER.debug(f"Request {url} failed with response: {response.error}")
            return {}

        iso_record = ET.fromstring(response.text)

        # Extract the keys
        for key in self.extraction_keys:
            name = key["name"]
            location = key["key"]

            value = iso_record.find(location, iso19115_ns)

            if value is not None:
                body[name] = value.text

        return body
