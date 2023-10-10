# encoding: utf-8
__author__ = "Richard Smith"
__date__ = "11 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import logging
from datetime import datetime

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

            - method: stac_observation

    """

    def run(
        self,
        body: dict,
        recipe: Recipe,
        **kwargs,
    ) -> dict:
        output = {
            "type": "Feature",
            "stac_version": self.stac_version,
            "stac_extensions": self.stac_extensions,
            "id": body.pop(f"{kwargs['TYPE'].value}_id"),
            "geometry": None,
            "assets": {},
            "properties": {
                "datetime": None,
            },
        }

        extent = {}
        if "datetime" in body:
            output["properties"]["datetime"] = body.pop("datetime")

        if "start_datetime" in body:
            output["properties"]["start_datetime"] = body.pop("start_datetime")

        if "end_datetime" in body:
            output["properties"]["end_datetime"] = body.pop("end_datetime")

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
