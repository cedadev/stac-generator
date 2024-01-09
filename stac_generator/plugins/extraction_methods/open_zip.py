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
import tempfile
import zipfile

from stac_generator.core.extraction_method import BaseExtractionMethod

# Package imports


LOGGER = logging.getLogger(__name__)


class ZipExtract(BaseExtractionMethod):
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

        if not hasattr(self, "output_key"):
            self.output_key = "zip_file"

        if not hasattr(self, "inner_file"):
            self.inner_file = ""

        if not hasattr(self, "zip_file"):
            self.zip_file = "uri"

    def run(self, body: dict, **kwargs) -> dict:
        # Extract the keys
        self.body = body
        try:
            if self.zip_file[0] == self.exists_key:
                self.zip_file = body[self.zip_file[1:]]

            if self.inner_file[0] == self.exists_key:
                self.inner_file = body[self.inner_file[1:]]

            with zipfile.ZipFile(self.zip_file) as z:
                if self.inner_file:
                    file_obj = z.read(self.inner_file)
                else:
                    file_obj = z.read()

        except FileNotFoundError:
            # return body
            file_obj = tempfile.TemporaryFile()

        body[self.output_key] = file_obj

        return body
