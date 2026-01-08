import json
from datetime import datetime
from os import listdir
from os.path import isdir, isfile, join

from extraction_methods.core.types import KeyOutputKey
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
    Reads lines from file/files as a source for events.

    **Plugin name:** ``text_file``

    Example Configuration:
        .. code-block:: yaml

            - name: text_file
              conf:
                filepath: /path/to/files
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

        for file in file_list:
            with (open(file, "r", encoding="utf-8") as f,):
                for line in f:
                    if line not in unique_lines:
                        unique_lines.add(line)

                        data = json.loads(line)
                        output = {"uri": data[self.conf.uri_term]}

                        for extra_term in self.conf.extra_terms:
                            output[extra_term.output_key] = data[extra_term.key]

                        yield output
                        total_generated += 1

        end = datetime.now()
        print(f"Processed {total_generated} elasticsearch records in {end-start}")
