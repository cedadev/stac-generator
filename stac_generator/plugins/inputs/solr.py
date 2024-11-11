"""
Solr Input
----------

Uses a Solr index node for a source for file
objects.

**Plugin name:** ``solr``

.. list-table::
    :header-rows: 1

    * - Option
      - Value Type
      - Description
    * - ``index_node``
      - string
      - ``REQUIRED`` Solr index
    * - ``search_params``
      - dict
      - request params to send to Solr


Example Configuration:
    .. code-block:: yaml

        inputs:
            - method: solr
              index_node: url.index-node.ac.uk
              search_params:
                q: "facet: value"
                rows: 10000
"""

__author__ = "Mahir Rahman"
__date__ = "23 Mar 2022"
__copyright__ = "Copyright 2022 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "kazi.mahir@stfc.ac.uk"

import logging
import sys

import requests
from extraction_methods.core.extraction_method import KeyOutputKey
from pydantic import BaseModel, Field

# Package imports
from stac_generator.core.input import Input

LOGGER = logging.getLogger(__name__)


class SolarParams(BaseModel):
    """Solar parameters model."""

    indent: str = Field(
        default="on",
        description="indent.",
    )
    q: str = Field(
        default="*:*",
        description="query.",
    )
    wt: str = Field(
        default="json",
        description="wt.",
    )
    rows: int = Field(
        default=10000,
        description="Number of rows.",
    )
    sort: str = Field(
        default="id asc",
        description="sort.",
    )
    cursorMark: str = Field(
        default="*",
        description="cursor mark.",
    )


class SolrConf(BaseModel):
    """Solar conf."""

    url: str = Field(
        description="URL of datastore.",
    )
    params: SolarParams = Field(
        description="Parameters to pass to solr.",
    )
    extra_terms: list[KeyOutputKey] = Field(
        default=[],
        description="List of extra attributes.",
    )


class SolrInput(Input):

    config_class = SolrConf

    def iter_docs(self):
        """
        Core loop to iterate through the Solr response.
        """
        n = 0
        while True:
            try:
                resp = requests.get(self.conf.url, self.conf.params.dict())
            except requests.exceptions.ConnectionError as e:
                LOGGER.error("Failed to establish connection to %s:\n%s", self.conf.url, e)
                sys.exit(1)

            resp = resp.json()
            docs = resp["response"]["docs"]

            # Return the list of files to the for loop and continue paginating
            yield from docs

            n += len(docs)
            LOGGER.info("%s/%s\n", n, resp["response"]["numFound"])
            if not docs:
                LOGGER.error("no docs found")
                break
            LOGGER.info("Next cursormark at position %s", n)

            # Change the search params to get next page.
            self.conf.params.cursorMark = resp["nextCursorMark"]

    def run(self):
        for doc in self.iter_docs():
            uri: str = doc.get("id")

            LOGGER.info("Input processing: %s", uri)

            # transform id to a uri
            # by replacing '.' with '/' up until the filename
            output = {"uri": uri.replace(".", "/", uri.split("|")[0].count(".") - 1)}

            for extra_term in self.conf.extra_terms:
                output[extra_term.output_key] = doc.get(extra_term.key)

            yield output
