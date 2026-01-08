# encoding: utf-8
__author__ = "Richard Smith"
__date__ = "02 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import logging
import os
from datetime import datetime

from pydantic import BaseModel, Field
from tqdm import tqdm

from stac_generator.core.input import Input

logger = logging.getLogger(__name__)


class FileSystemConf(BaseModel):
    """File system config."""

    path: str = Field(
        description="Root path to begin walk.",
    )
    kwargs: dict = Field(
        default={},
        description="os walk kwargs.",
    )


class FileSystemInput(Input):
    """
    Performs an os.walk to provide a stream of messages for procesing.

    **Plugin name:** ``file_system``

    Example Configuration:
      .. code-block:: yaml

        name: file_system
        conf:
          path: test_directory
    """

    config_class = FileSystemConf

    def run(self):
        total_files = 0
        start = datetime.now()
        for root, _, files in tqdm(os.walk(self.conf.path, **self.conf.kwargs)):
            for file in files:
                filename = os.path.abspath(os.path.join(root, file))
                logger.debug("Input processing: %s", filename)

                yield {"uri": filename}
                total_files += 1

        end = datetime.now()
        print(f"Processed {total_files} files from {self.conf.path} in {end-start}")
