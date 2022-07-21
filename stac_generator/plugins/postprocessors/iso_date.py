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
from stac_generator.core.utils import isoformat_date

LOGGER = logging.getLogger(__name__)


class ISODatePostProcessor(BasePostProcessor):
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
        source_dict: Optional[dict] = {},
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

        return term_list
