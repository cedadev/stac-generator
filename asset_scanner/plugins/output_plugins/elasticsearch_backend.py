# encoding: utf-8
"""
Elasticsearch
-------------

An output backend which outputs the content generated to elasticsearch
using the Elasticsearch API

**Plugin name:** ``elasticsearch``

.. list-table::
    :header-rows: 1

    * - Option
      - Value Type
      - Description
    * - ``connection_kwargs``
      - ``dict``
      - ``REQUIRED`` Connection kwargs passed to the `elasticsearch client  <https://elasticsearch-py.readthedocs.io/en/latest/api.html#elasticsearch>`_
    * - ``index.name``
      - ``str``
      - ``REQUIRED`` The index to output the content.
    * - ``index.mapping``
      - ``str``
      - Path to a yaml file which defines the mapping for the index
    * - ``namespace``
      - ``str``
      - Can be used by downstream processors to separate outputs to different indices or clusters

Example Configuration:
    .. code-block:: yaml

        outputs:
            - name: elasticsearch
              connection_kwargs:
                hosts: ['host1','host2']
              index:
                name: 'assets-2021-06-02'
              namespace: assets
"""
__author__ = 'Richard Smith'
__date__ = '01 Jun 2021'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from .base import OutputBackend
from elasticsearch import Elasticsearch
from asset_scanner.core.utils import load_yaml, Coordinates

from typing import Dict


class ElasticsearchOutputBackend(OutputBackend):
    """
    Connects to an elasticsearch instance and exports the
    documents to elasticsearch.

    """

    CLEAN_METHODS = [
            '_format_bbox',
            '_format_temporal_extent'
        ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        index_conf = kwargs['index']

        self.es = Elasticsearch(**kwargs['connection_kwargs'])
        self.index_name = index_conf['name']
        self.pipeline_conf = kwargs.get('pipeline', None)

        # Create the index, if it doesn't already exist
        if index_conf.get('mapping'):
            if not self.es.indices.exists(self.index_name):
                mapping = load_yaml(index_conf.get('mapping'))
                self.es.indices.create(self.index_name, body=mapping)

    @staticmethod
    def _format_bbox(data: Dict) -> Dict:
        """
        Convert WGS84 coordinates into GeoJSON and
        format for Elasticsearch. Replaces the bbox key.

        :param data: Input data dictionary
        """
        body = data['body']

        if body.get('bbox'):
            bbox = body.pop('bbox')

            body['spatial'] = {
                    "bbox": {
                        "type": "envelope",
                        "coordinates": Coordinates.from_wgs84(
                            bbox).to_geojson()
                    }
                }

        return data

    @staticmethod
    def _format_temporal_extent(data: Dict) -> Dict:
        """
        Convert `extent object<https://github.com/radiantearth/stac-spec/blob/master/collection-spec/collection-spec.md#extent-object>_` for Elasticsearch.

        :param data: Input data dictionary
        """
        body = data['body']

        if body.get('extent', {}).get('temporal'):
            temporal_extent = body['extent'].pop('temporal')

            if temporal_extent[0][0]:
                body['extent']['temporal'] = {'gte': temporal_extent[0][0]}
            if temporal_extent[0][1]:
                temporal = body['extent'].get('temporal',{})
                temporal['lte'] = temporal_extent[0][1]
                body['extent']['temporal'] = temporal

        return data

    def clean(self, data: Dict) -> Dict:
        """
        Condition the input dictionary for elasticsearch
        :param data: Input dictionary
        :returns: Dictionary produced as a result of the clean methods
        """

        for method in self.CLEAN_METHODS:
            m = getattr(self, method)
            data = m(data)

        return data

    def export(self, data, **kwargs):

        data = self.clean(data)

        index_kwargs = {
            'index': self.index_name,
            'id': data['id'],
            'body': {
                'doc': data['body'],
                'doc_as_upsert': True
            }
        }

        self.es.update(**index_kwargs)
