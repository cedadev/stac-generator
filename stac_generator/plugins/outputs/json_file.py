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
    * - ``dirpath``
      - ``str``
      - ``REQUIRED`` Path to output directory.
    * - ``filename_term``
      - ``str``
      - ``REQUIRED`` Term to be used for the file name (typically the id).
      

Example Configuration:
    .. code-block:: yaml

        outputs:
            - method: json_out
              dirpath: location_to_destination_file
              filename_term: item_id

"""
__author__ = "Mahir Rahman"
__date__ = "23 Mar 2022"
__copyright__ = "Copyright 2022 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "kazi.mahir@stfc.ac.uk"

import json

from stac_generator.core.output import BaseOutput


class JsonFileOutput(BaseOutput):
    """
    Export data to a json file
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dirpath = self.dirpath.rstrip("/")

    def export(self, data: dict, **kwargs) -> None:
        filepath = f"{self.dirpath}/{data[self.filename_term]}.json"

        with open(filepath, "w+", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
