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
import traceback
from datetime import datetime
from os import listdir
from os.path import isdir, isfile, join

from extraction_methods.core.extraction_method import KeyOutputKey
from pydantic import BaseModel, Field

from stac_generator.core.input import Input


class TextFileConf(BaseModel):
    """Text file Config."""

    path: str = Field(
        description="Path to file or directory of files.",
    )
    uri_term: str = Field(
        default="uri",
        description="Attritube to use as uri.",
    )
    extra_terms: list[KeyOutputKey] = Field(
        default=[],
        description="List of extra attributes.",
    )


class TextFileInput(Input):
    """
    Use external file(s) as input to enter data to pass to
    the processor.
    """

    config_class = TextFileConf

    def run(self):

        if isdir(self.conf.path):
            file_list = [
                join(self.conf.path, file)
                for file in listdir(self.conf.path)
                if isfile(join(self.conf.path, file))
            ]

        else:
            file_list = [self.conf.path]

        start = datetime.now()
        total_generated = 0
        unique_lines = set()

        errors_file = "errors.txt"
        failed_file = "failed.txt"

        for file in file_list:
            with (
                open(file, "r", encoding="utf-8") as f,
                open(errors_file, "w+", encoding="utf-8") as errors,
                open(failed_file, "w+", encoding="utf-8") as failed,
            ):
                for line in f:
                    if line not in unique_lines:
                        unique_lines.add(line)

                        try:
                            data = json.loads(line)
                            output = {"uri": data[self.conf.uri_term]}

                            for extra_term in self.conf.extra_terms:
                                output[extra_term.output_key] = data[extra_term.key]

                            yield output
                            total_generated += 1

                        except Exception:
                            failed.write(line)

                            errors.write(line)
                            errors.write(traceback.format_exc())

        end = datetime.now()
        print(f"Processed {total_generated} elasticsearch records in {end-start}")
