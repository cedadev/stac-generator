"""
Text File
---------

Takes file or directory path, uses the dictionary
in the file(s) to pass into the extractor.

**Plugin name:** ``text_file``

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
            - method: text_file
              filepath: input_file(s)_location

"""


import json
from datetime import datetime
from os import listdir
from os.path import isdir, isfile, join

from stac_generator.core.generator import BaseGenerator
from stac_generator.core.input import BaseInput


class TextFileInput(BaseInput):
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

        start = datetime.now()
        total_generated = 0
        unique_lines = set()

        for file in self.file_list:
            with open(file, "r", encoding="utf-8") as f:
                for line in f:
                    if line not in unique_lines:
                        total_generated += 1
                        unique_lines.add(line)
                        data = json.loads(line)
                        generator.process(**data)

        end = datetime.now()
        print(f"Processed {total_generated} elasticsearch records in {end-start}")

