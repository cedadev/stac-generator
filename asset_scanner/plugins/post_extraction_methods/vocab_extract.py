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


# Python imports
import json
import logging

import requests

from asset_scanner.core.decorators import accepts_postprocessors, accepts_preprocessors
from asset_scanner.core.processor import BaseProcessor

LOGGER = logging.getLogger(__name__)


class VocabExtract(BaseProcessor):
    """

    .. list-table::

        * - Processor Name
          - ``vocab``
        * - Accepts Pre-processors
          - .. fa:: check
        * - Accepts Post-processors
          - .. fa:: check

    Description:
        Validates and sorts properties into vocabs and generates
        the `general` vocab for specified properties.

    Configuration Options:
        - ``namespace``: namespace of vocab for terms
        - ``terms``: Terms to be sorted
        - ``strict``: Boolean on whether values should be validated
        - ``pre_processors``: List of pre-processors to apply
        - ``post_processors``: List of post_processors to apply

    Example configuration:
        .. code-block:: yaml

          - method: vocab
            inputs:
              url: vocab.ceda.ac.uk
              namespace: cmip6
              strict: False
              terms:
                  - start_time
                  - model

    """

    @accepts_preprocessors
    @accepts_postprocessors
    def run(
        self,
        body: dict,
        **kwargs,
    ) -> dict:

        properties = body["properties"]

        # if there is already an unspecified_vocab it is not the first vocab
        first = True
        if "unspecified_vocab" in properties:
            properties = properties["unspecified_vocab"]
            first = False

        req_data = {
            "namespace": self.namespace,
            "terms": self.terms,
            "properties": properties,
            "strict": self.strict,
        }

        response = requests.post(self.url, data=json.dumps(req_data))

        if response.status_code != 200:
            raise Exception(
                f"Bad response from vocab server: {response.status_code}, reason: {response.reason}"
            )

        json_response = response.json()

        if json_response["error"]:
            raise Exception(f"Vocab request failed, reason: {json_response['reason']}")

        if not first:
            new_properties = properties | json_response["result"]
            vocabs = body["vocabs"] + [self.namespace]

        else:
            new_properties = json_response["result"]
            vocabs = [self.namespace]

        body = body | {"vocabs": vocabs, "properties": new_properties}

        return body
