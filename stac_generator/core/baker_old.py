# encoding: utf-8
"""
STAC Baker
==========
"""
from __future__ import annotations

from typing import Optional

__author__ = "Rhys Evans"
__date__ = "01 August 2023"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "rhys.r.evans@stfc.ac.uk"


import logging

# Python imports
from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel

LOGGER = logging.getLogger(__name__)


class ExtractionMethod(BaseModel):
    """STAC extraction method model."""

    method: str
    inputs: dict = {}

    def __repr__(self):
        return yaml.dump(self.dict())


class Recipe(BaseModel):
    """STAC recipe model."""

    location: Path
    type: str
    paths: Optional[list[Path]] = []
    id: Optional[list[ExtractionMethod]] = []
    extraction_methods: Optional[list[ExtractionMethod]] = []
    member_of: Optional[list[Recipe]] = []

    def __repr__(self):
        return yaml.dump(self.dict())

    def get(self, term: str, default: any):
        return getattr(self, term, default)

    def hash(self):
        return self.model_dump_json(self, sort_keys=True)


Recipe.update_forward_refs()


class Recipes:
    """
    Holds references to all the recipes files and returns an :py:obj:`STACRecipe`
    """

    def __init__(self, root_path: str):
        """

        :param root_path: Path to the root of the yaml files
        """
        self._load_data(root_path)

    def _load_recipe(self, file: Path, first: bool = True) -> Recipe:
        with open(file, encoding="utf-8") as reader:
            data = yaml.safe_load(reader)

        data["location"] = file

        member_of = []
        if first:
            for link_path in data.get("member_of", []):
                link_recipe = self._load_recipe(link_path, False)
                member_of.append(link_recipe)

        data["member_of"] = member_of

        return Recipe(**data)

    def _load_data(self, root_path: str) -> None:
        """
        Loads the yaml files from the root path and builds the recipe dictionary and map of
        the recipes applicaple paths and their locations.

        :param root_path: Path to root of yaml files
        """

        self.recipes = {}
        self.paths_to_location = {}

        for file_path in Path(root_path).rglob("*.y*ml"):
            recipe = self._load_recipe(file_path)

            self.recipes[file_path] = recipe

            for path in recipe.paths:
                self.paths_to_location[Path(path)] = file_path

    @lru_cache(100)
    def get(self, path: str) -> Recipe:
        """
        Get the most relevant recipe for a given path.

        :param path: Path for which to retrieve the recipe
        """

        if path in self.recipes:
            return self.recipes[path]

        for parent in Path(path).parents:
            if parent in self.paths_to_location:
                parent_path = self.paths_to_location[parent]
                return self.recipes[parent_path]

        raise ValueError(f"No Recipe found for path: {path}")
