# encoding: utf-8
"""

"""
__author__ = "Richard Smith"
__date__ = "15 Jul 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import pytest

from stac_generator.plugins.postprocessors.bbox import BboxPostProcessor
from stac_generator.plugins.postprocessors.date_combinator import (
    DateCombinatorPostProcessor,
)
from stac_generator.plugins.postprocessors.facet_map import FacetMapPostProcessor
from stac_generator.plugins.postprocessors.facet_prefix import FacetPrefixPostProcessor
from stac_generator.plugins.postprocessors.iso_date import ISODatePostProcessor


@pytest.fixture
def fpath():
    return "a/b/c/d.txt"


@pytest.fixture
def body():
    return {"date": "2021-05-02"}


@pytest.fixture
def isodate_processor():
    return ISODatePostProcessor(date_keys=["date"])


@pytest.fixture
def isodate_processor_with_format():
    return ISODatePostProcessor(date_keys=["date"], format="%Y%m")


@pytest.fixture
def facet_map_processor():
    return FacetMapPostProcessor(term_map={"date": "start_date"})


@pytest.fixture
def bbox_processor():
    return BboxPostProcessor(coordinate_keys=["west", "south", "east", "north"])


@pytest.fixture
def facet_prefix_processor():
    return FacetPrefixPostProcessor(prefix="CMIP6", terms=["date"])


def test_isodate_processor(isodate_processor, fpath, body):
    """Check isodate processor does what's expected"""
    expected = body.copy()
    expected["date"] = "2021-05-02T00:00:00"

    output = isodate_processor.run(fpath, body=body)
    assert output == expected


def test_isodate_processor_bad_date(isodate_processor, fpath, caplog):
    """Check isodate processor does what's expected.date

    Conditions:
        - No format string
        - Date string not parsable by dateutil

    Expected:
        - Produce an error
        - Delete the date key
    """
    body = {"date": "202105"}
    expected = {}

    output = isodate_processor.run(fpath, body=body)
    assert output == expected
    assert len(caplog.records) == 2
    assert caplog.records[0].levelname == "ERROR"


def test_isodate_processor_with_good_format(isodate_processor_with_format, fpath):
    """Check isodate processor.
    Conditions:
        - Format string does match date string
        - Date string not parsable by dateutil

    Expected:
        - Successfully use strptime to parse the date
    """

    body = {"date": "202105"}
    expected = body.copy()
    expected["date"] = "2021-05-01T00:00:00"

    output = isodate_processor_with_format.run(fpath, body=body)
    assert output == expected


def test_isodate_processor_with_bad_format(
    isodate_processor_with_format, fpath, caplog
):
    """Check isodate processor.
    Conditions:
        - Format string does not match date string
        - Date string parsable by dateutil

    Expected:
        - Produce warning
        - Successfully Use dateutil to parse the date
    """
    body = {"date": "20210501"}
    expected = body.copy()
    expected["date"] = "2021-05-01T00:00:00"

    output = isodate_processor_with_format.run(fpath, body=body)
    assert output == expected
    assert len(caplog.records) == 2
    assert caplog.records[0].levelname == "WARNING"


def test_isodate_processor_with_bad_format_bad_dateutil(
    isodate_processor_with_format, fpath, caplog
):
    """Check isodate processor.
    Conditions:
        - Format string does not match date string
        - Date string ambiguous and nor parsable by dateutil

    Expected:
        Should delete the date
    """
    body = {"date": "2021010101"}
    expected = {}

    output = isodate_processor_with_format.run(fpath, body=body)
    assert output == expected
    assert len(caplog.records) == 4


def test_facet_map_processor(facet_map_processor, fpath, body):
    """
    Check processor changes name of named facets
    """
    expected = {"start_date": body["date"]}

    output = facet_map_processor.run(fpath, body=body)
    assert output == expected


def test_bbox_processor(bbox_processor, fpath):
    body = {"north": "42.0", "south": "38.0", "east": "-28.0", "west": "-37.0"}

    expected = {
        "bbox": {
            "type": "envelope",
            "coordinates": [
                [
                    float(body["west"]),
                    float(body["south"]),
                ],
                [
                    float(body["east"]),
                    float(body["north"]),
                ],
            ],
        },
        "north": "42.0",
        "south": "38.0",
        "east": "-28.0",
        "west": "-37.0",
    }

    output = bbox_processor.run(fpath, body=body)
    assert output == expected


def test_date_combinator_no_year(fpath, caplog):
    """
    Test that not providing a year results in an error logged
    """
    processor = DateCombinatorPostProcessor()

    body = {"month": "02", "day": "01"}

    processor.run(fpath, body=body)
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "ERROR"


def test_date_combinator(fpath):
    """
    Test can join and produce correct string
    """
    processor = DateCombinatorPostProcessor()

    body = {"year": "1850", "month": "02", "day": "01"}

    expected = {}
    expected["datetime"] = "1850-02-01T00:00:00"

    output = processor.run(fpath, body=body)
    assert output == expected


def test_date_combinator_non_destructive(fpath):
    """
    Test that data is preserved in non-destrictive mode
    """
    processor = DateCombinatorPostProcessor(destructive=False)

    body = {"year": "1850", "month": "02", "day": "01"}

    expected = body.copy()
    expected["datetime"] = "1850-02-01T00:00:00"

    output = processor.run(fpath, body=body)
    assert output == expected


def test_date_combinator_format_string(fpath):
    """
    Test can use format string
    """
    processor = DateCombinatorPostProcessor(format="%Y-%m")

    body = {
        "year": "1850",
        "month": "02",
    }

    expected = {}
    expected["datetime"] = "1850-02-01T00:00:00"

    output = processor.run(fpath, body=body)
    assert output == expected


def test_date_combinator_no_kwargs(fpath):
    """Check that the processor can run with no kwargs."""
    processor = DateCombinatorPostProcessor()

    body = {"year": "1850", "month": "02", "day": "01"}

    expected = {}
    expected["datetime"] = "1850-02-01T00:00:00"

    output = processor.run(fpath, body=body)
    assert output == expected


def test_date_combinator_ym_no_format(fpath, caplog):
    """
    Check that the processor logs an error
    if only year and month are provided with
    no format string.

    Expected:
        Should keep the original data
        Should produce an error log
    """

    processor = DateCombinatorPostProcessor()

    body = {
        "year": "1850",
        "month": "02",
    }

    expected = body.copy()

    output = processor.run(fpath, body=body)
    assert output == expected
    assert len(caplog.records) == 1


def test_facet_prefix_processor(facet_prefix_processor, fpath, body):
    """
    Check processor adds prefix to named facets
    """
    expected = {"CMIP6:date": body["date"]}

    output = facet_prefix_processor.run(fpath, body=body)
    assert output == expected
