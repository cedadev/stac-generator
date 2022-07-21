# encoding: utf-8
"""

"""
__author__ = "Richard Smith"
__date__ = "15 Jul 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import pytest

from stac_generator.plugins.preprocessors.ceda_observation import (
    CEDAObservationPreProcessor,
)
from stac_generator.plugins.preprocessors.basename import BasenamePreProcessor


@pytest.fixture
def basename():
    """
    Create basename instance
    :return:
    """
    return BasenamePreProcessor()


def test_basename_posix(basename):
    """
    Check that pre-processor extracts the filename from the POSIX path
    :param basename:
    :return:
    """
    input_path = "/a/b/c/d.txt"
    expected = "d.txt"

    uri, _ = basename.run(input_path)
    assert uri == expected


@pytest.fixture
def ceda_observation():
    return CEDAObservationPreProcessor(
        url_template="http://api.catalogue.ceda.ac.uk/api/v0/obs/get_info$uri"
    )


def test_ceda_observation(ceda_observation):
    input_path = "/badc/faam/data/2005/b070-jan-06"
    expected = "6f6d4b4fc7a042568cce7eccc6e9b6f2"

    _, kwargs = ceda_observation.run(input_path)
    assert kwargs["uuid"] == expected
