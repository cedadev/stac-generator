# encoding: utf-8

__author__ = "David Huard"
__date__ = "June 2022"
__copyright__ = "Copyright 2022 Ouranos"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "huard.david@ouranos.ca"


# Python imports
import logging

import pydantic

from stac_generator.core.decorators import accepts_postprocessors
from stac_generator.core.processor import BasePostExtractionMethod

LOGGER = logging.getLogger(__name__)


class ControlledVocabularyPostExtract(BasePostExtractionMethod):
    """

    .. list-table::

        * - Processor Name
          - ``controlled_vocabulary``
        * - Accepts Pre-processors
          -
        * - Accepts Post-processors
          - .. fa:: check

    Description:
        Compare properties to a controlled vocabulary defined by a pydantic.BaseModel.

    Configuration Options:
        - ``model``: pydantic.BaseModel subclass to be imported at run-time, e.g. `package.module.class_name`.
        - ``strict``: If True, raise ValidationError, otherwise simply log ValidationError messages.

    Example Configuration:

    .. code-block:: yaml

        post_processors:
            - name: controlled_vocabulary
              inputs:
                model: my_cv.collections.CMIP5
                strict: False
    """

    @accepts_postprocessors
    def run(
        self,
        data: dict,
        source_media: str = "POSIX",
        **kwargs,
    ) -> dict:
        import importlib

        # Import data model
        scopes = self.model.split(".")
        module = ".".join(scopes[:-1])

        module = importlib.import_module(module)
        klass = getattr(module, scopes[-1])

        # Get metadata attributes
        properties = data["body"]["properties"]

        # Instantiate data model
        try:
            cv = klass(**properties)
            data["body"]["properties"] = cv.dict()

        except pydantic.ValidationError as exc:
            LOGGER.warning(exc)

            if self.strict:
                raise exc

        return data
