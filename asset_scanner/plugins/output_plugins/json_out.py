"""
File Output Backend
-------------------

An output backend which outputs the content generated into a JSON file
in a location of your choosing.
This is only to be used for testing purposes and not suitable for large
scale application.

**Plugin name:** ``json_out``

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
            - name: json_out
              namespace: header
              filepath: location_to_destination_file

"""

import json
import os

from .base import OutputBackend


class JsonOutputBackend(OutputBackend):
    def __init__(self, namespace=None, **kwargs):
        super().__init__(namespace, **kwargs)
        self.filepath: str = kwargs["filepath"]
        self.filepath = self.filepath.rstrip("/")

    def export(self, data, **kwargs):

        if os.path.isdir(self.filepath):
            filepath = f"{self.filepath}/json_out.json"
        else:
            filepath = self.filepath

        mode = "r+" if os.path.exists(filepath) else "w+"

        with open(filepath, mode) as file:
            try:
                file_data = json.load(file)
                file_data.append(data)

            except json.JSONDecodeError:
                file_data = [data]

            file.seek(0)

            json.dump(file_data, file, indent=4)
