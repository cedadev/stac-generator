# encoding: utf-8
"""
File System Input
-----------------

Takes a path and will scan the file system, submitting
each file to the asset extractor

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
      - :ref:`PluginFilter <asset_scanner/plugin_filters:plugin filters>`
      - Optional filter plugins

Example Configuration:
    .. code-block:: yaml

        inputs:
            - name: file_system
              path: test_directory

"""
__author__ = 'Richard Smith'
__date__ = '02 Jun 2021'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'


from .base import BaseInputPlugin
from asset_scanner.types.source_media import StorageType
from tqdm import tqdm

import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from asset_scanner.core import BaseExtractor


class FileSystemInputPlugin(BaseInputPlugin):
    """
    Performs an os.walk to provide a stream of paths for procesing.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.root_path = kwargs['path']
        self.kwargs = kwargs.get('kwargs', {})

    def run(self, extractor: 'BaseExtractor' ):
        total_files = 0
        start = datetime.now()
        for root, _, files in tqdm(os.walk(self.root_path, **self.kwargs)):
            for file in files:
                filename = os.path.abspath(os.path.join(root, file))

                if self.should_process(filename, StorageType.POSIX):
                    extractor.process_file(filename, StorageType.POSIX)
                    logger.debug(f'Input processing: {filename}')
                else:
                    logger.debug(f'Input skipping: {filename}')
                total_files += 1
        end = datetime.now()
        print(f'Processed {total_files} files from {self.root_path} in {end-start}')
