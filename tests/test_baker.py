# encoding: utf-8
""" """
__author__ = "Richard Smith"
__date__ = "22 Oct 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import os
from pathlib import Path

import pytest

from stac_generator.core.baker import Recipes

ROOT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_recipes")


@pytest.fixture
def recipes():
    return Recipes(ROOT_PATH)


def test_retrieve_posix_description(recipes):

    recipe = recipes.get("/a/b/c/d/e", "item")

    print(recipe.paths)

    assert recipe.paths == [Path("/a/b/c"), Path("gc://a/b/c")]


def test_retrieve_remote_description(recipes):

    recipe = recipes.get("gc://a/b/c/d/e", "item")

    assert recipe.paths == [Path("/a/b/c"), Path("gc://a/b/c")]
