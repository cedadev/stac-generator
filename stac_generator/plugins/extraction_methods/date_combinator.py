__author__ = "Richard Smith"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import logging

# Package imports
from stac_generator.core.processor import BaseExtractionMethod
from stac_generator.core.utils import DATE_TEMPLATE, isoformat_date

LOGGER = logging.getLogger(__name__)


class DateCombinatorExtract(BaseExtractionMethod):
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

        - method: date_combinator
          inputs:
          destructive: true
          format: '%Y-%m'
          key: datetime

    """

    def run(self, body: dict, **kwargs):
        if body:

            if not body.get("year"):
                LOGGER.error(
                    f'Unable to use date combinator for file: {body["uri"]}. Requires at least "year"'
                )
                return body

            date_format = getattr(self, "format", None)

            if not all(k in body for k in ["year", "month", "day"]):
                if not date_format:
                    LOGGER.error(
                        "Dateutil does not perform as expected without a day. It will use the current day instead of 01."
                        "Make sure to use a format string if only providing %Y-%m"
                    )
                    return body

            # Template the date. safe_substitute allows missing and extra keys.
            date = DATE_TEMPLATE.safe_substitute(**body)

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
                    f"Error parsing date from file: {body["uri"]} with format: {self.format}."
                    "Trying dateutil..."
                )
            if not isodate:
                LOGGER.error(f"Error parsing date from file: {body["uri"]}")

            key = getattr(self, "key", "datetime")
            body[key] = isodate or date

            # Clear out keys if destructive
            if getattr(self, "destructive", True):
                for key in ["year", "month", "day", "hour", "minute", "second"]:
                    body.pop(key, None)

        return body
