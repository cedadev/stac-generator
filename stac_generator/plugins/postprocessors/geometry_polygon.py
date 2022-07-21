__author__ = "Richard Smith"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import logging

# Python imports
from typing import Optional

# Package imports
from stac_generator.core.processor import BasePostProcessor

LOGGER = logging.getLogger(__name__)


class GeometryPolygonPostProcessor(BasePostProcessor):
    """

    Processor Name: ``polygon_geometry``

    Description:
        Accepts a dictionary of coordinate values and converts to `RFC 7946, <https://tools.ietf.org/html/rfc7946>`_
        formatted geometry.

    Configuration Options:
        - ``coordinate_keys``: ``REQUIRED`` list of keys to convert to polygon geometry. Ordering is respected.

    Example Configuration:

    .. code-block:: yaml

        post_processors:
            - name: polygon_geometry
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

    def run(
        self,
        uri: str,
        source_dict: Optional[dict] = {},
        **kwargs,
    ):

        if source_dict:

            try:

                coordinates = []

                for coordinate_key in self.coordinate_keys:
                    coordinates.append(
                        [
                            float(source_dict[coordinate_key[0]]),
                            float(source_dict[coordinate_key[1]]),
                        ]
                    )

                # Add the first point to the end to complete the shape
                coordinates.append(
                    [
                        float(source_dict[self.coordinate_keys[0][0]]),
                        float(source_dict[self.coordinate_keys[0][1]]),
                    ]
                )

                source_dict["geometry"] = {
                    "type": "Polygon",
                    "coordinates": coordinates,
                }

            except KeyError:
                LOGGER.warning(
                    "Unable to convert to a polygon geometry.", exc_info=True
                )

        return source_dict

    def expected_terms(
        self,
        term_list: Optional[list] = [],
    ) -> list:
        """
        The expected terms to be returned from running the extraction method with the given Collection Description
        :param collection_descrition: CollectionDescription for extraction method
        :param kwargs: free kwargs passed to the processor.
        :return: list
        """

        return term_list.append("geometry")
