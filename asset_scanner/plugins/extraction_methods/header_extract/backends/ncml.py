# encoding: utf-8
"""
Metadata extraction backend for NcML (XML) description files.
"""
__author__ = "David Huard"
__date__ = "June 2022"
__copyright__ = "Copyright 2022 Ouranos"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "huard.david@ouranos.ca"

# Note that some of the XML parsing functions below are not used at the moment, but included for future reference.

from typing import List

import requests.exceptions
from lxml.etree import XMLParser, fromstring, Element

# NcML namespace
NS = {"ncml": "http://www.unidata.ucar.edu/namespaces/netcdf/ncml-2.2"}


class NcMLBackend:
    """
    NcML
    ----

    Backend Name: ``NcML``
    """

    def guess_can_open(self, filepath: str) -> bool:
        """Return a boolean on whether this backend can open that file."""
        try:
            get_ncml(filepath)
            return True
        except requests.exceptions.HTTPError:
            return False

    def attr_extraction(self, file: str, attributes: List, **kwargs) -> dict:
        """
        Takes a filepath and list of attributes and extracts the metadata.

        :param file: file-like object
        :param attributes: attributes to extract
        :param kwargs: {}

        :return: Dictionary of extracted attributes
        """
        # Send GET request to server for the THREDDS NCML response
        content = get_ncml(file)

        # Convert response to an XML etree.Element
        elem = to_element(content)

        extracted_metadata = {}
        for attr in attributes:
            # xpath expression to parse XML and extract attribute
            expr = attribute(attr)

            # Execute xpath expression
            value = elem.xpath(expr, namespaces=NS)

            if value:
                extracted_metadata[attr] = value[0]

        return extracted_metadata


def get_ncml(url: str, catalog: str = None, dataset: str = None) -> bytes:
    """Read NcML response from server.

    Providing the catalog and dataset reproduces the NcML response we get when we click on the NcML service on THREDDS.

    Parameters
    ----------
    url : str
      Link to NcML service of dataset hosted on a THREDDS server.
    catalog : str
      Link to catalog storing the dataset.
    dataset : str
      Relative link to the dataset.

    Returns
    -------
    bytes
      NcML content
    """
    import requests

    # For some reason, this is required to obtain the "THREDDSMetadata" group and the available services.
    # Note that the OPENDAP link would have been available from the top "location" attribute.
    params = {}
    if catalog:
        params["catalog"] = catalog
    if dataset:
        params["dataset"] = dataset

    r = requests.get(url, params=params)
    # logger.info(r.url)
    r.raise_for_status()
    return r.content


def to_element(content: bytes) -> Element:
    """Parse NcML file into XML node."""

    # Parse XML content - UTF-8 encoded documents need to be read as bytes
    parser = XMLParser(encoding='UTF-8')
    return fromstring(content, parser=parser)


def attribute(name: str) -> str:
    """Return xpath expression for global NcML attributes."""
    return f"//ncml:attribute[@name='{name}']/@value"


def varattr(name: str) -> str:
    """Return xpath expression for NcML variable attributes."""
    return f"./ncml:attribute[@name='{name}']/@value"


def dimlen(name: str) -> str:
    """Return xpath expression for NcML dimension length"""
    return f"./ncml:dimension[@name='{name}']/@length"


def get_variables(elem: Element) -> Element:
    """Return <variable> nodes that are not coordinates.

    Parameters
    ----------
    elem : lxml.etree.Element
      <ncml:netcdf> element.
    """

    # Get bounds
    bexpr = "./ncml:variable[ncml:attribute[@name='_CoordinateAxisType']]/ncml:attribute[@name='bounds']/@value"
    bounds = elem.xpath(bexpr, namespaces=NS)

    # Filter variables that are not coordinates
    vexpr = "./ncml:variable[not(ncml:attribute[@name='_CoordinateAxisType'])]"
    elements = elem.xpath(vexpr, namespaces=NS)

    # Get dimension names
    dexpr = "./ncml:dimension/@name"
    dimensions = elem.xpath(dexpr, namespaces=NS)

    exclude = bounds + dimensions
    return [el for el in elements if el.xpath("@name")[0] not in exclude]
