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
    * - ``collection.description``
      - ``str``
      - ``REQUIRED`` The collection description.

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

import requests
from shapely.geometry import Polygon, mapping
import os
import pystac
import pystac.extensions.eo
import datetime
from .base import OutputBackend
from asset_scanner.core.utils import generate_id


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
    Connects to a STAC API instance and exports the documents to STAC API.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.stac_host = kwargs["connection"]["host"]
        self.collection_name = kwargs["collection"]["name"]
        self.collection_id = generate_id(self.collection_name)
        self.collection_description = kwargs["collection"]["description"]

        stac_collection = self.create_stac_collection(self.collection_id, self.collection_name, self.collection_description)
        self.post_collection(self.stac_host, stac_collection)

    def export(self, data, **kwargs):
        # todo avoid processing second json object
        if "body" not in data:
            return

        json_data = self.create_stac_item(data)

        self.post_collection_item(self.stac_host, self.collection_id, json_data)

    def create_stac_collection(self, collection_id, collection_name, collection_description):
        sp_extent = pystac.SpatialExtent([[-180, -90, 180, 90]])
        capture_date = datetime.datetime.strptime('2015-10-22', '%Y-%m-%d')
        end_capture_date = datetime.datetime.strptime('2100-10-22', '%Y-%m-%d')
        tmp_extent = pystac.TemporalExtent([(capture_date, end_capture_date)])
        extent = pystac.Extent(sp_extent, tmp_extent)

        collection = pystac.Collection(id=collection_id,
                                       title=collection_name,
                                       description=collection_description,
                                       extent=extent,
                                       keywords=[
                                           "climate change",
                                           "CMIP5",
                                           "WCRP",
                                           "CMIP"
                                       ],
                                       providers=None,
                                       summaries=pystac.Summaries({"product": [
                                               "output1"
                                           ]})
                                       )

        return collection.to_dict()

    def post_collection(self, stac_host, json_data):
        """
        Post a STAC collection.

        Returns the collection id.
        """
        collection_id = json_data['id']
        r = requests.post(os.path.join(stac_host, "collections"), json=json_data)

        if r.status_code == 200:
            print(f"{bcolors.OKGREEN}[INFO] Pushed STAC collection [{collection_id}] to [{stac_host}] ({r.status_code}){bcolors.ENDC}")
        elif r.status_code == 409:
            print(f"{bcolors.WARNING}[INFO] STAC collection [{collection_id}] already exists on [{stac_host}] ({r.status_code}), updating..{bcolors.ENDC}")
            r = requests.put(os.path.join(stac_host, "collections"), json=json_data)
            r.raise_for_status()
        else:
            r.raise_for_status()

        return collection_id

    def create_stac_item(self, data):
        # get bbox and footprint
        bounds = {
            "left": -180,
            "bottom": -180,
            "right": 180,
            "top": 180
        }
        bbox = [bounds["left"], bounds["bottom"], bounds["right"], bounds["top"]]
        footprint = Polygon([
            [bounds["left"], bounds["bottom"]],
            [bounds["left"], bounds["top"]],
            [bounds["right"], bounds["top"]],
            [bounds["right"], bounds["bottom"]]
        ])

        stac_item = pystac.Item(id=data["body"]["item_id"],
                                geometry=mapping(footprint),
                                bbox=bbox,
                                datetime=datetime.datetime.utcnow(),
                                properties={},
                                collection=self.collection_id)

        stac_item.properties = data["body"]["properties"]

        link = pystac.Link("self", "dummy")
        stac_item.add_link(link)

        asset = pystac.Asset(href=data["body"]["location"], media_type="application/netcdf", title=data["body"]["filename"], roles=["data"])
        stac_item.add_asset('metadata_http', asset)

        return stac_item.to_dict()

    def post_collection_item(self, stac_host, collection_id, json_data):
        """
        Post an item to a collection.
        """
        item_id = json_data['id']
        r = requests.post(os.path.join(stac_host, f"collections/{collection_id}/items"), json=json_data)

        if r.status_code == 200:
            print(f"{bcolors.OKGREEN}[INFO] Pushed STAC item [{item_id}] to [{stac_host}/collections/{collection_id}] ({r.status_code}){bcolors.ENDC}")
        elif r.status_code == 409:
            print(f"{bcolors.WARNING}[INFO] STAC item [{item_id}] already exists on [{stac_host}/collections/{collection_id}] ({r.status_code}), updating..{bcolors.ENDC}")
            # todo fix "DELETE is not allowed in a non-volatile function"
            # r = requests.put(os.path.join(stac_host, f"collections/{collection_id}/items"), json=json_data)
            # r.raise_for_status()
        else:
            r.raise_for_status()
