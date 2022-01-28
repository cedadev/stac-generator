# encoding: utf-8
"""
"""
__author__ = 'Richard Smith'
__date__ = '25 Aug 2021'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from asset_scanner.core.processor import BaseAggregationProcessor
from asset_scanner.core.types import SpatialExtent, TemporalExtent
from elasticsearch import Elasticsearch

from typing import Optional, List, Dict


class ElasticsearchAggregator(BaseAggregationProcessor):
    """
    .. list-table::

        * - Processor Name
          - ``elasticsearch_aggregator``
        * - Accepts Pre-processors
          - .. fa:: times
        * - Accepts Post-processors
          - .. fa:: times

    Description:
        Using a collection ID. Generate a summary of information to create a collection.

    Configuration Options:
        - ``item_index``: ``REQUIRED`` Name of the index holding the STAC items
        - ``connection_kwargs``: ``REQUIRED`` Connection parameters passed to
        `elasticsearch.Elasticsearch<https://elasticsearch-py.readthedocs.io/en/7.10.0/api.html>`_

    Configuration Example:

        .. code-block:: yaml

                name: elasticsearch_aggregator
                inputs:
                    index: ceda-index
                    connection_kwargs:
                      hosts: ['host1:9200','host2:9200']
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.es = Elasticsearch(**kwargs['connection_kwargs'])
        self.index = kwargs['index']

    def get_page(self, query: Dict, facet: str, result_list: List) -> List:
        """
        Get page of aggregations and parse the results
        :param query: Elasticsearch query to execute
        :param facet: Facet to retrieve values for
        :param result_list: list to extend with any found values
        """

        result = self.es.search(index=self.index, body=query)

        if result['aggregations']:
            buckets = result['aggregations']['facet']['buckets']
            result_list.extend([bucket['key'][facet] for bucket in buckets])

            return result['aggregations']['facet'].get('after_key')

    @staticmethod
    def base_query(file_id: str) -> Dict:
        """
        Base query to filter the results to a single collection

        :param file_id: Collection to restrict results to
        """
        return {
            "query": {
                "term": {
                    "file_id.keyword": {
                        "value": file_id
                    }
                }
            },
            "size": 0
        }

    @staticmethod
    def time_range_query() -> Dict:
        """
        Query to extract the time range from items
        """
        return {
            "start_datetime": {
                "min": {"field": "properties.start_datetime"}
            },
            "end_datetime": {
                "max": {"field": "properties.end_datetime"}
            },
            "min_datetime": {
                "min": {"field": "properties.datetime"}
            },
            "max_datetime": {
                "max": {"field": "properties.datetime"}
            }
        }

    @staticmethod
    def bbox_query() -> Dict:
        """
        Query to extract the BBOX from items
        """
        return {}

    @staticmethod
    def facet_composite_query(facet: str) -> Dict:
        """
        Generate the composite aggregation for the facet
        :param facet: Facet to aggregate on
        """
        return {
            "facet": {
                "composite": {
                    "sources": [
                        {
                            facet: {
                                "terms": {
                                    "field": f"properties.{facet}.keyword"
                                }
                            }
                        }
                    ],
                    "size": 100
                }
            }
        }

    def get_facet_values(self, facet: str, file_id: str) -> List:
        """
        Query elasticsearch and scroll the aggregation response
        to get all the values for the given facet within the given
        collection.

        :param facet: Facet to check
        :param file_id: Collection ID
        :return: List of values for the facet
        """

        query = self.base_query(file_id)
        query['aggs'] = self.facet_composite_query(facet)

        facet_values = []

        after_key = self.get_page(query, facet, facet_values)

        while after_key:
            query['aggs']['facet']['composite']['after'] = after_key
            after_key = self.get_page(query, facet, facet_values)

        return facet_values

    @staticmethod
    def get_temporal_extent(response) -> Optional[TemporalExtent]:
        """
        Extract the temporal extent from the Elasticsearch Response.

        As there are two potential sources of date information, this method
        grabs the start_datetime/end_datetime by preference and defers to the
        datetime parameter if the former is not available.

        :param response: Elasticsearch result
        :return: [[start_date,end_date]]
        """

        aggs = response['aggregations']

        if aggs:

            # Comes from datetime
            max_datetime = aggs['max_datetime'].get('value_as_string')
            min_datetime = aggs['min_datetime'].get('value_as_string')

            # comes from start and end datetime
            end_datetime = aggs['end_datetime'].get('value_as_string')
            start_datetime = aggs['start_datetime'].get('value_as_string')

            # Prefer values from start/end datetime as these are likely to be
            # more specific. Open date ranges are allowed to one of the values
            # is allowed to be null
            if any([start_datetime, end_datetime]):
                return [[start_datetime, end_datetime]]

            # Max and min taken from same value so if one is missing, they both
            # will be. Less specific than start and end time so is a fallback
            if all([min_datetime, max_datetime]):
                return [[min_datetime, max_datetime]]

    @staticmethod
    def get_spatial_extent(response) -> Optional[SpatialExtent]:
        """
        Extract the spatial extent from the Elasticsearch response.

        :param response: Elasticsearch result
        :return: [[minLon, minLat, maxLon, maxLat]]
        """
        ...

    def get_extent(self, file_id: str) -> Dict:
        """
        Get the extent aggregation
        :param file_id: collection ID
        """

        query = self.base_query(file_id)

        # Time range query
        query['aggs'] = self.time_range_query()

        # BBOX query
        query['aggs'].update(self.bbox_query())

        result = self.es.search(index=self.index, body=query)

        extent = {}
        temporal_extent = self.get_temporal_extent(result)
        spatial_extent = self.get_spatial_extent(result)

        if temporal_extent:
            extent['temporal'] = temporal_extent
        if spatial_extent:
            extent['spatial'] = spatial_extent

        return extent

    def run(self, file_id: str, description: 'ItemDescription') -> Dict:
        """
        Run the processor
        :param file_id: Collection ID to aggregate on
        :param description: ItemDescription containing keys to summarise
        """

        metadata = {}

        # Get list of aggregation facets and extra top level facets
        facets = set(description.facets.aggregation_facets + description.facets.search_facets)

        # Poll elasticsearch for value list for each facet
        summaries = {}
        for facet in facets:
            values = self.get_facet_values(facet, file_id)
            if values:
                summaries[facet] = values

        # Get extent aggregation
        extent = self.get_extent(file_id)

        # Package up and return
        if summaries:
            metadata['summaries'] = summaries
        if extent:
            metadata['extent'] = extent

        return metadata
