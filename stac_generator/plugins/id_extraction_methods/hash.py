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


class HashIdExtract(BaseIdExtractionMethod):
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

    def flatten_dict(self, start_dict: dict):
        final_dict = {}
        for k, v in start_dict:
            if isinstance(v, dict):
                final_dict = final_dict | self.flatten_dict(v)
            final_dict[k] = v

    def hash(self, id_string: str):
        return hashlib.md5(id_string.encode("utf-8")).hexdigest()

    @accepts_preprocessors
    @accepts_postprocessors
    def run(self, body: dict, **kwargs) -> dict:

        properties = body["properties"]

        if hasattr(self, "terms") and all(
            [facet in properties for facet in self.terms]
        ):
            id_string = ""

            for facet in self.terms:

                vals = properties.get(facet)

                if isinstance(vals, (str, int)):
                    id_string = ".".join((id_string, vals))

                if isinstance(vals, (list)):
                    id_string = ".".join((id_string, f"multi_{facet}"))

            id_string = id_string[1:]

            return self.hash(id_string)

        elif "collection_id" in self.terms:
            return self.hash(f"{properties.get('collection_id')}.{properties.get('uri')}")

        else:
            return self.hash(properties.get("uri"))
