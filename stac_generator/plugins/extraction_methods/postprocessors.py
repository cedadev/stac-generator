# encoding: utf-8
"""
Post processors operate on the output from a main processor.
They are used using the same interface as a main processor ``process``
but they accept the result of the previous step as part of the ``process`` signature.
"""
__author__ = "Richard Smith"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import logging

# Python imports
from abc import abstractmethod
from typing import Optional

from stac_generator.core.decorators import accepts_output_key

# Package imports
from stac_generator.core.processor import BaseProcessor

from .utils import DATE_TEMPLATE, isoformat_date

LOGGER = logging.getLogger(__name__)


class BasePostProcessor(BaseProcessor):
    @accepts_output_key
    @abstractmethod
    def run(
        self,
        uri: str,
        source_dict: Optional[dict] = None,
        **kwargs,
    ) -> dict:
        pass


class FacetMapProcessor(BasePostProcessor):
    """

    Processor Name: ``facet_map``

    Description:
        In some cases, you may wish to map the header attributes to different
        facets. This method takes a map and converts the facet labels into those
        specified.

    Configuration Options:
        - ``term_map``: Dictionary of terms to map

    Example Configuration:

    .. code-block:: yaml

        post_processors:
            - method: facet_map
              inputs:
                term_map:
                    time_coverage_start: start_time

    """

    def run(
        self,
        uri: str,
        source_dict: Optional[dict] = None,
        **kwargs,
    ) -> dict:
        output = {}
        if source_dict:

            for k, v in source_dict.items():

                new_key = self.term_map.get(k)
                if new_key:
                    output[new_key] = v
                else:
                    output[k] = v

        return output


class ISODateProcessor(BasePostProcessor):
    """

    Processor Name: ``isodate_processor``

    Description:
        Takes the source dict and the key to access the date and
        converts the date to ISO 8601 Format.

        e.g.

        ``YYYY-MM-DDTHH:MM:SS.ffffff``, if microsecond is not 0
        ``YYYY-MM-DDTHH:MM:SS``, if microsecond is 0

        If the date format cannot be parsed, it is removed from the source dict with
        an error logged.

    Configuration Options:
        - ``date_keys``: `REQUIRED` List keys to the date value. Using a list allows processing of multiple dates.
        - ``format``: Optional format string. Default behaviour uses `dateutil.parser.parse <https://dateutil.readthedocs.io/en/stable/parser.html#dateutil.parser.parse>`_.
          If a format string is suppled, this will change to use `datetime.datetime.strptime <https://docs.python.org/3/library/datetime.html#datetime.datetime.strptime>`_.

    Example Configuration:

        .. code-block:: yaml

            post_processors:
                - method: isodate_processor
                  inputs:
                    date_keys:
                      - key: date
                    format: '%Y%m'

    """

    def run(
        self,
        uri: str,
        source_dict: Optional[dict] = None,
        **kwargs,
    ) -> dict:
        """
        :param uri: file currently being processed
        :param source_media: media source of the file being processed
        :param source_dict: dict containing the date value

        :return: the source dict with the date converted to ISO8601 format.
        """
        if source_dict:

            for key in self.date_keys:
                if source_dict.get(key):
                    date = source_dict[key]

                    date_format = getattr(self, "format", None)

                    date, format_errors = isoformat_date(date, date_format)

                    if format_errors:
                        LOGGER.warning(
                            f"Could not use format string {date_format} with date from: {uri}"
                        )

                    if not date:
                        LOGGER.error(f"Could not extract date from {uri}")
                        source_dict.pop(key)
                    else:
                        source_dict[key] = date

                else:
                    # Clean up empty strings and non-matches
                    source_dict.pop(key, None)

        return source_dict


