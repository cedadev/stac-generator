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
import boto3
import fsspec as fs
from botocore import UNSIGNED
from botocore.config import Config
from botocore.exceptions import ClientError

from stac_generator.core.decorators import accepts_postprocessors, accepts_preprocessors
from stac_generator.core.processor import BaseProcessor
from stac_generator.core.utils import Stats

# Package imports
from .mixins import PropertiesOutputKeyMixin

LOGGER = logging.getLogger(__name__)


class ObjectStoreStatsExtract(PropertiesOutputKeyMixin, BaseProcessor):
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        session_kwargs = getattr(self.conf, "session_kwargs", {})
        self.session = boto3.session.Session(**session_kwargs)
        self.anonymous = not session_kwargs

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

    @accepts_preprocessors
    @accepts_postprocessors
    def run(self, uri: str, **kwargs) -> dict:
        """

        :param uri:
        :param kwargs:
        :return:

        """

        LOGGER.info(f"Extracting metadata for: {uri} with checksum: {self.checksum}")

        uri_parse = kwargs.get("uri_parse")
        if not uri_parse:
            uri_parse = urlparse(uri)

        endpoint_url = f"{uri_parse.scheme}://{uri_parse.netloc}"
        url_path = Path(uri_parse.path)
        bucket = url_path.parts[1]
        object_path = "/".join(url_path.parts[2:])
        protocol = uri_parse.scheme
        client_kwargs = {}
        if self.anonymous:
            client_kwargs["config"] = Config(signature_version=UNSIGNED)

        if protocol in ["https", "http"]:
            s3 = self.session.client("s3", endpoint_url=endpoint_url, **client_kwargs)
            try:
                stats = s3.head_object(Bucket=bucket, Key=uri)
            except ClientError:
                stats = {}
            stats = Stats.from_boto(stats)

        else:
            file = fs.open(f"{uri}", anon=True)
            with file as f:
                stats = vars(f)

        self.info["uri"] = uri
        self.extract_filename(object_path)
        self.extract_extension(object_path)
        self.extract_stat("size", stats, "size")
        self.extract_stat("mtime", stats, "last_modified")
        self.extract_stat("magic_number", stats, "content_type")
        self.extract_checksum(stats, self.checksum)

        return self.info
