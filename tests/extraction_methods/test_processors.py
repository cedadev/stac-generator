# encoding: utf-8
"""

"""
__author__ = "Richard Smith"
__date__ = "15 Jul 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import pytest

from stac_generator.plugins.extraction_methods.iso19115 import ISO19115Extract
from stac_generator.plugins.preprocessors.ceda_observation import (
    CEDAObservationPreProcessor,
)
from stac_generator.plugins.extraction_methods.regex import RegexExtract


@pytest.fixture
def regex_processor():
    return RegexExtract(regex=r"^(?:\w*[\s]){2}(?P<interesting>\w*)")


@pytest.fixture
def iso19115_processor():
    return ISO19115Extract(
        url_template="http://api.catalogue.ceda.ac.uk/export/xml/$uuid.xml",
        extraction_keys=[{"name": "start_datetime", "key": ".//gml:beginPosition"}],
    )


@pytest.fixture
def ceda_observation():
    return CEDAObservationPreProcessor(
        url_template="http://api.catalogue.ceda.ac.uk/api/v0/obs/get_info$uri"
    )


def test_regex_extract(regex_processor):
    """Check can extract groups with regex"""

    input = "this contains interesting stuff"
    expected = {"interesting": "interesting"}

    output = regex_processor.run(input)
    assert output == expected


# TODO: Mock the call to catalogue server
def test_iso19115_extract(iso19115_processor):
    """Check can extract data from the iso record"""

    input = "/irrelevant/filepath"
    expected = {"start_datetime": "2005-01-06T09:57:05"}

    iso19115_processor.url_template = "http://api.catalogue.ceda.ac.uk/export/xml/6f6d4b4fc7a042568cce7eccc6e9b6f2.xml"

    output = iso19115_processor.run(input)
    assert output == expected


# TODO: Mock the call to catalogue server
def test_iso19115_processor_with_preprocessor(iso19115_processor, ceda_observation):
    """Check processor works with ceda obs pre-processor"""

    input = "/badc/faam/data/2005/b070-jan-06"
    expected = {"start_datetime": "2005-01-06T09:57:05"}

    output = iso19115_processor.run(input, pre_processors=[ceda_observation])
    assert output == expected


# TODO: Mock the call to catalogue server
def test_iso19115_processor_with_preprocessor_null_output(
    iso19115_processor, ceda_observation, caplog
):
    """
    Checkout non-failing output and warning when pre-processor fails to provide the
    template keys.
    """

    input = "/badc"
    expected = {}

    output = iso19115_processor.run(input, pre_processors=[ceda_observation])

    assert output == expected
    assert "URL templating failed" in caplog.text
