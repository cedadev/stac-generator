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

from abc import ABC, abstractmethod
from collections import defaultdict

from stac_generator.core.bulk_output import BaseBulkOutput
from stac_generator.types.generators import GeneratorType

from .baker import ExtractionMethodConf, Recipe, Recipes
from .extraction_method import BaseExtractionMethod
from .handler_picker import HandlerPicker
from .utils import load_plugins


class BaseGenerator(ABC):
    """
    Base class to define an interface for other generator classes

    Attributes:

        TYPE:
            Defines the stac levels the extraction is occuring at.

    """

    TYPE = GeneratorType.NONE

    def __init__(self, conf: dict):
        recipes_root = conf.get("recipes_root", "recipes")

        self.recipes = Recipes(recipes_root)

        self.default_id_methods = conf.pop("default_id_methods", {})

        self.outputs = load_plugins(conf.pop("outputs", []), "stac_generator.outputs")

        self.conf = conf

        self.extraction_methods = self.load_extraction_methods()

    def load_extraction_methods(self) -> HandlerPicker:
        """
        Load extraction methods from entrypoint.

        :return: HandlerPicker for extraction methods
        """
        return HandlerPicker("stac_generator.extraction_methods")

    def _load_extraction_method(
        self, extraction_method_conf: dict, **kwargs
    ) -> BaseExtractionMethod:
        """
        Load the given extraction method

        :param extraction_method_conf: Configuration for the extraction method

        :return: extraction method
        """

        extraction_method_name = extraction_method_conf.method

        generator_conf = self.conf.get("extraction_methods", {})

        default_conf = generator_conf.get(extraction_method_name, {})

        inputs = extraction_method_conf.inputs

        inputs["default_conf"] = kwargs | default_conf

        if "extraction_methods" in inputs:
            extraction_methods = []

            for extraction_method in inputs.get("extraction_methods", []):
                if isinstance(extraction_method, dict):
                    extraction_methods.append(self._load_extraction_method(ExtractionMethodConf(**extraction_method), **kwargs))

                else:
                    extraction_methods.append(extraction_method)

            inputs["extraction_methods"] = extraction_methods

        return self.extraction_methods.get(extraction_method_name, **inputs)

    def _run_extraction_method(
        self, body: dict, extraction_method_conf: dict, **kwargs
    ) -> dict:
        """Run the specified extraction method."""

        extraction_method = self._load_extraction_method(
            extraction_method_conf, **kwargs
        )

        return extraction_method.run(body)

    def run_extraction_methods(
        self, body: dict, extraction_methods: list, **kwargs: dict
    ) -> dict:
        """
        Extract facets from the listed extraction methods

        :param body: current extracted meta data
        :param recipe: Recipe

        :return: result from the processing
        """

        for extraction_method in extraction_methods:
            body = self._run_extraction_method(body, extraction_method, **kwargs)

        return body

    def run_member_of_methods(
        self, body: dict, member_of: list, **kwargs: dict
    ) -> dict:
        """
        Extract the raw facets from the listed extraction methods

        :param body: Dict of current extracted data
        :param recipe: Recipe
        :return: updated body
        """

        update = defaultdict(list)

        update["member_of_recipes"] = {}

        for link in member_of:
            body = self.run_extraction_methods(body, link.id, **kwargs)

            link_id = body.pop(f"{link.type}_id")

            update[f"{link.type}_id"].append(link_id)

            update["member_of_recipes"][link_id] = link.key

        body.update(update)

        return body

    def output(self, body: dict, recipe: Recipe, **kwargs) -> None:
        """
        Run all configured outputs export methods.

        :param data: data to be output
        """
        for output in self.outputs:
            output.run(body, recipe, **kwargs)

    def finished(self) -> None:
        """
        Run clear cache of remaining data for bulk outputs.
        """
        for output in self.outputs:
            if isinstance(output, BaseBulkOutput):
                output.clear_cache()

    @abstractmethod
    def _process(self, body: dict, **kwargs) -> None:
        """
        Run generator.

        :param body: body for object
        """

    def process(self, uri: str, **kwargs) -> None:
        """
        Run generator.

        :param uri: uri for object
        """
        kwargs["TYPE"] = self.TYPE

        body = {"uri": uri}

        self._process(body, **kwargs)
