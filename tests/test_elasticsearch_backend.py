# encoding: utf-8
"""

"""
__author__ = "Richard Smith"
__date__ = "30 Jul 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import pytest

from asset_scanner.plugins.output_plugins.elasticsearch_backend import (
    ElasticsearchOutputBackend,
)


@pytest.fixture
def elasticsearch_backend():
    return ElasticsearchOutputBackend(connection_kwargs={}, index={"name": "test"})


def test_elasticsearch_clean(elasticsearch_backend):
    data = {"body": {"bbox": ["-37", "38", "-28", "42"]}}

    expected = {
        "body": {
            "spatial": {
                "bbox": {
                    "type": "envelope",
                    "coordinates": [["-37", "42"], ["-28", "38"]],
                }
            }
        }
    }

    output = elasticsearch_backend.clean(data)
    assert output == expected
