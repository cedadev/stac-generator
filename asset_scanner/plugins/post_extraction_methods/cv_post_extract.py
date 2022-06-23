# encoding: utf-8

__author__ = "David Huard"
__date__ = "June 2022"
__copyright__ = "Copyright 2018 Ouranos"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "huard.david@ouranos.ca"


# Python imports
import logging

from asset_scanner.core.decorators import accepts_postprocessors, accepts_preprocessors
from asset_scanner.core.processor import BaseProcessor

LOGGER = logging.getLogger(__name__)


class ControlledVocabularyPostExtract(BaseProcessor):
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

    Example Configuration:

    .. code-block:: yaml

        post_processors:
            - name: controlled_vocabulary
              inputs:
                model:
                  my_cv.collections.CMIP5
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
        scopes = self.model.split('.')
        module = '.'.join(scopes[:-1])

        module = importlib.import_module(module)
        klass = getattr(module, scopes[-1])

        # Get metadata attributes
        properties = data["body"]["properties"]

        # Instantiate data model
        cv = klass(**properties)

        # Return validated properties. Could be different from original properties (default values, processing, etc.)
        data["body"]["properties"] = cv.dict()

        return data
