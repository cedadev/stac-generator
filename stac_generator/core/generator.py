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

import logging
from collections import defaultdict

from extraction_methods.core.extraction_method import ExtractionMethod

from stac_generator.core.bulk_output import BulkOutput

from .baker import ExtractionMethodConf, Recipe, Recipes
from .handler_picker import HandlerPicker
from .utils import load_plugins

LOGGER = logging.getLogger(__name__)


class Generator:
    """
    Generator class
    """

    def __init__(self, conf: dict):
        recipes_root = conf.get("recipes_root", "recipes")

        self.recipes = Recipes(recipes_root)

        self.inputs = load_plugins(conf.pop("inputs", []), "stac_generator.inputs")

        self.outputs = load_plugins(conf.pop("outputs", []), "stac_generator.outputs")

        self.conf = conf

        self.extraction_methods = self.load_extraction_methods()

    def load_extraction_methods(self) -> HandlerPicker:
        """
        Load extraction methods from entrypoint.

        :return: HandlerPicker for extraction methods
        """
        return HandlerPicker("extraction_methods")

    def _load_extraction_method(self, extraction_method_conf: dict, **kwargs) -> ExtractionMethod:
        """
        Load the given extraction method

        :param extraction_method_conf: Configuration for the extraction method
        :param kwargs:

        :return: extraction method
        """

        # Overide less specific inputs
        inputs = (
            self.conf.get("extraction_methods", {}).get(extraction_method_conf.method, {})
            | extraction_method_conf.inputs
            | kwargs
        )

        # Collect "sub" extraction methods
        if "extraction_methods" in inputs:
            extraction_methods = []

            for extraction_method in inputs.get("extraction_methods", []):
                if isinstance(extraction_method, dict):
                    extraction_methods.append(
                        self._load_extraction_method(
                            ExtractionMethodConf(**extraction_method), **kwargs
                        )
                    )

                else:
                    extraction_methods.append(extraction_method)

            inputs["extraction_methods"] = extraction_methods

        return self.extraction_methods.get(extraction_method_conf.method, **inputs)

    def _run_extraction_method(self, body: dict, extraction_method_conf: dict, **kwargs) -> dict:
        """
        Run the specified extraction method.

        :param body: The current body of data
        :param extraction_method_conf: Configuration for the extraction method
        :param kwargs:

        :return: body post extraction method
        """

        extraction_method = self._load_extraction_method(extraction_method_conf, **kwargs)

        return extraction_method._run(body)

    def run_extraction_methods(self, body: dict, extraction_methods: list, **kwargs) -> dict:
        """
        Extract facets from the listed extraction methods

        :param body: current extracted meta data
        :param recipe: Recipe
        :param kwargs:

        :return: result from the processing
        """

        for extraction_method in extraction_methods:
            body = self._run_extraction_method(body, extraction_method, **kwargs)

        return body

    def output(self, body: dict, recipe: Recipe, **kwargs) -> None:
        """
        Run all configured outputs export methods.

        :param data: data to be output
        :param kwargs:
        """
        for output in self.outputs:
            output.run(body, recipe, **kwargs)

    def finished(self) -> None:
        """
        Run clear cache of remaining data for bulk outputs.
        """
        for output in self.outputs:
            if isinstance(output, BulkOutput):
                output.clear_cache()

    def process(self, body: dict, **kwargs) -> None:
        """
        process a generator record.

        :param body: body for object
        :param kwargs:
        """
        kwargs["GENERATOR_TYPE"] = self.conf.get("generator")

        recipe = self.recipes.get(body.get("recipe_path", body["uri"]), self.conf.get("generator"))

        LOGGER.debug("Generating %s : %s with recipe %s", self.conf.get("generator"), body["uri"], recipe)

        body = self.run_extraction_methods(body, recipe.extraction_methods, **kwargs)

        self.output(body, recipe, **kwargs)

    def run(self) -> None:
        """
        Run generator.
        """
        for input_plugin in self.inputs:
            for body in input_plugin.run():
                self.process(body)

        self.finished()
