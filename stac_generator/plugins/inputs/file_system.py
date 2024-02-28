# encoding: utf-8
"""
File System Input
-----------------

Takes a path and will scan the file system, submitting
each file to the asset generator

**Plugin name:** ``file_system``

.. list-table::
    :header-rows: 1

    * - Option
      - Value Type
      - Description
    * - ``path``
      - ``string``
      - ``REQUIRED`` The root path to scan
    * - ``kwargs``
      - ``dict``
      - Optional kwargs to pass to `os.walk <https://docs.python.org/3/library/os.html#os.walk>`_
    * - ``filters``
      - :ref:`Filters <stac_generator/filters:filters>`
      - Optional filters

Example Configuration:
    .. code-block:: yaml

        inputs:
            - method: file_system
              path: test_directory

"""
__author__ = "Richard Smith"
__date__ = "02 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import logging
import os
from datetime import datetime

from tqdm import tqdm

from stac_generator.core.generator import BaseGenerator
from stac_generator.core.input import BaseInput

logger = logging.getLogger(__name__)


class FileSystemInput(BaseInput):
    """
    Performs an os.walk to provide a stream of messages for procesing.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.root_path = kwargs["path"]
        self.kwargs = kwargs.get("kwargs", {})

    def run(self, generator: BaseGenerator):
        total_files = 0
        start = datetime.now()
        for root, _, files in tqdm(os.walk(self.root_path, **self.kwargs)):
            for file in files:
                filename = os.path.abspath(os.path.join(root, file))

                if self.should_process(filename):
                    generator.process(filename)
                    logger.debug(f"Input processing: {filename}")
                else:
                    logger.debug(f"Input skipping: {filename}")
                total_files += 1
        end = datetime.now()
        print(f"Processed {total_files} files from {self.root_path} in {end-start}")
