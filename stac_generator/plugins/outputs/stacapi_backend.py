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
from stac_generator.core.output import BaseOutput
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


class StacApiOutputBackend(BaseOutput):
    """
    Connects to a STAC API instance and exports the documents to STAC API.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.stac_host = kwargs["connection"]["host"]
        self.collection_name = kwargs["collection"]["name"]
        self.drop_properties = kwargs["drop_properties"] or []
        self.collection_id = generate_id(self.collection_name)

        # TODO if collection not exist, raise

    def export(self, data, **kwargs):
        # todo avoid processing second json object
        if "body" not in data:
            return

        json_data = self.create_stac_item(data)
        self.post_collection_item(self.stac_host, self.collection_id, json_data)

    def create_stac_item(self, data):
        # get bbox and footprint
        bounds = {
            "left": -140.99778,
            "bottom": 41.6751050889,
            "right": -52.6480987209,
            "top": 83.23324
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

        properties_list = dict()

        for k, v in data["body"]["properties"].items():
            if k not in self.drop_properties:
                properties_list[k] = v

        stac_item.properties = properties_list

        link = pystac.Link("self", "{}/collections/{}/items/{}".format(self.stac_host, self.collection_id, stac_item.id))
        stac_item.add_link(link)

        # TODO : hardcoded url path replacements
        asset = pystac.Asset(href=data["body"]["properties"]["uri"].replace("dodsC", "fileServer"), media_type="application/netcdf",
                             title=data["body"]["properties"]["filename"], roles=["data"])
        stac_item.add_asset('metadata_http', asset)

        asset = pystac.Asset(href=data["body"]["properties"]["uri"].replace("dodsC", "iso"), media_type="application/xml",
                             title="ISO", roles=["metadata"])
        stac_item.add_asset('metadata_iso', asset)

        asset = pystac.Asset(href=data["body"]["properties"]["uri"].replace("dodsC", "ncml"), media_type="application/xml",
                             title="NcML", roles=["metadata"])
        stac_item.add_asset('metadata_ncml', asset)

        asset = pystac.Asset(href=data["body"]["properties"]["uri"], media_type="application/netcdf",
                             title="OPeNDAP", roles=["data"])
        stac_item.add_asset('metadata_opendap', asset)

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
            # todo fix "asyncpg.exceptions.FeatureNotSupportedError: DELETE is not allowed in a non-volatile function"
            # r = requests.put(os.path.join(stac_host, f"collections/{collection_id}/items"), json=json_data)
            # r.raise_for_status()
        else:
            r.raise_for_status()