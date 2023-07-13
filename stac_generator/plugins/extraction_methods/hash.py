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


class HashExtract(BaseExtractionMethod):
    """

    .. list-table::

        * - Processor Name
          - ``hash``

    Description:
        Takes list of terms and creates dot seperated string of
        values which is then hashed.

    Configuration Options:
        - ``key``: Key for result to be saved as
        - ``terms``: Terms to be hashed

    Example configuration:
        .. code-block:: yaml

          id:
            method: hash
            inputs:
              key: hashed_terms
              terms:
                  - start_time
                  - model

    """

    def flatten_dict(self, start_dict: dict):
        final_dict = {}
        for k, v in start_dict:
            if isinstance(v, dict):
                final_dict = final_dict | self.flatten_dict(v)
            final_dict[k] = v

    def hash(self, output: str):
        return hashlib.md5(output.encode("utf-8")).hexdigest()

    def run(self, uri: str, body: dict, **kwargs) -> dict:

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

            output = output[1:]

            body[self.key] = self.hash(output)

            return body
