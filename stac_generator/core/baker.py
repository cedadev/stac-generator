# encoding: utf-8
"""
STAC Baker
==========
"""
from __future__ import annotations

from itertools import chain

__author__ = "Rhys Evans"
__date__ = "01 August 2023"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "rhys.r.evans@stfc.ac.uk"

import hashlib
import logging

# Python imports
from functools import lru_cache
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, field_serializer

LOGGER = logging.getLogger(__name__)


class ExtractionMethodConf(BaseModel):
    """STAC extraction method model."""

    method: str
    inputs: Optional[dict] = {}

    def __repr__(self):
        return yaml.dump(self.model_dump())


class Recipe(BaseModel):
    """Recipe model."""

    _key: Optional[str] = None
    type: str
    paths: Optional[list[Path]] = []
    id: Optional[list[ExtractionMethodConf]] = []
    extraction_methods: Optional[list[ExtractionMethodConf]] = []
    links: Optional[list[dict]] = []
    _member_of: Optional[list[Recipe]] = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_key()

    @property
    def key(self):
        """Get key"""
        # Hidden variables not used in model dump
        return self._key

    @property
    def member_of(self):
        """Get member_of"""
        # Hidden variables not used in model dump
        return self._member_of

    @member_of.setter
    def member_of(self, value):
        """Set member_of"""
        self._member_of = value

    def set_key(self):
        """Fuction to set recipe key"""
        recipe_json = self.model_dump_json()
        # Using hash for key as it is independent of storage location
        self._key = hashlib.md5(recipe_json.encode("utf-8")).hexdigest()

    @field_serializer("paths")
    def serialize_paths(self, paths: list[Path], _info):
        """serialize paths to strings"""
        return [str(path) for path in paths]

    def __repr__(self):
        return yaml.dump(self.model_dump())


Recipe.model_rebuild()


class Recipes:
    """
    Holds references to all the recipes files and returns an :py:obj:`STACRecipe`
    """

    def __init__(self, root_path: str):
        """
        :param root_path: Path to the root of the yaml files
        """
        self.recipes = {"asset": {}, "item": {}, "collection": {}}
        self.paths_map = {"asset": {}, "item": {}, "collection": {}}
        self.location_map = {}

        for file_path in Path(root_path).rglob("*.y*ml"):
            _ = self._load_data(file_path)

    def _load_data(self, file: Path) -> Recipe:
        """
        Loads the yaml files from the root path and builds the recipe dictionary and map of
        the recipes applicaple paths and their locations.

        :param root_path: Path to root of yaml files
        """
        if file in self.location_map.keys():
            location_map_file = self.location_map[file]
            return self.recipes[location_map_file["type"]][location_map_file["key"]]

        with open(file, "r", encoding="utf-8") as reader:
            data = yaml.safe_load(reader)

        links = []
        for path in data.pop("member_of", []):
            link_recipe = self._load_data(path)
            links.append({"key": link_recipe.key, "type": link_recipe.type})

        data["links"] = links

        recipe = Recipe(**data)

        self.recipes[recipe.type][recipe.key] = recipe
        self.location_map[file] = {"key": recipe.key, "type": recipe.type}

        for path in recipe.paths:
            self.paths_map[recipe.type][Path(path)] = recipe.key

        return recipe

    @lru_cache(100)
    def load_recipe(self, key: str, stac_type: str) -> Recipe:
        """
        Load the links from recipes member for ID generation.

        :param recipe: Recipe for links to be loaded for
        """
        recipe = self.recipes[stac_type][key]

        recipe.member_of = [
            self.recipes[link["type"]][link["key"]] for link in recipe.links
        ]

        return recipe

    def get(self, path: str, stac_type: str) -> Recipe:
        """
        Get the most relevant recipe for a given path.

        :param path: Path for which to retrieve the recipe
        :param stac_type: Type of recipe to return
        """
        if path in self.recipes[stac_type]:
            return self.load_recipe(path, stac_type)

        for parent in chain([path], Path(path).parents):
            if parent in self.paths_map[stac_type]:
                key = self.paths_map[stac_type][parent]

                return self.load_recipe(key, stac_type)

        raise ValueError(f"No Recipe found for path: {path}")

    def get_maps(self):
        return self.paths_map, self.location_map
