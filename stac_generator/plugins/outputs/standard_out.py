# encoding: utf-8
__author__ = "Richard Smith"
__date__ = "01 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import pprint

from stac_generator.core.output import Output


class StandardOutOutput(Output):
    """
    Output to standard out.
    Useful for testing and debugging.

    **Plugin name:** ``standard_out``

    Example configuration:
        .. code-block:: yaml

            - name: standard_out
    """

    def export(self, data: dict, **kwargs) -> None:
        """
        Print the received data.

        :param data: Data from extraction process
        :param kwargs: Not used
        """
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(data)
