# encoding: utf-8
"""

"""
__author__ = "Richard Smith"
__date__ = "03 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

# Package imports

import logging
import re

# Python imports
from datetime import datetime
from string import Template
from typing import Optional, Tuple

# 3rd party imports
from dateutil.parser import parse

LOGGER = logging.getLogger(__name__)

DATE_TEMPLATE = Template("${year}-${month}-${day}T${hour}:${minute}:${second}")


def is_remote_uri(path: str) -> bool:
    """Finds URLs of the form protocol:// or protocol::
    This also matches for http[s]://, which were the only remote URLs
    supported in <=v0.16.2.
    """
    return bool(re.search(r"^[a-z][a-z0-9]*(\://|\:\:)", path))


def isoformat_date(date_string: str, format=None) -> Tuple[Optional[str], bool]:
    """
    Return the date string in ISO 8601 format.

    :param date_string: date string to parse
    :param format: Optional format string to try against the date string
    :return:
        possible return values:
            - None, True: Format string supplied. Unable to parse date using format string or dateutil.parser.parse
            - None, False: No format string supplied. Tried dateutil.parser.parse and failed
            - str, True: Format string supplied and failed to parse date. Date successfully parsed by dateutil.parser.parse
            - str, False: Either the format string or date parser worked successfully.
    """

    output_date = None
    format_errors = False

    try:
        # If there is a specified format, try that. Else
        # use generic parser
        if format:
            output_date = datetime.strptime(date_string, format).isoformat()
        else:
            output_date = parse(date_string).isoformat()
    except ValueError as e:
        if format:
            format_errors = True
            LOGGER.warning(
                f"Could not parse {date_string} with format {format}. {e}\n"
                f"Trying dateutil..."
            )
        else:
            LOGGER.error(f"Error parsing {date_string} with dateutil. {e}")

    # Tried specific format but this failed. Try generic parser.
    if format_errors:
        try:
            output_date = parse(date_string).isoformat()
        except ValueError as e:
            LOGGER.error(f"Error parsing {date_string} with dateutil. {e}")

    return output_date, format_errors
