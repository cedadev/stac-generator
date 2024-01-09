__author__ = "Richard Smith"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import logging

# Package imports
from stac_generator.core.extraction_method import BaseExtractionMethod

LOGGER = logging.getLogger(__name__)


class STACBboxExtract(BaseExtractionMethod):
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
              coordinate_keys:
                - west
                - south
                - east
                - north

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if not hasattr(self, "output_term"):
            self.output_term = "bbox"

    def run(self, body: dict, **kwargs):
        try:
            west = body[self.coordinate_keys[0]]
            south = body[self.coordinate_keys[1]]
            east = body[self.coordinate_keys[2]]
            north = body[self.coordinate_keys[3]]

            body[self.output_term] = [
                float(west) if west is not None else west,
                float(south) if south is not None else south,
                float(east) if east is not None else east,
                float(north) if north is not None else north,
            ]

        except KeyError:
            LOGGER.warning("Unable to convert bbox.", exc_info=True)

        return body
