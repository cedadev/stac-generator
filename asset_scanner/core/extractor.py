# encoding: utf-8
"""
Base Extractor
--------------

This module provides the base class for all derived extractors.

"""
__author__ = 'Richard Smith'
__date__ = '08 Jun 2021'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from abc import ABC, abstractmethod
from .utils import load_plugins
from .handler_picker import HandlerPicker
from .item_describer import ItemDescriptions, ItemDescription
from asset_scanner.types.source_media import StorageType
import re

from typing import List


class BaseExtractor(ABC):
    """
    Base class to define an interface for other extractor classes

    Attributes:

        PROCESSOR_ENTRY_POINT:
            Defines the entry point to look for in the setup.py for the downstream
            package. This is used by the ``asset_scanner`` command to load the extractor
            if the extractor is not specifically defined in the the configuration file.
    """
    PROCESSOR_ENTRY_POINT = None

    def __init__(self, conf: dict):
        self.conf = conf
        self.processors = self.load_processors()
        self.output_plugins = self.load_output_plugins()
        self.item_descriptions = ItemDescriptions(conf['item_descriptions']['root_directory']) if 'item_descriptions' in conf else None

        self.load_processors()

    @staticmethod
    def _get_path(filepath, **kwargs) -> str:
        """
        Check to see if there is a `ParseResult <https://docs.python.org/3/library/urllib.parse.html?highlight=parseresult#urllib.parse.ParseResult>_
        object. If there is and it contains a network location, return just the path
        e.g.
        - https://data.ceda.ac.uk/badc/ukmo -> /badc/ukmo
        - http://cmip6-zarr-o.s3.jc.rl.ac.uk/CMIP6.CFMIP.IPSL.IPSL-CM6A-LR/amip-p4K.r1i1p1f1.Amon.evspsbl.gr.v20180906.zarr -> CMIP6.CFMIP.IPSL.IPSL-CM6A-LR/amip-p4K.r1i1p1f1.Amon.evspsbl.gr.v20180906.zarr

        :param filepath:
        :param kwargs:
        :return:
        """
        parse_result = kwargs.get('uri_parse')
        if not parse_result:
            return filepath

        if not parse_result.netloc:
            return filepath

        return parse_result.path

    @staticmethod
    def _get_category(string, label, regex):
        """

        :param string:
        :param label:
        :param regex:
        :return:

        """

        m = re.search(regex, string)

        if not m:
            label = None

        return label

    def get_categories(self, filepath: str, source_media: StorageType, description: ItemDescription) -> List:
        """
        Get asset category labels

        :param filepath: Asset path
        :param source_media: Source media class
        :param description: ItemDescription for asset
        :return:

        """
        categories = set()

        for conf in description.categories:
            label = self._get_category(filepath, **conf)
            if label:
                categories.add(label)

        return list(categories) or ['data']

    def load_processors(self, entrypoint: str = None) -> HandlerPicker:
        return HandlerPicker(entrypoint or self.PROCESSOR_ENTRY_POINT)

    def load_output_plugins(self) -> List:
        return load_plugins(self.conf, 'asset_scanner.output_plugins', 'outputs')

    @abstractmethod
    def process_file(self, filepath: str, source_media: StorageType = StorageType.POSIX, **kwargs) -> None:
        pass

    def output(self, filepath: str, source_media: StorageType, data: dict, namespace: str = None) -> None:
        for backend in self.output_plugins:
            if not backend.namespace or backend.namespace == namespace:
                backend.export(data)
