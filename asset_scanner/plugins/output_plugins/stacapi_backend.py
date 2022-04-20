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
    * - ``connection.host``
      - ``REQUIRED`` STAC API URL
    * - ``collection.name``
      - ``str``
      - ``REQUIRED`` The collection to output the content.

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
import tzlocal
import pytz


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


# Taken from https://chromium.googlesource.com/infra/infra/infra_libs/+/b2e2c9948c327b88b138d8bd60ec4bb3a957be78/time_functions/testing.py
class MockDateTimeMeta(datetime.datetime.__dict__.get('__metaclass__', type)):
    @classmethod
    def __instancecheck__(cls, instance):
      return isinstance(instance, datetime.datetime)

# Taken from https://chromium.googlesource.com/infra/infra/infra_libs/+/b2e2c9948c327b88b138d8bd60ec4bb3a957be78/time_functions/testing.py
class MockDateTime():
    __metaclass__ = MockDateTimeMeta
    mock_utcnow = datetime.datetime.utcnow()
    tzinfo = "mock"

    @classmethod
    def isoformat(cls):
        return cls.mock_utcnow.strftime("%Y-%m-%dT%H:%M:%SZ")

    @classmethod
    def utcnow(cls):
        return cls.mock_utcnow

    @classmethod
    def now(cls, tz=None):
        if not tz:
            tz = tzlocal.get_localzone()
        tzaware_utcnow = pytz.utc.localize(cls.mock_utcnow)
        return tz.normalize(tzaware_utcnow.astimezone(tz)).replace(tzinfo=None)

    @classmethod
    def today(cls):
        return cls.now().date()

    @classmethod
    def fromtimestamp(cls, timestamp, tz=None):
        if not tz:
            # TODO(sergiyb): This may fail for some unclear reason because pytz
            # doesn't find normal timezones such as 'Europe/Berlin'. This seems to
            # happen only in appengine/chromium_try_flakes tests, and not in tests
            # for this module itself.
            tz = tzlocal.get_localzone()
        tzaware_dt = pytz.utc.localize(cls.utcfromtimestamp(timestamp))
        return tz.normalize(tzaware_dt.astimezone(tz)).replace(tzinfo=None)


class StacApiOutputBackend(OutputBackend):
    """
    Connects to a STAC API instance and exports the
    documents to STAC API.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.stac_host = kwargs["connection"]["host"]
        self.collection_id = kwargs["collection"]["name"]

        stac_collection = self.create_stac_collection(self.collection_id)
        self.post_collection(self.stac_host, stac_collection)

    def export(self, data, **kwargs):
        # todo avoid processing second json object
        if "body" not in data:
            return

        json_data = self.create_stac_item(data)

        self.post_collection_item(self.stac_host, self.collection_id, json_data)

    def create_stac_collection(self, collection_name):
        # extents
        sp_extent = pystac.SpatialExtent([-180, -180, 180, 180])
        capture_date = datetime.datetime.strptime('2015-10-22', '%Y-%m-%d')
        end_capture_date = datetime.datetime.strptime('2100-10-22', '%Y-%m-%d')
        tmp_extent = pystac.TemporalExtent([(capture_date, end_capture_date)])
        extent = pystac.Extent(sp_extent, tmp_extent)

        collection = pystac.Collection(id=collection_name,
                                       description=collection_name,
                                       extent=extent,
                                       license='na')

        return collection.to_dict()

    def post_collection(self, stac_host, json_data):
        """
        Post a STAC collection.

        Returns the collection id.
        """
        collection_id = json_data['id']
        r = requests.post(os.path.join(stac_host, "collections"), json=json_data)

        if r.status_code == 200:
            print(f"{bcolors.OKGREEN}[INFO] Created collection [{collection_id}] ({r.status_code}){bcolors.ENDC}")
        elif r.status_code == 409:
            print(f"{bcolors.WARNING}[INFO] Collection already exists [{collection_id}] ({r.status_code}), updating..{bcolors.ENDC}")
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

        # TODO : utils.MockDateTime() has been used since STAC API requires date in %Y-%m-%dT%H:%M:%SZ format while
        #  pystac.Item.datetime include the ms
        stac_item.datetime = MockDateTime()
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
            print(f"{bcolors.OKGREEN}[INFO] Created item [{item_id}] ({r.status_code}){bcolors.ENDC}")
        elif r.status_code == 409:
            print(f"{bcolors.WARNING}[INFO] Item already exists [{item_id}] ({r.status_code}), updating..{bcolors.ENDC}")
            # todo fix "DELETE is not allowed in a non-volatile function"
            # r = requests.put(os.path.join(stac_host, f"collections/{collection_id}/items"), json=json_data)
            # r.raise_for_status()
        else:
            r.raise_for_status()
