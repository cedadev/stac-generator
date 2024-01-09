# encoding: utf-8
__author__ = "Richard Smith"
__date__ = "11 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import logging

from jinja2 import Environment, FileSystemLoader

from stac_generator.core.baker import Recipe

# Package imports
from stac_generator.core.mapping import BaseMapping

LOGGER = logging.getLogger(__name__)


class Jinja2Mapping(BaseMapping):
    """

    Mapping Name: ``jinja2_mapping``

    Description:
        Takes body, and recipe and returns object in CEDA mapping.

    Example Configuration:

        .. code-block:: yaml

            - method: jinja2_mapping

    """

    def run(
        self,
        body: dict,
        recipe: Recipe,
        **kwargs,
    ) -> dict:
        environment = Environment(loader=FileSystemLoader(self.template_directory))
        template = environment.get_template(self.template)

        return template.render(**body)
