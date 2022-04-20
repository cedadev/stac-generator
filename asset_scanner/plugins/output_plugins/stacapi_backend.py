# encoding: utf-8
"""
STAC API
-------------

An output backend which outputs the content generated to STAC API

**Plugin name:** ``stacapi``

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
    * - ``namespace``
      - ``str``
      - Can be used by downstream processors to separate outputs to different indices or clusters

Example Configuration:
    .. code-block:: yaml

        outputs:
            - name: stacapi
              connection:
                host: 'host1'
              collection:
                name: 'cmip5'
"""
__author__ = "Mathieu Provencher"
__date__ = "20 Apr 2022"
__copyright__ = "Copyright 2022 Computer Research Institute of Montréal"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "mathieu.provencher@crim.ca"

from typing import Dict
import requests
from urllib.parse import urljoin

from asset_scanner.core.utils import Coordinates, load_yaml

from .base import OutputBackend


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class StacApiOutputBackend(OutputBackend):
    """
    Connects to a STAC API instance and exports the
    documents to STAC API.
    """

    CLEAN_METHODS = ["_format_bbox", "_format_temporal_extent"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.stac_host = kwargs["connection"]["host"]
        self.collection_id = kwargs["collection"]["name"]

        # todo create collection if not exist

        # # Create the index, if it doesn't already exist
        # if index_conf.get("mapping"):
        #     if not self.es.indices.exists(self.index_name):
        #         mapping = load_yaml(index_conf.get("mapping"))
        #         self.es.indices.create(self.index_name, body=mapping)

    @staticmethod
    def _format_bbox(data: Dict) -> Dict:
        """
        Convert WGS84 coordinates into GeoJSON and
        format for Elasticsearch. Replaces the bbox key.

        :param data: Input data dictionary
        """
        body = data["body"]

        if body.get("bbox"):
            bbox = body.pop("bbox")

            body["spatial"] = {
                "bbox": {
                    "type": "envelope",
                    "coordinates": Coordinates.from_wgs84(bbox).to_geojson(),
                }
            }

        return data

    @staticmethod
    def _format_temporal_extent(data: Dict) -> Dict:
        """
        :param data: Input data dictionary
        """
        body = data["body"]

        if body.get("extent", {}).get("temporal"):
            temporal_extent = body["extent"].pop("temporal")

            if temporal_extent[0][0]:
                body["extent"]["temporal"] = {"gte": temporal_extent[0][0]}
            if temporal_extent[0][1]:
                temporal = body["extent"].get("temporal", {})
                temporal["lte"] = temporal_extent[0][1]
                body["extent"]["temporal"] = temporal

        return data

    def clean(self, data: Dict) -> Dict:
        """
        :param data: Input dictionary
        :returns: Dictionary produced as a result of the clean methods
        """

        for method in self.CLEAN_METHODS:
            m = getattr(self, method)
            data = m(data)

        return data

    def export(self, data, **kwargs):

        data = self.clean(data)

        json_data = {}

        self.post_collection_item(self.stac_host, self.collection_id, json_data)

    def post_collection_item(self, stac_host, collection_id, json_data):
        """
        Post an item to a collection.
        """
        item_id = json_data['id']
        r = requests.post(urljoin(stac_host, f"/collections/{collection_id}/items"), json=json_data)

        if r.status_code == 200:
            print(f"{bcolors.OKGREEN}[INFO] Created item [{item_id}] ({r.status_code}){bcolors.ENDC}")
        elif r.status_code == 409:
            print(f"{bcolors.WARNING}[INFO] Item already exists [{item_id}] ({r.status_code}), updating..{bcolors.ENDC}")
            r = requests.put(urljoin(stac_host, f"/collections/{collection_id}/items"), json=json_data)
            r.raise_for_status()
        else:
            r.raise_for_status()