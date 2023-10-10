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


import hashlib
import logging

# Python imports
import os
from datetime import datetime

import magic

from stac_generator.core.extraction_method import BaseExtractionMethod

LOGGER = logging.getLogger(__name__)


class OsStatsExtract(BaseExtractionMethod):
    """

    .. list-table::

        * - Processor Name
          - ``os_stats``

    Description:
        Takes an input filepath and returns a dictionary of file level stats.

    Configuration Options:


    Example configuration:
        .. code-block:: yaml

            - method: os_stats

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if not hasattr(self, "input_term"):
            self.input_term = "uri"

    def extract_stat(self, name: str, stats: os.stat_result, attribute: str) -> None:
        """
        Trys to retrieve the named attribute

        :param name: Name of the returned stat
        :param stats: Output from os.stat
        :param attribute: The name of the attribute to return

        """
        try:
            self.info[name] = getattr(stats, attribute)
        except AttributeError as e:
            LOGGER.debug(e)

    def extract_modified_time(self, stats: os.stat_result):
        try:
            self.info["modified_time"] = datetime.fromtimestamp(
                stats.st_mtime
            ).isoformat()
        except Exception as e:
            LOGGER.debug(e)

    def extract_filename(self, path: str) -> None:
        try:
            self.info["filename"] = os.path.basename(path)
        except Exception as e:
            LOGGER.debug(e)

    def extract_extension(self, path: str) -> None:
        try:
            self.info["extension"] = os.path.splitext(path)[1]
        except Exception as e:
            LOGGER.debug(e)

    def extract_magic_number(self, path: str) -> None:
        try:
            self.info["magic_number"] = magic.from_file(path, mime=True)
        except Exception as e:
            LOGGER.debug(e)

    def extract_checksum(self, path: str, checksum: str) -> None:
        # Check if the checksum is the right length for md5 (32 chars)
        if checksum and len(checksum) != 32:
            checksum = None

        if not checksum:
            try:
                hash_md5 = hashlib.md5()
                with open(path, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_md5.update(chunk)
            except Exception as e:
                LOGGER.debug(e)
                return

            checksum = hash_md5.hexdigest()

        # Assuming no errors we can now store the checksum
        self.info["checksum"] = [{"time": datetime.now(), "checksum": checksum}]

    def run(self, body: dict, **kwargs) -> dict:
        """

        :param body:
        :param kwargs:
        :return:

        """

        uri = body[self.input_term]

        self.info = body

        if os.path.exists(uri):
            stats = os.stat(uri)

            self.extract_filename(uri)
            self.extract_extension(uri)
            self.extract_stat("size", stats, "st_size")
            self.extract_modified_time(stats)
            self.extract_magic_number(uri)
            # self.extract_checksum(uri, self.checksum)

        return self.info
