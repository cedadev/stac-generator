# encoding: utf-8
"""
Base Extractor
--------------

This module provides the base class for all derived extractors.

"""
__author__ = "Richard Smith"
__date__ = "08 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import re
from abc import ABC, abstractmethod
from typing import List

from asset_scanner.types.source_media import StorageType

from .handler_picker import HandlerPicker
from .item_describer import ItemDescription, ItemDescriptions
from .processor import BaseProcessor
from .utils import dot2dict, load_plugins


class BaseExtractor(ABC):
    """
    Base class to define an interface for other extractor classes

    Attributes:

        PROCESSOR_ENTRY_POINT:
            Defines the entry point to look for in the setup.py for the
            downstream package. This is used by the ``asset_scanner`` command
            to load the extractor if the extractor is not specifically defined
            in the the configuration file.
    """

    PROCESSOR_ENTRY_POINT = None

    def __init__(self, conf: dict):
        self.conf = conf
        self.processors = self.load_processors()
        self.output_plugins = self.load_output_plugins()
        self.item_descriptions = (
            ItemDescriptions(conf["item_descriptions"]["root_directory"])
            if "item_descriptions" in conf
            else None
        )

        self.facet_processors = self.load_processors(
            entrypoint="asset_scanner.facet_extractors"
        )
        self.pre_processors = self.load_processors(
            entrypoint="asset_scanner.pre_processors"
        )
        self.post_processors = self.load_processors(
            entrypoint="asset_scanner.post_processors"
        )

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

    def _get_processor(
        self, name: str, group: str = "processors", **kwargs
    ) -> BaseProcessor:
        """

        :param name: Name of the requested processor
        :return: processor object
        """

        return getattr(self, group).get_processor(name, **kwargs)

    def _load_extra_processors(self, processor: dict, key: str) -> List[BaseProcessor]:
        """
        Load the post processors for the given processor

        :param processor: Configuration for the processor including any post processor
        :param key: The name of the key which holds the list of extra processors

        :return: List of loaded processors.
        """

        loaded_pprocessors = []

        for pprocessor in processor.get(key, []):
            pp_name = pprocessor["name"]
            pp_kwargs = pprocessor.get("inputs", {})

            loaded = self._get_processor(pp_name, key, **pp_kwargs)

            if loaded:
                loaded_pprocessors.append(loaded)

        return loaded_pprocessors

    def _load_facet_processor(self, processor: dict) -> BaseProcessor:
        processor_name = processor["name"]
        processor_inputs = processor.get("inputs", {})
        output_key = processor.get("output_key")

        return self._get_processor(
            processor_name,
            "facet_processors",
            output_key=output_key,
            **processor_inputs
        )

    def _run_facet_processor(
        self, processor: dict, filepath: str, source_media: StorageType
    ) -> dict:
        """Run the specified processor."""

        # Load the processors
        p = self._load_facet_processor(processor)
        pre_processors = self._load_extra_processors(processor, "pre_processors")
        post_processors = self._load_extra_processors(processor, "post_processors")

        # Retrieve the metadata
        metadata = p.run(
            filepath,
            source_media=source_media,
            post_processors=post_processors,
            pre_processors=pre_processors,
        )

        output_key = getattr(p, "output_key", None)

        if output_key and metadata:
            metadata = dot2dict(output_key, metadata)

        return metadata

    def get_categories(
        self, filepath: str, source_media: StorageType, description: ItemDescription
    ) -> List:
        """
        Get asset category labels

        :param filepath: Asset path
        :param source_media: Source media class
        :param description: ItemDescription for asset
        :return:

        """
        categories = set()

        for conf in description.categories:
            label = self._get_category(filepath, **conf.dict())
            if label:
                categories.add(label)

        return list(categories) or ["data"]

    def load_processors(self, entrypoint: str = None) -> HandlerPicker:
        return HandlerPicker(entrypoint or self.PROCESSOR_ENTRY_POINT)

    def load_output_plugins(self) -> List:
        return load_plugins(self.conf, "asset_scanner.output_plugins", "outputs")

    @abstractmethod
    def process_file(
        self, filepath: str, source_media: StorageType = StorageType.POSIX, **kwargs
    ) -> None:
        pass

    def output(
        self,
        filepath: str,
        source_media: StorageType,
        data: dict,
        namespace: str = None,
    ) -> None:
        for backend in self.output_plugins:
            if not backend.namespace or backend.namespace == namespace:
                backend.export(data)
