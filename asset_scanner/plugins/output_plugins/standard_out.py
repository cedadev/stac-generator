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
    * - ``namespace``
      - ``str``
      - Can be used by downstream processors to separate outputs.

Example configuration:
    .. code-block:: yaml

        outputs:
            - name: standard_out
"""
__author__ = 'Richard Smith'
__date__ = '01 Jun 2021'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from .base import OutputBackend


class StdoutOutputBackend(OutputBackend):
    """
    Simple print backend which can be used
    for testing and debugging.
    """

    def export(self, data: dict, **kwargs) -> None:
        """
        Print the received data.

        :param data: Data from extraction process
        :param kwargs: Not used
        """
        print(data)
