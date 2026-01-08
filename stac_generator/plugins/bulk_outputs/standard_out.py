# encoding: utf-8
__author__ = "Richard Smith"
__date__ = "01 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import json

from stac_generator.core.bulk_output import BulkOutput


class StandardOutBulkOutput(BulkOutput):
    """
    Outputs to standard out.
    Useful for testing and debugging.

    **Plugin name:** ``standard_out_bulk``

    Example configuration:
        .. code-block:: yaml

            - name: standard_out_bulk
              conf:
                cache_max_size: 10
    """

    def export(self, data_list: list) -> None:
        """
        Print the data if cache is full.

        :param data: expected data
        """
        print(json.dumps(data_list, indent=4))
