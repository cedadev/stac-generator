"""
JSON File
---------

Takes file or directory path, uses the dictionary
in the file(s) to pass into the extractor.

**Plugin name:** ``json_file``

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
            - method: json_file
              filepath: input_file(s)_location

"""


import json
from os import listdir
from os.path import isdir, isfile, join

from stac_generator.core.generator import BaseGenerator
from stac_generator.core.input import BaseInput


class JsonFileInput(BaseInput):
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
                    data = json.loads(line)
                    generator.process(**data)
