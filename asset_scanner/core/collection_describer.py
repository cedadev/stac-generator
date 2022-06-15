# encoding: utf-8
"""
Item Description
================
"""
__author__ = "Richard Smith"
__date__ = "27 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import logging

# Python imports
from functools import lru_cache
from pathlib import Path
from typing import Optional

import yaml

# 3rd Party Imports
from directory_tree import DatasetNode
from pydantic import BaseModel

# Package imports
from asset_scanner.core.utils import dict_merge, load_description_files

LOGGER = logging.getLogger(__name__)


class Category(BaseModel):
    """Category label model."""

    label: str
    regex: str


class STACModel(BaseModel):
    """Collections processor description model."""

    id: dict = {}
    extraction_methods: list[dict] = []
    post_extraction_methods: list[dict] = []


class CollectionDescription(BaseModel):
    """Top level container for CollectionDescriptions."""

    paths: list

    asset: Optional[STACModel]
    item: Optional[STACModel]
    collection: Optional[STACModel]

    categories: list[Category] = []

    def __repr__(self):
        return yaml.dump(self.dict())


class CollectionDescriptions:
    """
    Holds references to all the description files and handles loading, merging
    and returning an :py:obj:`ItemDescription`
    """

    def __init__(
        self, root_path: Optional[str] = None, filelist: Optional[list] = None
    ):
        """

        :param root_path: Path to the root of the yaml store
        :param filelist: Can supply a set of yml files to load. If present, root_path is ignored.
        """

        self.tree = DatasetNode()

        self._build_tree(root_path, filelist)

    def _build_tree(self, root_path: str, files: list[Path]) -> None:
        """
        Loads the yaml files from the root path and builds the dataset tree
        with references to the yaml files.

        :param root_path: Path at the top of the yaml file tree
        :param files: list of files to open.
        """

        if not files:
            files = load_description_files(root_path)

        if not files:
            LOGGER.error(
                "No description files found. "
                "Check the path in your configuration. Exiting..."
            )
            exit()

        for file in files:
            with open(file) as reader:
                data = yaml.safe_load(reader)

                for dataset in data.get("paths", []):
                    # Strip trailing slash. Needed to make sure tree search works
                    dataset = dataset.rstrip("/")

                    self.tree.add_child(dataset, description_file=file.as_posix())

    def get_description(self, filepath: str) -> CollectionDescription:
        """
        Get the merged description for the given file path.
        This gets all the description files along the path
        and merges them from top down so that more generic
        descriptions are overridden.
        e.g.

        files describing ``/badc`` will be overridden by files
        which describe ``/badc/faam/data``

        dict values are overridden by more specific files and
        arrays are appended to, with duplicates ignored.

        .. note::
            For remote filepaths (e.g. https://... or gs://) a ``/``
            character will be pre-pended. This is to enable the lookup
            to pass as the root node of the tree is ``/``.

        :param filepath: Path for which to retrieve the description
        """

        if not filepath[0] == "/":
            filepath = f"/{filepath}"

        nodes = self.tree.search_all(filepath)
        description_files = [node.description_file for node in nodes]

        config_description = self.load_config(*description_files)

        return CollectionDescription(**config_description)

    @lru_cache(100)
    def load_config(self, *args: str) -> dict:
        """

        :param args: each arg is a filepath to a description file
        :return: dictionary containing the merged properties of all the matching nodes
        """
        base_dict = {}
        for file in args:
            with open(file) as reader:
                base_dict = dict_merge(base_dict, yaml.safe_load(reader))

        return base_dict


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "root", help="root from which to load all the yaml description files"
    )
    parser.add_argument("path", help="path to retrieve description for")

    args = parser.parse_args()

    descriptions = CollectionDescriptions(args.root)

    description = descriptions.get_description(args.path)

    print(description)
