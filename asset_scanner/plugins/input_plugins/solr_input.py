"""
Solr Input
----------

Uses a Solr index node for a source for file
objects.

**Plugin name:** ``solr_input``

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
            - name: solr_input
              index_node: url.index-node.ac.uk
              search_params:
                q: "facet: value"
"""

import logging
from typing import TYPE_CHECKING
import requests
import logging
from asset_scanner.types.source_media import StorageType
from asset_scanner.core.extractor import BaseExtractor
from .base import BaseInputPlugin
from string import Template

LOGGER = logging.getLogger(__name__)


class SolrInputPlugin(BaseInputPlugin):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.index_node = kwargs.get('index_node')
        self.core = kwargs.get('core', 'files')
        self.url = f"http://{self.index_node}/solr/{self.core}/select"

        search_params = kwargs.get('search_params', {})
        self.params = {
            'indent': search_params.get('indent', 'on'),
            'q': search_params.get('q', '*:*'),
            'wt': search_params.get('wt', 'json'),
            'rows': search_params.get('rows', 10000),
            'sort': search_params.get('sort', 'id asc'),
            'cursorMark': '*'
        }

    def iter_docs(self):
        n = 0
        while True:
            resp = requests.get(self.url, self.params).json()
            docs = resp['response']['docs']

            yield from docs
            n += len(docs)
            LOGGER.error(f"{n}/{resp['response']['numFound']}\n")
            if not docs:
                LOGGER.error("No docs found")
                break
            LOGGER.info(f"Next cursormark at position {n}")
            self.params['cursorMark'] = resp['nextCursorMark']

    def run(self, extractor: BaseExtractor):
        for doc in self.iter_docs():
            filepath: str = doc.get('id')

            LOGGER.info(f"Input processing: {filepath}")

            # transform file id to a filepath
            filepath = filepath.replace('.', '/', (filepath.split('|')[0].count('.')-1))
            extractor.process_file(filepath=filepath, source_media=StorageType.ESGF_SOLR)