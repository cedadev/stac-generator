# encoding: utf-8
"""
Standard Out
------------

An bulk output which outputs the generated metadata to standard out.
Useful for testing and debugging.

**Plugin name:** ``standard_out_bulk``

.. list-table::
    :header-rows: 1

    * - Option
      - Value Type
      - Description

Example configuration:
    .. code-block:: yaml

        outputs:
            - method: standard_out_bulk
              cache_max_size: 10
"""
__author__ = "Richard Smith"
__date__ = "01 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import json

from cachetools import Cache

from stac_generator.core.bulk_output import BaseBulkOutput


class StandardOutBulkOutput(BaseBulkOutput):
    """
    Simple bulk print backend which can be used
    for testing and debugging.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.message_cache = Cache(maxsize=getattr(self, "cache_max_size", 100) + 1)

    def export(self, data_list: list):
        """
        Print the data if cache is full.

        :param data: expected data
        """
        print(json.dumps(data_list, indent=4))
