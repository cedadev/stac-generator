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
__copyright__ = "Copyright 2021 Computer Research Institute of Montréal"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "mathieu.provencher@crim.ca"

# Python imports
import logging
from datetime import datetime

# Thirdparty imports
from siphon.catalog import CaseInsensitiveDict, TDSCatalog

from stac_generator.core.generator import BaseGenerator

# Package imports
from stac_generator.core.input import BaseInput

logger = logging.getLogger(__name__)


def walk_tds(cat: TDSCatalog, depth: int = 1):
    """
    Return a generator walking a THREDDS data catalog for datasets.

    :param cat: THREDDS catalog.
    :param depth: Maximum recursive depth. Setting 0 will return only datasets within the top-level catalog. If None,
      depth is set to 1000.
    """
    yield from cat.datasets.items()

    if depth is None:
        depth = 1000

    if depth > 0:
        for name, ref in cat.catalog_refs.items():
            child = ref.follow()
            yield from walk_tds(child, depth=depth - 1)


def get_sub_attr(obj: object, path: str):
    """
    Returns a child or sub-child attribute of a dict object.

    :param obj: Object
    :param path: 'attr1.attr2.etc'
    :return: obj.attr1.attr2.etc
    """
    attrs = path.split(".")

    for attr in attrs:
        if type(obj) == CaseInsensitiveDict:
            obj = obj[attr]
            continue

        obj = getattr(obj, attr)

    return obj


class ThreddsInput(BaseInput):
    """
    Process each dataset underneath a TDS catalog.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.uri = kwargs["uri"]
        self.object_attr = kwargs["object_path_attr"]

        self.thredds_kwargs = kwargs.get("catalog_kwargs", {})

    def open_catalog(self):
        """
        Open the Thredds catalog.

        :return: TDSCatalog
        """
        logger.info("Opening catalog")
        catalog = TDSCatalog(self.uri, **self.thredds_kwargs)

        return catalog

    def process_ds(self, ds, generator: BaseGenerator):
        """
        Process a single dataset.

        :param ds: siphon.catalog.TDSCatalog.datasets
        :param generator: BaseGenerator
        """
        filepath = get_sub_attr(ds, self.object_attr)

        if self.should_process(filepath):
            generator.process(filepath)
            logger.debug(f"Input processing: {filepath}")
        else:
            logger.debug(f"Input skipping: {filepath}")

    def run(self, generator: BaseGenerator, kwargs):
        """
        Plugin's entrypoint.

        :param generator: BaseGenerator
        """
        total_files = 0
        start = datetime.now()

        catalog = self.open_catalog()

        for _, ds in walk_tds(catalog, depth=None):
            self.process_ds(ds, generator)
            total_files += 1

        end = datetime.now()
        print(f"Processed {total_files} files from {self.uri} in {end - start}")
