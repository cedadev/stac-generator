# encoding: utf-8
"""

"""
__author__ = "Richard Smith"
__date__ = "22 Oct 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import os

import pytest

from stac_generator.core.collection_describer import CollectionDescriptions

ROOT_DESCRIPTIONS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "test_descriptions"
)

default_description = {
    "paths": [],
    "asset": {},
    "item": {},
    "collection": {},
    "categories": [],
}


@pytest.fixture
def item_descriptions():
    print(ROOT_DESCRIPTIONS)
    return CollectionDescriptions(ROOT_DESCRIPTIONS)


def test_retrieve_posix_description(collection_descriptions):
    expected = {**default_description, **{"paths": ["/a/b/c"]}}

    description = collection_descriptions.get_description("/a/b/c/d/e")

    print(expected)
    print(description.dict())
    assert description.dict() == expected


def test_retrieve_remote_description(collection_descriptions):
    expected = {**default_description, **{"paths": ["gc://a/b/c"]}}

    description = collection_descriptions.get_description("gc://a/b/c/d/e")
    assert description.dict() == expected
