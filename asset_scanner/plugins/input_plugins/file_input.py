"""
File Input
----------

Takes file or directory path, uses the dictionary
in the file(s) to pass into the extractor.

**Plugin name:** ``file_input``

.. list-table::
    :header-rows: 1

    * - Option
      - Value Type
      - Description
    * - ``filepath``
      - ``string``
      - ``REQUIRED`` the path to input file(s)

Example Configuration:
    .. code-block:: yaml

        inputs:
            - method: file_input
              filepath: input_file(s)_location

"""


import json
from os import listdir
from os.path import isdir, isfile, join

from asset_scanner.core.generator import BaseGenerator
from asset_scanner.types.source_media import StorageType

from .base import BaseInputPlugin


class FileInputPlugin(BaseInputPlugin):
    """
    Use external file(s) as input to enter data to pass to
    the processor.
    """

    def __init__(self, **kwargs):
        self.filepath = kwargs["filepath"]

        if isdir(self.filepath):
            self.file_list = [
                join(self.filepath, file)
                for file in listdir(self.filepath)
                if isfile(join(self.filepath, file))
            ]
        else:
            self.file_list = [self.filepath]

    def run(self, generator: BaseGenerator):

        for file in self.file_list:
            with open(file) as f:
                for line in f:
                    filepath = json.loads(line)
                    generator.process(filepath)
