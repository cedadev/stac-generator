# encoding: utf-8

__author__ = "David Huard"
__date__ = "June 2022"
__copyright__ = "Copyright 2022 Ouranos"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "huard.david@ouranos.ca"


import importlib

# Python imports
import logging

import pydantic

from stac_generator.core.processor import BaseExtractionMethod

LOGGER = logging.getLogger(__name__)


class ControlledVocabularyExtract(BaseExtractionMethod):
    """

    .. list-table::

        * - Processor Name
          - ``controlled_vocabulary``

    Description:
        Compare properties to a controlled vocabulary defined by a pydantic.BaseModel.

    Configuration Options:
        - ``model``: pydantic.BaseModel subclass to be imported at run-time, e.g. `package.module.class_name`.
        - ``strict``: If True, raise ValidationError, otherwise simply log ValidationError messages.

    Example Configuration:

    .. code-block:: yaml

            - name: controlled_vocabulary
              inputs:
                model: my_cv.collections.CMIP5
                strict: False
    """

    def run(self, body: dict, **kwargs) -> dict:

        # Import data model
        scopes = self.model.split(".")
        module = ".".join(scopes[:-1])

        module = importlib.import_module(module)
        klass = getattr(module, scopes[-1])

        # Get metadata attributes
        properties = body

        # Instantiate data model
        try:
            cv = klass(**properties)
            body = cv.dict()

        except pydantic.ValidationError as exc:
            LOGGER.warning(exc)

            if self.strict:
                raise exc

        return body
