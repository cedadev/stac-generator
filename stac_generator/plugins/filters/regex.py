# encoding: utf-8
"""
Regex Filter
-----------------

Takes a uri and matches against a regex pattern. This can be used to pre-filter
uris for processing. Can use the ``exclude`` flag to flip the regex match.

**Plugin name:** ``regex``

.. list-table::
    :header-rows: 1

    * - Option
      - Value Type
      - Description
    * - ``regex``
      - ``string``
      - ``REQUIRED`` Pattern to match.
    * - ``exclude``
      - ``bool``
      - Optional flag to either include or exclude the matched path. False will send only paths that match to processing. True
        will send all paths which do not match the regex for processing. ``DEFAULT: False``

Example Configuration:
    .. code-block:: yaml

        inputs:
            - method: file_system
              path: /badc/cmip5
              filters:
                - method: regex
                  regex: ^\/badc\/cmip[56]\/.*files
                  exclude: True

# noqa: W605
"""
__author__ = "Richard Smith"
__date__ = "20 Sep 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import re
from distutils.util import strtobool


class RegexFilter:
    def __init__(self, **kwargs):
        self.regex = rf"{kwargs['regex']}"
        self.exclude = strtobool(kwargs.get("exclude", "False"))

    def run(self, uri: str) -> bool:
        if self.exclude:
            return not bool(re.match(self.regex, uri))
        else:
            return bool(re.match(self.regex, uri))
