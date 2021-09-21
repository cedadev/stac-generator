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
from .item_describer import ItemDescriptions

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
        self.item_descriptions = ItemDescriptions(conf['item_descriptions']['root_directory'])

        self.load_processors()

    def load_processors(self, entrypoint: str = None) -> HandlerPicker:
        return HandlerPicker(entrypoint or self.PROCESSOR_ENTRY_POINT)

    def load_output_plugins(self) -> List:
        return load_plugins(self.conf, 'asset_scanner.output_plugins', 'outputs')

    @abstractmethod
    def process_file(self, filepath: str, source_media: str = 'POSIX', **kwargs) -> None:
        pass

    def output(self, filepath: str, source_media: str, data: dict, namespace: str = None) -> None:
        for backend in self.output_plugins:
            if not backend.namespace or backend.namespace == namespace:
                backend.export(data)
