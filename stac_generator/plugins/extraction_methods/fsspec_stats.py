# encoding: utf-8
"""
..  _regex:

Regex
------
"""
__author__ = "Richard Smith"
__date__ = "27 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import logging

# Python imports
import os
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

# Third-party imports
import fsspec as fs

from stac_generator.core.decorators import (
    accepts_output_key,
    accepts_postprocessors,
    accepts_preprocessors,
    expected_terms_postprocessors,
)

LOGGER = logging.getLogger(__name__)


class FsSpecStatsExtract:
    """

    .. list-table::

        * - Processor Name
          - ``object_store_stats``
        * - Accepts Pre-processors
          - .. fa:: check
        * - Accepts Post-processors
          - .. fa:: check

    Description:
        Takes an input uri and returns a dictionary of file level stats.

    Configuration Options:
        - ``uri_parse``: The uri parser
        - ``pre_processors``: List of pre-processors to apply
        - ``post_processors``: List of post_processors to apply
        - ``output_key``: When the metadata is returned, this key determines
          where the metadata is fit in the response. Dot separated
          strings can be used to created nested attributes. An empty string can
          be used to return the output with no prefix.
          ``default: 'properties'``


    Example configuration:
        .. code-block:: yaml

            - method: object_store_stats
              inputs:
                uri_parse: urlparse

    """

    def extract_stat(self, name: str, stats: dict, attribute: str) -> None:
        """
        Trys to retrieve the named attribute

        :param name: Name of the returned stat
        :param stats: Output from self.client.head_object
        :param attribute: The name of the attribute to return
        """
        try:
            value = stats.get(attribute)
            if value:
                self.info[name] = value
        except Exception as e:
            LOGGER.debug(e)

    def extract_filename(self, path: str) -> None:
        try:
            self.info["filename"] = os.path.basename(path)
        except Exception as e:
            LOGGER.debug(e)

    def extract_extension(self, path: str) -> None:
        try:
            if os.path.splitext(path)[1] != "":
                self.info["extension"] = os.path.splitext(path)[1]
        except Exception as e:
            LOGGER.debug(e)

    def extract_checksum(self, stats: dict, checksum: Optional[str] = None) -> None:
        # Check if the checksum is the right length for md5 (32 chars)
        if checksum and len(checksum) != 32:
            checksum = None

        if not checksum:
            try:
                checksum = stats.get("ETag")
            except Exception as e:
                LOGGER.debug(e)
                return

        # Assuming no errors we can now store the checksum
        if checksum:
            self.info["checksum"] = checksum

    @accepts_output_key
    @accepts_preprocessors
    @accepts_postprocessors
    def run(self, uri: str, **kwargs) -> dict:
        """

        :param uri:
        :param kwargs:
        :return:

        """

        LOGGER.debug(
            "OS stats: Extracting metadata for: %s with checksum: %s",
            uri,
            getattr(self, "checksum", None),
        )

        if not hasattr(self, "uri_parse"):
            uri_parse = urlparse(uri)

        url_path = Path(uri_parse.path)
        self.object_path = "/".join(url_path.parts[2:])

        self.info = {"uri": uri}

        try:
            with fs.open(uri, anon=True) as f:
                stats = vars(f)

            self.extract_filename(self.object_path)
            self.extract_extension(self.object_path)
            self.extract_stat("size", stats, "size")
            self.extract_stat("modified_time", stats, "last_modified")
            self.extract_stat("magic_number", stats, "content_type")
            # self.extract_checksum(stats, self.checksum)
        except Exception:
            pass

        return self.info

    @expected_terms_postprocessors
    def expected_terms(self, **kwargs) -> list:
        """
        The expected terms to be returned from running the extraction method with the given Collection Description
        :param collection_descrition: CollectionDescription for extraction method
        :param kwargs: free kwargs passed to the processor.
        :return: list
        """

        return ["uri", "filename", "extension", "size", "modified_time", "magic_number"]
