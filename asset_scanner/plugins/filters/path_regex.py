# encoding: utf-8
"""
Path Regex Filter
-----------------

Takes a filepath and matches against a regex pattern. This can be used to pre-filter
paths for processing. Can use the ``exclude`` flag to flip the regex match.

**Plugin name:** ``path_regex``

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
      - Optional flag to either include or exclude the matched path. False (0) will send only paths that match to processing. True (1)
        will send all paths which do not match the regex for processing. ``DEFAULT: False``

Example Configuration:
    .. code-block:: yaml

        filters:
            - name: path_regex
              regex: ^\/badc\/cmip[56]\/.*files
              exclude: 1

"""
__author__ = 'Richard Smith'
__date__ = '20 Sep 2021'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

import re


class PathRegexFilter:

    def __init__(self, **kwargs):
        self.regex = kwargs['regex']
        self.exclude = kwargs.get('exclude', 0)

    def run(self, filepath: str, source_media: str) -> bool:
        if self.exclude:
            return not bool(re.match(self.regex, filepath))
        else:
            return bool(re.match(self.regex, filepath))
