# encoding: utf-8
"""
File System Input
-----------------

Takes a path and will scan the file system, submitting
each file to the asset extractor

**Plugin name:** ``file_system``

Example Configuration:
    .. code-block:: yaml

        inputs:
            - name: file_system
              path: test_directory

Config Arguments:
    path
        The root path to scan

"""
__author__ = 'Richard Smith'
__date__ = '02 Jun 2021'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'


from .base import BaseInputPlugin

import os
from datetime import datetime

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from asset_scanner.core import BaseExtractor


class FileSystemInputPlugin(BaseInputPlugin):
    """
    """

    def __init__(self, **kwargs):

        self.root_path = kwargs['path']

    def run(self, extractor: 'BaseExtractor' ):
        total_files = 0
        start = datetime.now()
        for root, _, files in os.walk(self.root_path):
            for file in files:
                filename = os.path.abspath(os.path.join(root, file))
                extractor.process_file(filename, 'posix')
                total_files += 1
        end = datetime.now()
        print(f'Processed {total_files} files from {self.root_path} in {end-start}')