class BBOXProcessor(BasePostProcessor):
    """

    Processor Name: ``bbox``

    Description:
        Accepts a dictionary of coordinate values and converts to `RFC 7946, section 5 <https://tools.ietf.org/html/rfc7946#section-5>`_
        formatted bbox.

    Configuration Options:
        - ``coordinate_keys``: ``REQUIRED`` list of keys to convert to bbox array. Ordering is respected.

    Example Configuration:

    .. code-block:: yaml

        post_processors:
            - method: bbox
              inputs:
                coordinate_keys:
                   - west
                   - south
                   - east
                   - north

    """

    def run(
        self,
        uri: str,
        source_dict: dict = {},
        **kwargs,
    ):

        if source_dict:

            try:
                coordinates = [
                    [
                        float(source_dict[self.coordinate_keys[0]]),
                        float(source_dict[self.coordinate_keys[1]]),
                    ],
                    [
                        float(source_dict[self.coordinate_keys[2]]),
                        float(source_dict[self.coordinate_keys[3]]),
                    ],
                ]

                source_dict["bbox"] = {
                    "type": "envelope",
                    "coordinates": coordinates,
                }

            except KeyError:
                LOGGER.warning("Unable to convert bbox.", exc_info=True)

        return source_dict


class GeometryPointProcessor(BasePostProcessor):
    """

    Processor Name: ``point_geometry``

    Description:
        Accepts a dictionary of coordinate values and converts to `RFC 7946, <https://tools.ietf.org/html/rfc7946>`_
        formatted geometry.

    Configuration Options:
        - ``coordinate_keys``: ``REQUIRED`` list of keys to convert to a point geometry. Ordering is respected.

    Example Configuration:

    .. code-block:: yaml

        post_processors:
            - name: point_geometry
              inputs:
                coordinate_keys:
                   - lon
                   - lat

    """

    def run(
        self,
        uri: str,
        source_dict: dict = {},
        **kwargs,
    ):

        if source_dict:

            try:

                coordinates = [
                    float(source_dict[self.coordinate_keys[0]]),
                    float(source_dict[self.coordinate_keys[1]]),
                ]

                source_dict["geometry"] = {
                    "type": "Point",
                    "coordinates": coordinates,
                }

            except KeyError:
                LOGGER.warning("Unable to convert to point geometry.", exc_info=True)

        return source_dict


