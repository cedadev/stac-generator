# encoding: utf-8
__author__ = "Richard Smith"
__date__ = "11 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import logging
from datetime import datetime
from dateutil import parser

from stac_generator.core.baker import Recipe

# Package imports
from stac_generator.core.mapping import BaseMapping

LOGGER = logging.getLogger(__name__)


class STACMapping(BaseMapping):
    """

    Mapping Name: ``stac_mapping``

    Description:
        Takes body, and recipe and returns object in STAC mapping.

    Example Configuration:

        .. code-block:: yaml

            - method: stac_mapping

    """

    def datetime_field(self, body: dict, key: str) -> str:
        dt = parser.parse(body.pop(key))
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    def item(self, body: dict) -> dict:
        output = {
            "type": "Feature",
            "stac_version": self.stac_version,
            "stac_extensions": self.stac_extensions,
            "id": body.pop("item_id"),
            "geometry": None,
            "assets": {},
            "properties": {
                "datetime": None,
            },
        }

        if "datetime" in body:
            output["properties"]["datetime"] = self.datetime_field(body, "datetime")

        if "start_datetime" in body:
            output["properties"]["start_datetime"] = self.datetime_field(
                body, "start_datetime"
            )

        if "end_datetime" in body:
            output["properties"]["end_datetime"] = self.datetime_field(
                body, "end_datetime"
            )

        if "bbox" in body:
            output["bbox"] = body.pop("bbox")

        if "geometry" in body:
            output["geometry"] = body.pop("geometry")

        if "assets" in body:
            output["assets"] = body.pop("assets")

        if "member_of_recipes" in body:
            output["member_of_recipes"] = body.pop("member_of_recipes")

        if "collection_id" in body:
            output["collection"] = body.pop("collection_id")[0]

        output["properties"] |= body

        return output

    def collection(self, body: dict) -> dict:
        output = {
            "type": "Collection",
            "stac_version": self.stac_version,
            "stac_extensions": self.stac_extensions,
            "id": body.pop("collection_id"),
            "extent": {
                "temporal": {
                    "interval": None,
                },
                "spatial": {
                    "bbox": None,
                },
            },
            "summaries": {},
            "assets": {},
            "providers": [],
            "license": "",
        }

        if "description" in body:
            output["description"] = body.pop("description")

        if "interval" in body:
            output["extent"]["temporal"]["interval"] = body.pop("interval")

        if "bbox" in body:
            output["extent"]["spatial"]["bbox"] = body.pop("bbox")

        if "license" in body:
            output["license"] = body.pop("license")

        if "providers" in body:
            output["providers"] = body.pop("providers")

        if "member_of_recipes" in body:
            output["member_of_recipes"] = body.pop("member_of_recipes")

        output["summaries"] |= body

        return output

    def run(
        self,
        body: dict,
        recipe: Recipe,
        **kwargs,
    ) -> dict:
        if kwargs["TYPE"].value == "item":
            return self.item(body)

        elif kwargs["TYPE"].value == "collection":
            return self.collection(body)

        return body
