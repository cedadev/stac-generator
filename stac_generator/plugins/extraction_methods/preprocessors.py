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

import logging
import os
from string import Template

# Third party imports
import requests

# Package imports
from stac_generator.core.processor import BasePreProcessor

LOGGER = logging.getLogger(__name__)


class ReducePathtoName(BasePreProcessor):
    """

    Processor Name: ``filename_reducer``

    Description:
        Takes a file path and returns the filename using `os.path.basename`.

    Example Configuration:

    .. code-block:: yaml

          pre_processors:
            - method: filename_reducer

    """

    def run(self, uri: str, **kwargs):

        uri = os.path.basename(uri)

        LOGGER.info(f"Identified file name: {uri}")

        return uri, kwargs


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
                - method: ceda_observation
                  inputs:
                    url_template: http://api.catalogue.ceda.ac.uk/api/v0/obs/get_info$uri

    """

    def run(self, uri: str, **kwargs):

        url = Template(self.url_template).substitute(uri=uri)

        r = requests.get(url)

        if r.status_code == 200:
            response = r.json()
            record_type = response.get("record_type")
            url = response.get("url")

            if record_type == "Dataset" and url:
                uuid = url.split("/")[-1]
                kwargs["uuid"] = uuid

        return uri, kwargs
