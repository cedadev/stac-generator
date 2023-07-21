__author__ = "Richard Smith"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import logging

# Package imports
from stac_generator.core.processor import BaseExtractionMethod
from stac_generator.core.utils import isoformat_date

LOGGER = logging.getLogger(__name__)


class ISODateExtract(BaseExtractionMethod):
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

            - method: isodate_processor
              inputs:
              date_keys:
                - key: date
              format: '%Y%m'

    """

    def run(self, body: dict, **kwargs) -> dict:
        """
        :param body: dict containing the date value

        :return: the source dict with the date converted to ISO8601 format.
        """

        for key in self.date_keys:

            if body.get(key):

                date = body[key]

                date_format = getattr(self, "format", None)

                date, format_errors = isoformat_date(date, date_format)

                if format_errors:
                    LOGGER.warning(
                        f"Could not use format string {date_format} with date from: {body['uri']}"
                    )

                if not date:
                    LOGGER.error(f"Could not extract date from {body['uri']}")
                    body.pop(key)
                else:
                    body[key] = date

            else:
                # Clean up empty strings and non-matches
                body.pop(key, None)

        return body
