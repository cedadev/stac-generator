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
      - ``namespace``
      - ``str``
      - Can be used by downstream processors to capture specific outputs.

Example Configuration:
    .. code-block:: yaml

        outputs:
            - name: file_out
              namespace: header
              filepath: location_to_destination_file

"""


import json
import os

from .base import OutputBackend


class FileoutOutputBackend(OutputBackend):
    """
    Create or overwrite files to export data from
    the processor.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.filepath: str = kwargs["filepath"]
        self.filepath = self.filepath.rstrip("/")

    def export(self, data: dict, **kwargs) -> None:

        if os.path.isdir(self.filepath):
            filepath = f"{self.filepath}/file_out.txt"
        else:
            filepath = self.filepath

        with open(f"{filepath}", "a") as file:
            file.write(f"{json.dumps(data)}\n")
