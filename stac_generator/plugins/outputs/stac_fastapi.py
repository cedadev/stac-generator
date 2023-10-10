# encoding: utf-8
"""
Elasticsearch
-------------

An output backend which outputs the content generated to elasticsearch
using the Elasticsearch API

**Plugin name:** ``elasticsearch``

.. list-table::
    :header-rows: 1

    * - Option
      - Value Type
      - Description
    * - ``connection_kwargs``
      - ``dict``
      - ``REQUIRED`` Connection kwargs passed to the `elasticsearch client  <https://elasticsearch-py.readthedocs.io/en/latest/api.html#elasticsearch>`_
    * - ``index.name``
      - ``str``
      - ``REQUIRED`` The index to output the content.
    * - ``index.mapping``
      - ``str``
      - Path to a yaml file which defines the mapping for the index

Example Configuration:
    .. code-block:: yaml

        outputs:
            - method: elasticsearch
              connection_kwargs:
                hosts: ['host1','host2']
              index:
                name: 'assets-2021-06-02'
"""
__author__ = "Richard Smith"
__date__ = "01 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import requests
from urllib.parse import urljoin

from stac_generator.core.output import BaseOutput


class STACFastAPIOutput(BaseOutput):
    """
    Connects to an elasticsearch instance and exports the
    documents to elasticsearch.

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, "verify"):
          self.verify = True

    def export(self, data: dict, **kwargs) -> None:

        collections = data["collection"]

        if isinstance(data["collection"], str):
            collections = [collections]

        for collection in collections:

            response = requests.post(
                urljoin(self.api_url, f"collections/{collection}/items"), json=data, verify=self.verify
            )

            if response.status_code == 404:
                response_json = response.json()

                if response_json["description"] == f"Collection {collection} does not exist":
                    collection = {
                        "type": "Collection",
                        "id": collection,
                    }

                    response = requests.post(
                        urljoin(self.api_url, f"collections"), json=collection, verify=self.verify
                    )

                    response = requests.post(
                        urljoin(self.api_url, f"collections/{collection}/items"), json=data, verify=self.verify
                    )