class GeometryLineProcessor(BasePostProcessor):
    """

    Processor Name: ``line_geometry``

    Description:
        Accepts a dictionary of coordinate values and converts to `RFC 7946, <https://tools.ietf.org/html/rfc7946>`_
        formatted geometry.

    Configuration Options:
        - ``coordinate_keys``: ``REQUIRED`` list of keys to convert to line geometry. Ordering is respected.

    Example Configuration:

    .. code-block:: yaml

        post_processors:
            - name: line_geometry
              inputs:
                coordinate_keys:
                -
                  - lon_1
                  - lat_1
                -
                  - lon_2
                  - lat_2

    """

    def run(
        self,
        uri: str,
        source_dict: dict = {},
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

                source_dict["geometry"] = {
                    "type": "Line",
                    "coordinates": coordinates,
                }

            except KeyError:
                LOGGER.warning("Unable to convert to a line geometry.", exc_info=True)

        return source_dict


class GeometryPolygonProcessor(BasePostProcessor):
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
        source_dict: dict = {},
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


class StringJoinProcessor(BasePostProcessor):
    """

    Processor Name: ``string_join``

    Description:
        Accepts a dictionary. String values are popped from the dictionary and
        are put back into the dictionary with the ``key`` specified.

    Configuration Options:
        - ``key_list``: ``REQUIRED`` list of keys to convert to bbox array. Ordering is respected.
        - ``delimiter``: ``REQUIRED`` text delimiter to put between strings
        - ``key``: ``REQUIRED`` name of the key you would like to output

    Example Configuration:


    .. code-block:: yaml

        post_processors:
            - method: string_join
              inputs:
                key_list:
                   - year
                   - month
                   - day
                delimiter: "-"
                key: datetime

    """

    def run(
        self,
        uri: str,
        source_dict: dict = {},
        **kwargs,
    ):
        if source_dict:

            try:
                string_elements = [str(source_dict.pop(key)) for key in self.key_list]
                source_dict[self.key] = self.delimiter.join(string_elements)
            except KeyError:
                LOGGER.warning(f"Unable merge strings. file: {uri}", exc_info=True)

        return source_dict


class DateCombinatorProcessor(BasePostProcessor):
    """

    Processor Name: ``date_combinator``

    Description:
        Used to automatically join date components to create an ISO 8601 date.
        E.g.
        - year (required)
        - month
        - day
        - hour
        - minutes
        - seconds

        .. note::

            If you are only expecting to extract <year>-<month> make sure to include
            a format string. Dateutil.parser.parse will use the current day to fill the
            blank rather than 01. e.g. ``2021-03`` -> ``2021-03-29T00:00:00``. Using format: ``%Y-%m`` will
            result in ``2021-03`` -> ``2021-03-01T00:00:00``.

    Configuration Options:
        - ``destructive``: Whether the keys are removed from the output when combined. ``DEFAULT: true``
        - ``key``: Name of the key you would like to output. ``DEFAULT: datetime``
        - ``format``: Format string to parse date to isodate. Date template is: ``${year}-${month}-${day}T${hour}:${minute}:${second}``
          The format string is passed to `datetime.datetime.strptime <https://docs.python.org/3/library/datetime.html#datetime.datetime.strptime>`_

    Example Configuration:

    .. code-block:: yaml

        post_processors:
            - method: date_combinator
              inputs:
                destructive: true
                format: '%Y-%m'
                key: datetime

    """

    def run(
        self,
        uri: str,
        source_dict: Optional[dict] = None,
        **kwargs,
    ):
        if source_dict:

            if not source_dict.get("year"):
                LOGGER.error(
                    f'Unable to use date combinator for file: {uri}. Requires at least "year"'
                )
                return source_dict

            date_format = getattr(self, "format", None)

            if not all(k in source_dict for k in ["year", "month", "day"]):
                if not date_format:
                    LOGGER.error(
                        "Dateutil does not perform as expected without a day. It will use the current day instead of 01."
                        "Make sure to use a format string if only providing %Y-%m"
                    )
                    return source_dict

            # Template the date. safe_substitute allows missing and extra keys.
            date = DATE_TEMPLATE.safe_substitute(**source_dict)

            # Trim the resulting string to remove un-filled template parameters
            try:
                trim_index = date.index("$")
                date = date[0 : trim_index - 1]
            except ValueError:
                # $ not found in date string so fully templated
                ...

            # ISO8601 format the date
            isodate, format_errors = isoformat_date(date, date_format)

            if format_errors:
                LOGGER.warning(
                    f"Error parsing date from file: {uri} with format: {self.format}."
                    "Trying dateutil..."
                )
            if not isodate:
                LOGGER.error(f"Error parsing date from file: {uri}")

            key = getattr(self, "key", "datetime")
            source_dict[key] = isodate or date

            # Clear out keys if destructive
            if getattr(self, "destructive", True):
                for key in ["year", "month", "day", "hour", "minute", "second"]:
                    source_dict.pop(key, None)

        return source_dict


class FacetPrefixProcessor(BasePostProcessor):
    """

    Processor Name: ``facet_prefix``

    Description:
        In some cases, you may wish add a prefix to some or all of the facets
        based on the vocabulary they're from.

    Configuration Options:
        - ``prefix``: Prefix to be added
        - ``terms``: List of terms that require prefix

    Example Configuration:

    .. code-block:: yaml

        post_processors:
            - method: facet_prefix
              inputs:
                prefix:
                  cmip6
                terms:
                    - start_time
                    - model

    """

    def run(
        self,
        uri: str,
        source_dict: Optional[dict] = None,
        **kwargs,
    ) -> dict:
        output = {}
        if source_dict:

            for k, v in source_dict.items():
                if k in self.terms:
                    output[f"{self.prefix}:{k}"] = v
                else:
                    output[k] = v

        return output
