# encoding: utf-8
"""
Thredds Input
-----------------

Uses a `Thredds Data Server <https://www.unidata.ucar.edu/software/tds/current/>`_
as a source.

**Plugin name:** ``thredds``

.. list-table::
    :header-rows: 1

    * - Option
      - Value Type
      - Description
    * - ``uri``
      - ``string``
      - ``REQUIRED`` The URL to a Thredds Data Server.
    * - ``object_path_attr``
      - ``string``
      - ``REQUIRED`` The column header which contains the URI to
        the file object.
    * - ``catalog_kwargs``
      - ``dict``
      - Optional kwargs to pass to
        `siphon.catalog.TDSCatalog
        <https://unidata.github.io/siphon/latest/api/catalog.html#siphon.catalog.TDSCatalog>`_


Example Configuration with OPENDAP:
    .. code-block:: yaml

        inputs:
            - method: thredds
              uri: test-url
              object_path_attr: access_urls.OPENDAP

Example Configuration with NCML:
    .. code-block:: yaml

        inputs:
            - name: thredds
              uri: test-url
              object_path_attr: access_urls.NCML

"""
__author__ = "Mathieu Provencher"
__date__ = "3 Dec 2021"
__copyright__ = "Copyright 2021 Computer Research Institute of Montreal"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "mathieu.provencher@crim.ca"

import logging

# Python imports
from collections.abc import Iterator
from datetime import datetime

from extraction_methods.core.extraction_method import KeyOutputKey
from pydantic import BaseModel, Field

# Thirdparty imports
from siphon.catalog import CaseInsensitiveDict, TDSCatalog

# Package imports
from stac_generator.core.input import Input

logger = logging.getLogger(__name__)


class ThreddsConf(BaseModel):
    """Thredds Config."""

    url: str = Field(
        description="URL of Thredds server.",
    )
    depth: int = Field(
        default=1000,
        description="Depth of catalog walk.",
    )
    uri_term: str = Field(
        description="Attritube to use as uri.",
    )
    extra_terms: list[KeyOutputKey] = Field(
        default=[],
        description="List of extra attributes.",
    )


class ThreddsInput(Input):
    """
    Process each dataset underneath a TDS catalog.
    """

    config_class = ThreddsConf

    def walk_tds(self, catalog: TDSCatalog, depth: int) -> Iterator:
        """
        Return a generator walking a THREDDS data catalog for datasets.

        :param cat: THREDDS catalog.
        :param depth: Maximum recursive depth.
        """
        yield from catalog.datasets.items()

        if depth > 0:
            for _, ref in catalog.catalog_refs.items():
                child = ref.follow()
                yield from self.walk_tds(catalog=child, depth=depth - 1)

    def get_sub_attr(self, obj: object, path: str):
        """
        Returns a child or sub-child attribute of a dict object.

        :param obj: Object
        :param path: 'attr1.attr2.etc'
        :return: obj.attr1.attr2.etc
        """
        attrs = path.split(".")

        for attr in attrs:
            if isinstance(obj, CaseInsensitiveDict):
                obj = obj[attr]
                continue

            obj = getattr(obj, attr)

        return obj

    def run(self):
        """
        Plugin's entrypoint.

        """
        total_generated = 0
        start = datetime.now()

        catalog = TDSCatalog(self.conf.url, **self.conf.thredds_kwargs)

        for _, dataset in self.walk_tds(catalog=catalog, depth=self.conf.depth):
            output = {"uri": self.get_sub_attr(dataset, self.conf.uri_term)}

            for extra_term in self.conf.extra_terms:
                output[extra_term.output_key] = self.get_sub_attr(dataset, extra_term.key)

            yield output
            total_generated += 1

        end = datetime.now()
        print(f"Processed {total_generated} records from {self.conf.url} in {end - start}")
