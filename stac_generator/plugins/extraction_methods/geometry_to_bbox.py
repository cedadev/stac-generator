__author__ = "Richard Smith"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import logging

# Package imports
from stac_generator.core.extraction_method import BaseExtractionMethod

LOGGER = logging.getLogger(__name__)


class GeometryToBboxExtract(BaseExtractionMethod):
    """

    Processor Name: ``bbox``

    Description:
        Accepts a dictionary of coordinate values and converts to `RFC 7946, section 5 <https://tools.ietf.org/html/rfc7946#section-5>`_
        formatted bbox.

    Configuration Options:
        - ``coordinate_keys``: ``REQUIRED`` list of keys to convert to bbox array. Ordering is respected.

    Example Configuration:

    .. code-block:: yaml

        - method: stac_bbox
            inputs:
              type: polygon

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if not hasattr(self, "input_term"):
            self.input_term = "geometry"

        if not hasattr(self, "output_term"):
            self.output_term = "bbox"

    def run(self, body: dict, **kwargs):

        coordinates = body[self.input_term]["coordinates"][0]
        bbox = [
            coordinates[0][0],
            coordinates[0][1],
            coordinates[0][0],
            coordinates[0][1],
        ]

        if self.type in ["polygon", "line"]:
            for coordinate in coordinates:

                if coordinate[0] < bbox[0]:
                    bbox[0] = coordinate[0]

                elif coordinate[0] > bbox[2]:
                    bbox[2] = coordinate[0]

                if coordinate[1] < bbox[1]:
                    bbox[1] = coordinate[1]

                elif coordinate[1] > bbox[3]:
                    bbox[3] = coordinate[1]

        body[self.output_term] = bbox

        return body
