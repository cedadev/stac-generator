__author__ = "Mahir Rahman"
__date__ = "23 Mar 2022"
__copyright__ = "Copyright 2022 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "kazi.mahir@stfc.ac.uk"

import os

from pydantic import BaseModel, Field

from stac_generator.core.output import Output


class TextFileConf(BaseModel):
    """Text File config model."""

    filepath: str = Field(
        description="Path to text file.",
    )


class TextFileOutput(Output):
    """
    Outputs to a text file.

    **Plugin name:** ``file_out``

    Example Configuration:
        .. code-block:: yaml

            - name: file_out
              conf:
                filepath: location_to_destination_file
    """

    config_class = TextFileConf

    def export(self, data: dict, **kwargs) -> None:

        if os.path.isdir(self.conf.filepath):
            self.conf.filepath = os.path.join(self.conf.filepath, "file_out.txt")

        with open(self.conf.filepat, "a", encoding="utf-8") as file:
            file.write(f"{data}\n")
