__author__ = "Richard Smith"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import logging

# Package imports
from stac_generator.core.extraction_method import BaseExtractionMethod
from datetime import datetime

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
                - date
              formats:
                - '%Y%m'

    """

    def run(self, body: dict, **kwargs) -> dict:
        """
        :param body: dict containing the date value

        :return: the source dict with the date converted to ISO8601 format.
        """

        for date_key in self.date_keys:
            date_str = body.get(date_key)
            date_iso = None

            if not date_str:
                LOGGER.error(f"{date_key} not present in body for {body.get('uri', body.get('href'))}")
            
            else:

                if hasattr(self, "formats"):
                
                    for date_format in self.formats:
                        try:
                            date_iso = datetime.strptime(date_str, date_format).isoformat()

                        except ValueError:
                            pass

                else:
                    date_iso = datetime.strptime(date_str).isoformat()

                if date_iso:
                    body[date_key] = date_iso

        return body
