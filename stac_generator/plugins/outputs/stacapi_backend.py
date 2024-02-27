# encoding: utf-8
"""
STAC API backend
-------------

An output backend which outputs the content generated to STAC API.

**Plugin name:** ``stacapi``

.. list-table::
    :header-rows: 1

    * - Option
      - Value Type
      - Description
    * - ``connection.host``
      - ``REQUIRED`` STAC API URL
    * - ``collection.name``
      - ``str``
      - ``REQUIRED`` The collection name to output the content to.
    * - ``drop_properties``
      - List of properties to drop from item indexing

Example Configuration:
    .. code-block:: yaml

        outputs:
            - name: stacapi
              connection:
                host: 'hosturl'
              collection:
                name: 'CMIP6'
              drop_properties:
                - uri
                - extension
                - filename
"""
__author__ = "Mathieu Provencher"
__date__ = "20 Apr 2022"
__copyright__ = "Copyright 2022 Computer Research Institute of Montreal"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "mathieu.provencher@crim.ca"

import datetime
import hashlib
import os

import pystac
import pystac.extensions.eo
import requests
from shapely.geometry import Polygon, mapping

from stac_generator.core.output import BaseOutput


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class StacApiOutputBackend(BaseOutput):
    """
    Connects to a STAC API instance and exports the documents to STAC API.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.stac_host = kwargs["connection"]["host"]
        self.collection_name = kwargs["collection"]["name"]
        self.drop_properties = []

        if "drop_properties" in kwargs:
            self.drop_properties = kwargs["drop_properties"]

        # TODO : use same collection ID hasing than `stac-generator`
        self.collection_id = hashlib.md5(
            self.collection_name.encode("utf-8")
        ).hexdigest()

        r = requests.get(
            os.path.join(self.stac_host, f"collections/{self.collection_id}")
        )
        if r.status_code == 404:
            r.raise_for_status()

    def post_collection_item(self, stac_host, collection_id, json_data):
        """
        Post an item to a collection.
        """
        item_id = json_data["id"]
        r = requests.post(
            os.path.join(stac_host, f"collections/{collection_id}/items"),
            json=json_data,
        )

        if r.status_code == 200:
            print(
                f"{bcolors.OKGREEN}[INFO] Pushed STAC item [{item_id}] to [{stac_host}/collections/{collection_id}] ({r.status_code}){bcolors.ENDC}"
            )
        elif r.status_code == 409:
            print(
                f"{bcolors.WARNING}[INFO] STAC item [{item_id}] already exists on [{stac_host}/collections/{collection_id}] ({r.status_code}), updating..{bcolors.ENDC}"
            )
            # todo fix "asyncpg.exceptions.FeatureNotSupportedError: DELETE is not allowed in a non-volatile function"
            # r = requests.put(os.path.join(stac_host, f"collections/{collection_id}/items"), json=json_data)
            # r.raise_for_status()
        else:
            r.raise_for_status()
