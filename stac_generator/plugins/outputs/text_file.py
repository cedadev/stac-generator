"""
File Output Backend
-------------------

An output backend which outputs the content generated into a text file
in a location of your choosing.

**Plugin name:** ``file_out``

.. list-table::
    :header-rows: 1

    * - Option
      - Value Type
      - Description
    * - ``filepath``
      - ``str``
      - ``REQUIRED`` Path to output file(s), either directory or specific file to write.

Example Configuration:
    .. code-block:: yaml

        outputs:
            - method: file_out
              filepath: location_to_destination_file

"""
__author__ = "Mahir Rahman"
__date__ = "23 Mar 2022"
__copyright__ = "Copyright 2022 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "kazi.mahir@stfc.ac.uk"

import json
import os

from stac_generator.core.output import BaseOutput


class TextFileOutput(BaseOutput):
    """
    Create/Append to files to export data from
    the processor.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.filepath = self.filepath.rstrip("/")

    def export(self, data: dict) -> None:
        if hasattr(self, "deduplicate"):
            return

        if os.path.isdir(self.filepath):
            filepath = f"{self.filepath}/file_out.txt"
        else:
            filepath = self.filepath

        with open(f"{filepath}", "a") as file:
            message = {
                f"{data['surtype']}_id": data["body"][f"{data['surtype']}_id"],
                "uri": data["uri"],
            }
            file.write(f"{json.dumps(message)}\n")
