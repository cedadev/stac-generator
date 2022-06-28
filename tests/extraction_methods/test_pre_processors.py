# encoding: utf-8
"""

"""
__author__ = "Richard Smith"
__date__ = "15 Jul 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import pytest

from stac_generator.plugins.extraction_methods.preprocessors import (
    CEDAObservation,
    ReducePathtoName,
)


@pytest.fixture
def filename_reducer():
    """
    Create filename_reducer instance
    :return:
    """
    return ReducePathtoName()


def test_filename_reducer_posix(filename_reducer):
    """
    Check that pre-processor extracts the filename from the POSIX path
    :param filename_reducer:
    :return:
    """
    input = "/a/b/c/d.txt"
    expected = "d.txt"

    uri, _ = filename_reducer.run(input)
    assert uri == expected


@pytest.fixture
def ceda_observation():
    return CEDAObservation(
        url_template="http://api.catalogue.ceda.ac.uk/api/v0/obs/get_info$uri"
    )


def test_ceda_observation(ceda_observation):
    input = "/badc/faam/data/2005/b070-jan-06"
    expected = "6f6d4b4fc7a042568cce7eccc6e9b6f2"

    _, kwargs = ceda_observation.run(input)
    assert kwargs["uuid"] == expected
