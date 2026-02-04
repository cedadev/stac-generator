# encoding: utf-8
__author__ = "Ag Stephens"
__date__ = "23 Jan 2026"
__copyright__ = "Copyright 2026 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import logging
import copy
import os
import sys

from dateutil import parser
from pydantic import BaseModel, Field

from stac_generator.core.baker import Recipe

# Package imports
from stac_generator.core.mapping import BaseMapping

sys.path.insert(0, ".")

STAC_CROISSANT_MAP_FILE = "stac_croissant_map.py"
if os.path.isfile(STAC_CROISSANT_MAP_FILE):
    import stac_croissant_map as scm
    print(f"Loaded: {STAC_CROISSANT_MAP_FILE}")
else:
    scm = None


LOGGER = logging.getLogger(__name__)

CROISSANT_FIXED_PROPERTIES = {
    "@context": {
        "@language": "en",
        "@vocab": "https://schema.org/",
        "arrayShape": "cr:arrayShape",
        "citeAs": "cr:citeAs",
        "column": "cr:column",
        "conformsTo": "dct:conformsTo",
        "cr": "http://mlcommons.org/croissant/",
        "data": {
            "@id": "cr:data",
            "@type": "@json"
        },
        "dataBiases": "cr:dataBiases",
        "dataCollection": "cr:dataCollection",
        "dataType": {
            "@id": "cr:dataType",
            "@type": "@vocab"
        },
        "dct": "http://purl.org/dc/terms/",
        "extract": "cr:extract",
        "field": "cr:field",
        "fileProperty": "cr:fileProperty",
        "fileObject": "cr:fileObject",
        "fileSet": "cr:fileSet",
        "format": "cr:format",
        "includes": "cr:includes",
        "isArray": "cr:isArray",
        "isLiveDataset": "cr:isLiveDataset",
        "jsonPath": "cr:jsonPath",
        "key": "cr:key",
        "md5": "cr:md5",
        "parentField": "cr:parentField",
        "path": "cr:path",
        "personalSensitiveInformation": "cr:personalSensitiveInformation",
        "recordSet": "cr:recordSet",
        "references": "cr:references",
        "regex": "cr:regex",
        "repeated": "cr:repeated",
        "replace": "cr:replace",
        "sc": "https://schema.org/",
        "separator": "cr:separator",
        "source": "cr:source",
        "subField": "cr:subField",
        "transform": "cr:transform",
        "containedIn": "cr:containedIn"
    }
}

class CroissantConf(BaseModel):
    """Croissant mapping config model."""

    croissant_version: str = Field(
        default="1.0",
        description="Croissant version.",
    )
    conformsTo: str = Field(
        default="http://mlcommons.org/croissant/1.0",
        description="Croissant conformance link"
    )


class CroissantMapping(BaseMapping):
    """Map metadata into Croissant.

    Mapping Name**: ``croissant_mapping``

    Description:


    Example Configuration:

        .. code-block:: yaml

            - name: croissant_mapping
              conf:
                croissant_version: 1.0.0

    """

    config_class = CroissantConf

    def datetime_field(self, date_str: str) -> str:
        dt = parser.parse(date_str)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    def _get_parent_from_nested_dict(self, dct, path):
        """
        Return parent of nested path keys in dct and return it.
        """
        current_dct = dct
        for key in path[:-1]:
            current_dct = current_dct[key]

        return current_dct


    def croissant_record(self, body: dict) -> dict:
        fixed = {
            "croissant_version": self.conf.croissant_version,
            "id": body.pop("id"),
        }

        output = CROISSANT_FIXED_PROPERTIES | {"@type": "sc:Dataset"} | body

        # If mapper file is imported, then use mappings
        get_parent = self._get_parent_from_nested_dict
        if scm:
            print("Applying STAC-to-Croissant mappings.")
            delimiter = getattr(scm, "delimiter", "|")

            print("Overriding fields")
            for key, value in getattr(scm, "overrides", {}):
                key_path = key.split(delimiter)
                get_parent(output, key_path)[key_path[-1]] = value

            print("Mapping fields")
            for key, value in getattr(scm, "mapper", {}).items():
                key_path = key.split(delimiter)
                value_path = value.split(delimiter)
                parent = get_parent(output, key_path)
                content = copy.deepcopy(parent[key_path[-1]])
                del parent[key_path[-1]]

                current = output
                for v_key in value_path[:-1]:
                    current[v_key] = {}
                    current = current[v_key]

                current[value_path[-1]] = content

            print("Removing fields")
            for key in getattr(scm, "removals", []):
                key_path = key.split(delimiter)
                del get_parent(output, key_path)[key_path[-1]]

        print("Mapped STAC content to Croissant.")
        return output

    def run(
        self,
        body: dict,
        recipe: Recipe,
        **kwargs,
    ) -> dict:
        return self.croissant_record(body)
