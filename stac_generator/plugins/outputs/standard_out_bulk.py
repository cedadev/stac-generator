# encoding: utf-8
"""
Standard Out
------------

An output backend which outputs the generated metadata to standard out.
Useful for testing and debugging.

**Plugin name:** ``standard_out``

.. list-table::
    :header-rows: 1

    * - Option
      - Value Type
      - Description

Example configuration:
    .. code-block:: yaml

        outputs:
            - method: standard_out
"""
__author__ = "Richard Smith"
__date__ = "01 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import json

from cachetools import Cache

from stac_generator.core.output import BaseOutput


class StandardOutBulkOutput(BaseOutput):
    """
    Simple print backend which can be used
    for testing and debugging.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.message_cache = Cache(maxsize=getattr(self, "cache_max_size", 100) + 1)

    def clear_cache(self):
        print(
            "This is a bulk one",
            json.dumps(list(self.message_cache.items()), indent=4),
        )

        self.message_cache.clear()

    def export(self, data: dict, **kwargs):
        """
        Export the data to rabbit.

        :param data: expected data as header dict
        """
        id = data["id"]
        # add to cache
        self.message_cache.update({id: data})

        # check cache is full
        cache_size = self.message_cache.currsize

        if cache_size >= getattr(self, "cache_max_size", 100):
            # empty cache

            self.clear_cache()

    def finished(self, **kwargs):
        """
        Empty cache when input has finished.
        """

        self.clear_cache()
