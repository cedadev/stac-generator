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
from boto3.session import Session as BotoSession
from botocore import UNSIGNED
from botocore.config import Config

from stac_generator.core.processor import BaseExtractionMethod
from stac_generator.core.utils import Stats

LOGGER = logging.getLogger(__name__)


class BotoStatsExtract(BaseExtractionMethod):
    """

    .. list-table::

        * - Processor Name
          - ``object_store_stats``

    Description:
        Takes an input uri and returns a dictionary of file level stats.

    Configuration Options:
        - ``uri_parse``: The uri parser

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

    def run(self, body: dict, **kwargs) -> dict:
        """

        :param body:
        :param kwargs:
        :return:

        """

        LOGGER.debug(
            "OS stats: Extracting metadata for: %s with checksum: %s",
            body["uri"],
            getattr(self, "checksum", None),
        )

        if not hasattr(self, "uri_parse"):
            self.uri_parse = urlparse(body["uri"])

        endpoint_url = f"{self.uri_parse.scheme}://{self.uri_parse.netloc}"
        url_path = Path(self.uri_parse.path)
        bucket = url_path.parts[1]

        if endpoint_url == "://":
            return False

        self.object_path = "/".join(url_path.parts[2:])

        session_kwargs = getattr(kwargs, "session_kwargs", {})
        self.session = BotoSession(**session_kwargs)

        client_kwargs = {}
        if not session_kwargs:
            client_kwargs["config"] = Config(signature_version=UNSIGNED)

        s3 = self.session.client("s3", endpoint_url=endpoint_url, **client_kwargs)
        stats = s3.head_object(Bucket=bucket, Key=body["uri"])
        self.stats = Stats.from_boto(stats)

        self.info = body
        self.extract_filename(self.object_path)
        self.extract_extension(self.object_path)
        self.extract_stat("size", self.stats, "size")
        self.extract_stat("modified_time", self.stats, "last_modified")
        self.extract_stat("magic_number", self.stats, "content_type")
        # self.extract_checksum(stats, self.checksum)

        return self.info
