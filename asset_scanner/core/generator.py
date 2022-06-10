# encoding: utf-8
"""
Base Generator
--------------

This module provides the base class for all derived generators.

"""
__author__ = "Richard Smith"
__date__ = "08 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import re
from abc import ABC, abstractmethod
from typing import List
from cachetools import TTLCache

from .handler_picker import HandlerPicker
from .collection_describer import CollectionDescription, CollectionDescriptions
from .processor import BaseProcessor
from .utils import dict_merge, dot2dict, generate_id, load_plugins


class BaseGenerator(ABC):
    """
    Base class to define an interface for other generator classes

    Attributes:

        PROCESSOR_ENTRY_POINT:
            Defines the entry point to look for in the setup.py for the
            downstream package. This is used by the ``asset_scanner`` command
            to load the extractor if the extractor is not specifically defined
            in the the configuration file.
    """

    EXTRACTION_TYPE = None
    
    PROCESSOR_ENTRY_POINT = None
    
    def __init__(self, conf: dict):
        self.conf = conf
        self.processors = self.load_processors()
        self.output_plugins = self.load_output_plugins()
        self.collection_descriptions = (
            CollectionDescriptions(conf["collection_descriptions"]["root_directory"])
            if "collection_descriptions" in conf
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

        self.header_deduplication = conf.get('header_deduplication', False)
        self.item_id_cache = TTLCache(
            maxsize=conf.get('CACHE_MAX_SIZE', 10),
            ttl=conf.get('CACHE_MAX_AGE', 30)
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
    
    def get_collection_id(self, description: CollectionDescription) -> str:
        """Return the collection ID."""
        collection_id = getattr(description.collection, 'id', 'undefined')
        return generate_id(collection_id)

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

    def _load_processor(self, processor: dict) -> BaseProcessor:
        processor_name = processor["name"]
        processor_inputs = processor.get("inputs", {})
        output_key = processor.get("output_key")

        return self._get_processor(
            processor_name,
            "facet_processors",
            output_key=output_key,
            **processor_inputs
        )

    def _run_processor(
        self, processor: dict, uri: str
    ) -> dict:
        """Run the specified processor."""

        # Load the processors
        p = self._load_processor(processor)
        pre_processors = self._load_extra_processors(processor, "pre_processors")
        post_processors = self._load_extra_processors(processor, "post_processors")

        # Retrieve the metadata
        metadata = p.run(
            uri,
            pre_processors=pre_processors,
            post_processors=post_processors,
        )

        output_key = getattr(p, "output_key", None)

        if output_key and metadata:
            metadata = dot2dict(output_key, metadata)

        return metadata
    
    def run_processors(self,
                       uri: str,
                       description: CollectionDescription,
                       **kwargs: dict) -> dict:
        """
        Extract the raw facets from the file based on the listed processors

        :param uri: uri for object
        :param description: CollectionDescription

        :return: result from the processing
        """
        # Execute facet extraction functions
        generator_description = description.get(self.EXTRACTION_TYPE)

        if processors := generator_description.get("extraction_methods"):
            for processor in processors:

                metadata = self._run_processor(processor, uri)

                # Merge the extracted metadata with the metadata already retrieved
                if metadata:
                    tags = dict_merge(tags, metadata)

        # Process multi-values

        # Apply mappings

        # Apply overrides

        # Convert to URIs

        # Process URIs to human terms

        return tags

    def get_categories(
        self, uri: str, description: CollectionDescription
    ) -> List:
        """
        Get category labels

        :param uri: uri for object
        :param description: CollectionDescription
        :return:

        """
        categories = set()

        for conf in description.categories:
            label = self._get_category(uri, **conf.dict())
            if label:
                categories.add(label)

        return list(categories) or ["data"]

    def load_processors(self, entrypoint: str = None) -> HandlerPicker:
        return HandlerPicker(entrypoint or self.PROCESSOR_ENTRY_POINT)

    def load_output_plugins(self) -> List:
        return load_plugins(self.conf, "asset_scanner.output_plugins", "outputs")

    @abstractmethod
    def process(
        self, **kwargs
    ) -> None:
        pass

    def output(
        self,
        data: dict,
        namespace: str = None,
        **kwargs
    ) -> None:
        for backend in self.output_plugins:
            if not backend.namespace or backend.namespace == namespace:
                backend.export(data, **kwargs)
