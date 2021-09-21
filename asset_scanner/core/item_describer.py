# encoding: utf-8
"""
Item Description
================
"""
__author__ = 'Richard Smith'
__date__ = '27 May 2021'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

# Package imports
from asset_scanner.core.utils import dict_merge, load_description_files

# 3rd Party Imports
from directory_tree import DatasetNode

# Python imports
import yaml
from functools import lru_cache
import logging

# Typing imports
from typing import List, Optional


LOGGER = logging.getLogger(__name__)


class ItemDescription:
    """
    Container to provide convenient access points into parts of
    the item description.
    """
    def __init__(self, description):
        self._description = description

    def __repr__(self):
        return yaml.dump(self._description)

    @property
    def defaults(self) -> dict:
        """Returns defaults"""
        return self._description.get('defaults', {})

    @property
    def overrides(self) -> Optional[dict]:
        """Returns overrides"""
        return self._description.get('overrides')

    @property
    def mappings(self) -> Optional[dict]:
        """Returns mappings"""
        return self._description.get('mappings')

    @property
    def allowed_facets(self) -> List:
        """Returns allowed facets"""
        return self.facet_extract_conf.get('allowed_facets', [])

    @property
    def extraction_methods(self) -> List[dict]:
        """Returns extraction methods"""
        return self.facet_extract_conf.get('extraction_methods', [])

    @property
    def aggregation_facets(self) -> List:
        """Returns aggregation facets
        """
        return self.facet_extract_conf.get('aggregation_facets', [])

    @property
    def facet_extract_conf(self) -> dict:
        """Returns facets key"""
        return self._description.get('facets', {})

    @property
    def categories(self):
        """Returns categories"""
        return self._description.get('categories', [])

    @property
    def collection(self):
        """Returns collection"""
        return self._description.get('collection', {})


class ItemDescriptions:
    """
    Holds references to all the description files and handles loading, merging
    and returning an :py:obj:`ItemDescription`
    """

    def __init__(self, root_path: str):
        """

        :param root_path: Path to the root of the yaml store
        """

        self.tree = DatasetNode()

        self._build_tree(root_path)

    def _build_tree(self, root_path: str) -> None:
        """
        Loads the yaml files from the root path and builds the dataset tree
        with references to the yaml files.

        :param root_path: Path at the top of the yaml file tree
        """

        files = load_description_files(root_path)

        if not files:
            LOGGER.error("No description files found. Check the path in your configuration. Exiting...")
            exit()

        for file in files:
            with open(file) as reader:
                data = yaml.safe_load(reader)

                for dataset in data.get('datasets', []):
                    # Strip trailing slash. Needed to make sure tree search works
                    dataset = dataset.rstrip('/')

                    self.tree.add_child(dataset, description_file=file.as_posix())

    def get_description(self, filepath: str) -> ItemDescription:
        """
        Get the merged description for the given file path.
        This gets all the description files along the path
        and merges them from top down so that more generic
        descriptions are overridden.
        e.g.

        files describing ``/badc`` will be overridden by files
        which describe ``/badc/faam/data``

        Dict values are overridden by more specific files and
        arrays are appended to, with duplicates ignored.

        :param filepath: Path for which to retrieve the description
        """
        nodes = self.tree.search_all(filepath)
        description_files = [node.description_file for node in nodes]

        config_description = self.load_config(*description_files)

        return ItemDescription(config_description)

    @lru_cache(100)
    def load_config(self, *args: str) -> dict:
        """

        :param args: each arg is a filepath to a description file
        :return: Dictionary containing the merged properties of all the matching nodes
        """
        base_dict = {}
        for file in args:
            with open(file) as reader:
                base_dict = dict_merge(base_dict, yaml.safe_load(reader))

        return base_dict


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('root')
    args = parser.parse_args()

    descriptions = ItemDescriptions(args.root)

    description = descriptions.get_description('/badc/faam/data/2005/b069-jan-05/core_processed/core_faam_20050105_r0_b069.nc')

    print(description)
