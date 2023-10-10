__author__ = "Richard Smith"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import logging

# Package imports
from stac_generator.core.extraction_method import BaseExtractionMethod

LOGGER = logging.getLogger(__name__)


class GeometryPolygonExtract(BaseExtractionMethod):
    """

    Processor Name: ``geometry_polygon``

    Description:
        Accepts a dictionary of coordinate values and converts to `RFC 7946, <https://tools.ietf.org/html/rfc7946>`_
        formatted geometry.

    Configuration Options:
        - ``coordinates_term``: term for coordinates to convert to polygon geometry.
        - ``coordinate_keys``: list of keys to convert to polygon geometry. Ordering is respected.

    Example Configuration:

    .. code-block:: yaml

        - method: geometry_polygon
          inputs:
          coordinate_keys:
            -
              - lon_1
              - lat_1
            -
              - lon_2
              - lat_2
            -
              - lon_3
              - lat_3
    """

    def run(self, body: dict, **kwargs):
        try:
            coordinates = []

            if hasattr(self, "coordinates_term"):
                coordinates = body[self.coordinates_term]

            elif hasattr(self, "coordinate_keys"):
                for coordinate_key in self.coordinate_keys:
                    coordinates.append(
                        [
                            float(body[coordinate_key[0]]),
                            float(body[coordinate_key[1]]),
                        ]
                    )

            if coordinates[0] != coordinates[-1]:
                # Add the first point to the end to complete the shape
                coordinates.append(coordinates[0])

            body["geometry"] = {
                "type": "Polygon",
                "coordinates": coordinates,
            }

        except KeyError:
            LOGGER.warning("Unable to convert to a polygon geometry.", exc_info=True)

        return body
