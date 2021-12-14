# encoding: utf-8
"""
Pre processors operate on the input arguments for the main processor.

They can be used to manipuate the input arguments for a given processor to
modify its behaviour.
"""
__author__ = "Richard Smith"
__date__ = "11 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import abc
import logging
import os
from string import Template

# Third party imports
import requests

# Package imports
from asset_scanner.core.processor import BaseProcessor

LOGGER = logging.getLogger(__name__)


class BasePreProcessor(BaseProcessor):
    @abc.abstractmethod
    def run(self, filepath: str, source_media: str = "POSIX", **kwargs) -> dict:
        pass


class ReducePathtoName(BasePreProcessor):
    """

    Processor Name: ``filename_reducer``

    Description:
        Takes a file path and returns the filename using `os.path.basename`.

    Example Configuration:

    .. code-block:: yaml

          pre_processors:
            - name: filename_reducer

    """

    def run(self, filepath: str, source_media: str = "POSIX", **kwargs):

        filepath = os.path.basename(filepath)

        LOGGER.info(f"Identified file name: {filepath}")

        return (filepath, source_media), kwargs


class CEDAObservation(BasePreProcessor):
    """

    Processor Name: ``ceda_observation``

    Description:
        Takes a file path and returns the ceda observation record.

    Configuration Options:
        - ``url_template``: ``REQUIRED`` URL string template to build url.
          Template uses the `python string template <https://docs.python.org/3/library/string.html#template-strings>`_ format.

    Example Configuration:

        .. code-block:: yaml

              pre_processors:
                - name: ceda_observation
                  inputs:
                    url_template: http://api.catalogue.ceda.ac.uk/api/v0/obs/get_info$filepath

    """

    def run(self, filepath: str, source_media: str = "POSIX", **kwargs):

        url = Template(self.url_template).substitute(filepath=filepath)

        r = requests.get(url)

        if r.status_code == 200:
            response = r.json()
            record_type = response.get("record_type")
            url = response.get("url")

            if record_type == "Dataset" and url:
                uuid = url.split("/")[-1]
                kwargs["uuid"] = uuid

        return (filepath, source_media), kwargs
