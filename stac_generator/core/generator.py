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

from stac_generator.types.generators import ExtractionType

from .collection_describer import CollectionDescription, CollectionDescriptions
from .handler_picker import HandlerPicker
from .processor import BaseProcessor
from .utils import dict_merge, load_plugins


class BaseGenerator(ABC):
    """
    Base class to define an interface for other generator classes

    Attributes:

        EXTRACTION_TYPE:
            Defines the stac level the extraction is occuring at.

        DEFAULT_ID_EXTRACTION_METHODS:
            Defines the default id extraction methods for each stac level
            which is used if a method is not specified in the description.

    """

    EXTRACTION_TYPE = None

    DEFAULT_ID_EXTRACTION_METHODS = {
        "asset_id": {"method": "hash", "inputs": {"terms": ["uri"]}},
        "item_id": {"method": "hash", "inputs": {"terms": []}},
        "collection_id": {"method": "default", "inputs": {"name": "undefined"}},
    }

    def __init__(self, conf: dict):
        self.conf = conf
        self.output_plugins = self.load_output_plugins()
        self.collection_descriptions = (
            CollectionDescriptions(conf["collection_descriptions"]["root_directory"])
            if "collection_descriptions" in conf
            else None
        )

        self.extraction_methods = self.load_processors(
            entrypoint="stac_generator.extraction_methods"
        )
        self.pre_processors = self.load_processors(
            entrypoint="stac_generator.pre_processors"
        )
        self.post_processors = self.load_processors(
            entrypoint="stac_generator.post_processors"
        )
        self.post_extraction_methods = self.load_processors(
            entrypoint="stac_generator.post_extraction_methods"
        )
        self.id_extraction_methods = self.load_processors(
            entrypoint="stac_generator.id_extraction_methods"
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

    def _get_processor(self, name: str, group: str, **kwargs) -> BaseProcessor:
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

        :return: list of loaded processors.
        """

        loaded_pprocessors = []

        for pprocessor in processor.get(key, []):
            loaded = self._load_processor(pprocessor, key)

            if loaded:
                loaded_pprocessors.append(loaded)

        return loaded_pprocessors

    def _load_processor(self, processor: dict, key: str) -> BaseProcessor:
        processor_name = processor["method"]

        processor_inputs = processor.get("inputs", {})

        processor_conf = self.conf.get(key, {}).get(processor_name, {})
        if processor_conf:
            processor_inputs["conf"] = processor_conf

        output_key = processor.get("output_key", None)
        if not output_key:
            output_key = processor_conf.get("output_key", None)

        if not output_key:
            output_key = self.conf.get("output_key", None)

        processor_inputs["output_key"] = output_key

        return self._get_processor(processor_name, key, **processor_inputs)

    def _run_extraction_method(self, extraction_method: dict, uri: str) -> dict:
        """Run the specified extraction method."""

        # Load the processors
        processor = self._load_processor(extraction_method, "extraction_methods")
        pre_processors = self._load_extra_processors(
            extraction_method, "pre_processors"
        )
        post_processors = self._load_extra_processors(
            extraction_method, "post_processors"
        )

        # Retrieve the metadata
        metadata = processor.run(
            uri,
            pre_processors=pre_processors,
            post_processors=post_processors,
        )

        return metadata

    def _run_post_extraction_method(
        self, post_extraction_method: dict, body: dict
    ) -> dict:
        """Run the specified post extraction method."""

        # Load the processors
        processor = self._load_processor(
            post_extraction_method, "post_extraction_methods"
        )
        pre_processors = self._load_extra_processors(
            post_extraction_method, "pre_processors"
        )
        post_processors = self._load_extra_processors(
            post_extraction_method, "post_processors"
        )

        # Retrieve the data
        post_body = processor.run(
            body,
            post_processors=post_processors,
            pre_processors=pre_processors,
        )

        return post_body

    def _run_id_extraction_method(self, id_extraction_method: dict, body: dict) -> dict:
        """Run the specified id extraction method."""

        # Load the processors
        processor = self._load_processor(id_extraction_method, "id_extraction_methods")

        # Retrieve the data
        id = processor.run(
            body,
            post_processors=[],
            pre_processors=[],
        )

        return id

    def run_extraction_methods(
        self, uri: str, description: CollectionDescription, **kwargs: dict
    ) -> dict:
        """
        Extract facets from the listed extraction methods

        :param uri: uri for object
        :param description: CollectionDescription

        :return: result from the processing
        """
        # Execute facet extraction functions
        generator_description = getattr(description, self.EXTRACTION_TYPE.value)

        if generator_description:
            body = {}

            for extraction_method in generator_description.extraction_methods:

                metadata = self._run_extraction_method(extraction_method, uri)

                # Merge the extracted metadata with the metadata already retrieved
                if metadata:
                    body = dict_merge(body, metadata)

        # Process multi-values

        # Apply mappings

        # Apply overrides

        # Convert to URIs

        # Process URIs to human terms

        return body

    def run_post_extraction_methods(
        self, body: dict, description: CollectionDescription, **kwargs: dict
    ) -> dict:
        """
        Extract the raw facets from the listed extraction methods

        :param body: Dict of current extracted data
        :param description: CollectionDescription
        :return: result from the processing
        """

        # Execute facet extraction functions
        generator_description = getattr(description, self.EXTRACTION_TYPE.value)

        if generator_description:

            for post_extraction_method in generator_description.post_extraction_methods:

                body = self._run_post_extraction_method(post_extraction_method, body)

            return body

    def run_id_extraction_methods(
        self, body: dict, description: CollectionDescription, **kwargs: dict
    ) -> dict:
        """
        Extract the raw facets from the listed extraction methods

        :param body: Dict of current extracted data
        :param description: CollectionDescription
        :return: dictionary containing ids
        """

        ids = {}
        collection_description = description.collection

        if collection_description.id:
            collection_id_description = collection_description.id

        else:
            collection_id_description = self.DEFAULT_ID_EXTRACTION_METHODS[
                "collection_id"
            ]

        ids["collection_id"] = self._run_id_extraction_method(
            collection_id_description, body
        )

        if self.EXTRACTION_TYPE in [ExtractionType.ASSET, ExtractionType.ITEM]:
            item_description = description.item

            if item_description.id:
                item_id_description = item_description.id

            else:
                item_id_description = self.DEFAULT_ID_EXTRACTION_METHODS["item_id"]

            # Add collection_id to item_id terms
            if (
                "method" in item_id_description
                and item_id_description["method"] == "hash"
            ):
                item_id_description["inputs"]["terms"].append("collection_id")
                body["properties"]["collection_id"] = ids["collection_id"]

            ids["item_id"] = self._run_id_extraction_method(item_id_description, body)

        if self.EXTRACTION_TYPE in [ExtractionType.ASSET]:
            asset_description = description.asset

            if asset_description.id:
                asset_id_description = asset_description.id

            else:
                asset_id_description = self.DEFAULT_ID_EXTRACTION_METHODS["asset_id"]

            ids["asset_id"] = self._run_id_extraction_method(asset_id_description, body)

        return ids

    def load_processors(self, entrypoint: str) -> HandlerPicker:
        return HandlerPicker(entrypoint)

    def load_output_plugins(self) -> list:
        return load_plugins(self.conf, "stac_generator.output_plugins", "outputs")

    @abstractmethod
    def process(self, **kwargs) -> None:
        pass

    def output(self, data: dict, **kwargs) -> None:
        for backend in self.output_plugins:
            backend.export(data, **kwargs)
