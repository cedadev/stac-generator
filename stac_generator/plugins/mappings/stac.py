# encoding: utf-8
__author__ = "Richard Smith"
__date__ = "11 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import logging

from dateutil import parser
from pydantic import BaseModel, Field

from stac_generator.core.baker import Recipe

# Package imports
from stac_generator.core.mapping import BaseMapping

LOGGER = logging.getLogger(__name__)


class STACConf(BaseModel):
    """STAC mapping config model."""

    stac_root_url: str = Field(
        description="STAC root URL.",
    )
    stac_version: str = Field(
        description="STAC version.",
    )
    stac_extensions: list[str] = Field(
        default=[],
        description="STAC extensions.",
    )


class STACMapping(BaseMapping):
    """Map metadata into STAC.

    Mapping Name**: ``stac_mapping``

    Description:


    Example Configuration:

        .. code-block:: yaml

            - name: stac_mapping
              conf:
                stac_root_url: http://stac.catalog
                stac_version: 0.0.1

    """

    config_class = STACConf

    def datetime_field(self, date_str: str) -> str:
        dt = parser.parse(date_str)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    def item(self, body: dict) -> dict:
        output = {
            "type": "Feature",
            "stac_version": self.conf.stac_version,
            "stac_extensions": body.pop("stac_extensions", []) + self.conf.stac_extensions,
            "id": body.pop("id"),
            "geometry": body.pop("geometry", None),
            "bbox": body.pop("bbox"),
            "properties": {
                "datetime": None,
            },
            "links": body.pop("links", [])
            + [
                {
                    "rel": "self",
                    "type": "application/geo+json",
                    "href": f"{self.conf.stac_root_url}/collections/{body['collection']}/items/{body['id']}",
                },
                {
                    "rel": "parent",
                    "type": "application/json",
                    "href": f"{self.conf.stac_root_url}/collections/{body['collection']}",
                },
                {
                    "rel": "collection",
                    "type": "application/json",
                    "href": f"{self.conf.stac_root_url}/collections/{body['collection']}",
                },
                {
                    "rel": "root",
                    "type": "application/json",
                    "href": self.conf.stac_root_url,
                },
            ],
            "assets": body.pop("assets", {}),
            "collection": body.pop("collection"),
        }

        if title := body.pop("title", None):
            output["properties"]["title"] = title

        if description := body.pop("description", None):
            output["properties"]["description"] = description

        if version := body.pop("version", None):
            output["properties"]["version"] = version

        if "datetime" in body:
            output["properties"]["datetime"] = self.datetime_field(body.pop("datetime"))

        if "start_datetime" in body:
            output["properties"]["start_datetime"] = self.datetime_field(body.pop("start_datetime"))

        if "end_datetime" in body:
            output["properties"]["end_datetime"] = self.datetime_field(body.pop("end_datetime"))

        if project := body.pop("project", None):
            output["properties"]["project"] = project

        if license := body.pop("license", None):
            output["properties"]["license"] = license

        if sci_doi := body.pop("sci:doi", None):
            output["properties"]["sci:doi"] = sci_doi

        if sci_citation := body.pop("sci:citation", None):
            output["properties"]["sci:citation"] = sci_citation

        output["properties"] |= body

        return output

    def collection(self, body: dict) -> dict:
        output = {
            "type": "Collection",
            "stac_version": self.conf.stac_version,
            "stac_extensions": self.conf.stac_extensions,
            "id": body.pop("id"),
        }

        if title := body.pop("title", None):
            output["title"] = title

        if description := body.pop("description", None):
            output["description"] = description

        if keywords := body.pop("keywords", []):
            output["keywords"] = keywords

        if license := body.pop("license", None):
            output["properties"]["license"] = license

        if providers := body.pop("providers", []):
            output["providers"] = providers

        if extent := body.pop(
            "extent",
            {
                "temporal": {
                    "interval": None,
                },
                "spatial": {
                    "bbox": None,
                },
            },
        ):
            output["extent"] = extent

        if bbox := body.pop("bbox", None):
            output["extent"]["spatial"]["bbox"] = bbox

        if interval := body.pop("interval", None):
            output["extent"]["temporal"]["interval"] = interval

        output["links"] = body.pop("links", []) + [
            {
                "rel": "self",
                "type": "application/geo+json",
                "href": f"{self.conf.stac_root_url}/collections/{output['id']}",
            },
            {
                "rel": "parent",
                "type": "application/json",
                "href": f"{self.conf.stac_root_url}/",
            },
            {
                "rel": "queryables",
                "type": "application/json",
                "href": f"{self.conf.stac_root_url}/collections/{output['id']}/queryables",
            },
            {
                "rel": "items",
                "type": "application/geo+json",
                "href": f"{self.conf.stac_root_url}/collections/cmip6/{output['id']}",
            },
            {
                "rel": "root",
                "type": "application/json",
                "href": self.conf.stac_root_url,
            },
        ]

        if assets := body.pop("assets", {}):
            output["assets"] = assets

        if item_assets := body.pop("item_assets", {}):
            output["item_assets"] = item_assets

        output["summaries"] |= body

        return output

    def run(
        self,
        body: dict,
        recipe: Recipe,
        **kwargs,
    ) -> dict:
        if kwargs["GENERATOR_TYPE"] == "item":
            return self.item(body)

        if kwargs["GENERATOR_TYPE"] == "collection":
            return self.collection(body)

        return body
