# encoding: utf-8
"""
..  _regex:

Regex
------
"""
__author__ = "Richard Smith"
__date__ = "27 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


# Python imports
import hashlib
import logging

from stac_generator.core.processor import BaseExtractionMethod

LOGGER = logging.getLogger(__name__)


class DotSeperatedStrExtract(BaseExtractionMethod):
    """

    .. list-table::

        * - Processor Name
          - ``hash``

    Description:
        Takes list of terms and creates dot seperated string of
        values.

    Configuration Options:
        - ``key``: Key for result to be saved as
        - ``terms``: Terms to be dot seperated

    Example configuration:
        .. code-block:: yaml

          id:
            method: hash
            inputs:
              output_key: dot_terms
              terms:
                  - start_time
                  - model

    """

    def run(self, body: dict, **kwargs) -> dict:

        if hasattr(self, "terms"):
            output = ""

            for facet in self.terms:

                if facet in body:
                    vals = body.get(facet)

                    if isinstance(vals, (str, int)):
                        output = ".".join((output, vals))

                    if isinstance(vals, (list)):
                        if len(vals) == 1:
                            output = ".".join((output, vals[0]))
                        elif len(vals) != 0:
                            output = ".".join((output, f"multi_{facet}"))

            body[self.output_key] = output[1:]

            return body
