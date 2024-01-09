__author__ = "Richard Smith"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import logging
from datetime import datetime

# Package imports
from stac_generator.core.extraction_method import BaseExtractionMethod

LOGGER = logging.getLogger(__name__)


class DatetimeBoundToCentroidExtract(BaseExtractionMethod):
    """

    Processor Name: ``datetime_bound_to_centroid``

    Description:
        Accepts a dictionary of coordinate values and converts to `RFC 7946, section 5 <https://tools.ietf.org/html/rfc7946#section-5>`_
        formatted bbox.

    Configuration Options:
        - ``coordinate_keys``: ``REQUIRED`` list of keys to convert to bbox array. Ordering is respected.

    Example Configuration:

    .. code-block:: yaml

        - method: stac_bbox
            inputs:
              output_term: polygon

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if not hasattr(self, "start_term"):
            self.start_term = {"name": "start_datetime", "format": "%Y-%m-%dT%H:%M:%S"}

        if "name" not in self.start_term:
            self.start_term["name"] = "start_datetime"

        if "format" not in self.start_term:
            self.start_term["format"] = "%Y-%m-%dT%H:%M:%S"

        if not hasattr(self, "end_term"):
            self.end_term = {"name": "end_datetime", "format": "%Y-%m-%dT%H:%M:%S"}

        if "name" not in self.end_term:
            self.end_term["name"] = "start_datetime"

        if "format" not in self.end_term:
            self.end_term["format"] = "%Y-%m-%dT%H:%M:%S"

        if not hasattr(self, "output_term"):
            self.output_term = {"name": "datetime", "format": "%Y-%m-%dT%H:%M:%S"}

        if "name" not in self.output_term:
            self.output_term["name"] = "datetime"

        if "format" not in self.output_term:
            self.output_term["format"] = "%Y-%m-%dT%H:%M:%S"

    def run(self, body: dict, **kwargs):

        start_datetime = datetime.strptime(
            body[self.start_term["name"]], self.start_term["format"]
        )
        end_datetime = datetime.strptime(
            body[self.end_term["name"]], self.end_term["format"]
        )

        centroid_datetime = start_datetime + (end_datetime - start_datetime) / 2

        body[self.output_term["name"]] = centroid_datetime.strftime(
            self.output_term["format"]
        )

        return body
