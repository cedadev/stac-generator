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

from stac_generator.core.decorators import accepts_postprocessors, accepts_preprocessors
from stac_generator.core.processor import BaseIdExtractionMethod

LOGGER = logging.getLogger(__name__)


class HashExtract(BaseIdExtractionMethod):
    """

    .. list-table::

        * - Processor Name
          - ``hash``
        * - Accepts Pre-processors
          - .. fa:: check
        * - Accepts Post-processors
          - .. fa:: check

    Description:
        Takes list of terms and creates dot seperated string of
        values which is then hashed.

    Configuration Options:
        - ``terms``: Terms to be hashed
        - ``pre_processors``: List of pre-processors to apply
        - ``post_processors``: List of post_processors to apply

    Example configuration:
        .. code-block:: yaml

          id:
            method: hash
            inputs:
              terms:
                  - start_time
                  - model

    """

    def hash(self, id_string: str):
        return hashlib.md5(id_string.encode("utf-8")).hexdigest()

    @accepts_preprocessors
    @accepts_postprocessors
    def run(self, body: dict) -> dict:

        properties = body["properties"]

        if hasattr(self, "terms") and all(
            [facet in self.terms for facet in properties]
        ):
            id_string = ""

            for facet in self.terms:

                vals = properties.get(facet)

                if isinstance(vals, (str, int)):
                    id_string = ".".join((id_string, vals))

                if isinstance(vals, (list)):
                    id_string = ".".join((id_string, f"multi_{facet}"))

            # remove initial '.'
            id_string[1:]

            return hash(id_string)

        elif "collection_id" in self.terms:
            return hash(f"{properties.get('collection_id')}.{properties.get('uri')}")

        else:
            return hash(properties.get("uri"))
