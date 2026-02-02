__author__ = "Mahir Rahman"
__date__ = "23 Mar 2022"
__copyright__ = "Copyright 2022 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "kazi.mahir@stfc.ac.uk"

import json
import os

from pydantic import BaseModel, Field

from stac_generator.core.output import Output


class JsonFileConf(BaseModel):
    """JSON config model."""

    filename: str = Field(
        default="$id",
        description="Term to use for the JSON file name.",
    )
    pop: bool = Field(
        default=False,
        description="If the field used for the id should be removed from the data.",
    )
    dirpath: str = Field(
        description="Root directory for JSON files.",
    )


class JsonFileOutput(Output):
    """
    Output to a JSON file.

    **Plugin name:** ``json_out``

    Example Configuration:
        .. code-block:: yaml

            - name: json_out
              conf:
                dirpath: location_to_destination_file
                filename_term: item_id
    """

    config_class = JsonFileConf

    def export(self, data: dict, **kwargs) -> None:

        filename = self.conf.file_field
        if self.conf.file_field[0] == "$":
            filename = data.pop(filename[1:]) if self.conf.pop else data[filename[1:]]

        filepath = os.path.join(self.conf.dirpath, filename)

        with open(filepath, "w+", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
