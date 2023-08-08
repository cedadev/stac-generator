# encoding: utf-8
__author__ = "Richard Smith"
__date__ = "11 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import logging
from datetime import datetime
from pathlib import Path

from stac_generator.core.baker import Recipe

# Package imports
from stac_generator.core.mapping import BaseMapping

LOGGER = logging.getLogger(__name__)


class CEDAMapping(BaseMapping):
    """

    Mapping Name: ``ceda_mapping``

    Description:
        Takes ids, body, and recipe and returns object in CEDA mapping.

    Configuration Options:
        - ``url_template``: ``REQUIRED`` URL string template to build url.
          Template uses the `python string template <https://docs.python.org/3/library/string.html#template-strings>`_ format.

    Example Configuration:

        .. code-block:: yaml

            - method: ceda_observation
              inputs:
                url_template: http://api.catalogue.ceda.ac.uk/api/v0/obs/get_info$uri

    """

    def run(
        self,
        body: dict,
        recipe: Recipe,
        **kwargs,
    ) -> dict:
        output = {
            f"{kwargs['TYPE'].value}_id": body.pop(f"{kwargs['TYPE'].value}_id"),
            "stac": {
                "member_of_recipes": body.pop("member_of_recipes"),
                "mod_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "status": "new",
            },
        }

        extent = {}
        if "datetime" in body:
            extent["datetime"] = body.pop("datetime")

        if "start_datetime" in body:
            extent["start_datetime"] = body.pop("start_datetime")

        if "end_datetime" in body:
            extent["end_datetime"] = body.pop("end_datetime")

        if "bbox" in body:
            extent["bbox"] = body.pop("bbox")

        if "geometry" in body:
            extent["geometry"] = body.pop("geometry")

        if extent:
            output["extent"] = extent

        output["properties"] = body

        return output
