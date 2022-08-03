"""
Intake-ESM Output Backend
-------------------------

An output backend which outputs the content generated into a JSON catalog description and a zipped CSV file
at a location of your choosing.

This is only to be used for testing purposes and not suitable for large
scale application.

Note also that the CSV header is constructed from the first data payload processed. If there are attribute variations
across files, attribute columns may not align, which will yield an invalid catalog.

**Plugin name:** ``intake_esm_out``

.. list-table::
    :header-rows: 1

    * - Option
      - Value Type
      - Description
    * - ``filepath``
      - ``str``
      - ``REQUIRED`` Path to output file(s), either directory or specific file to write.
    * - ``collection``
      - ``str``
      - Collection name. If `filepath` is a directory, `collection` will be used as the output file name.
    * - ``description``
      - ``str``
      - Textual description of the collection.

Example Configuration:
    .. code-block:: yaml

        outputs:
            - name: intake_esm_out
              filepath: location/to/destination_files/
              collection: my_collection
              description: A long form description of the dataset catalog.

"""
__author__ = "David Huard"
__date__ = "June 2022"
__copyright__ = "Copyright 2022 Ouranos"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "huard.david@ouranos.ca"

import json
import os

from stac_generator.core.output import BaseOutput

ESMCAT_VERSION = "0.1.0"
ASSET_FORMAT = {".nc": "netcdf", ".zarr": "zarr"}


class IntakeESMOutput(BaseOutput):
    """
    Export data to
    - a json catalog description file
    - a zipped CSV content file
    """

    def __init__(self, collection="", description="", **kwargs):
        super().__init__(namespace="asset", **kwargs)
        self.filepath: str = kwargs["filepath"]
        self.filepath = self.filepath.rstrip("/")

        self.collection = collection or "collection"
        self.description = description

        if os.path.isdir(self.filepath):
            self.filepath = self.filepath + "/" + self.collection

        self.json_path = self.filepath + ".json"
        self.csv_path = self.filepath + ".csv.gz"

    def export(self, data, **kwargs):
        """Write data to disk."""
        import csv
        import gzip

        if not os.path.exists(self.json_path):
            # Create catalog spec file and CSV file with header and first data row
            mode = "wt"

            # Write ESM-Collection json file
            with open(self.json_path, mode) as f:
                json.dump(self.to_intake_spec(data), f)

            # Write catalog data in csv.gz format
            with gzip.open(filename=self.csv_path, mode=mode) as f:
                w = csv.writer(f)
                w.writerow(self.properties(data))
                w.writerow(self.data2row(data))

        else:
            # Append new data row to CSV file
            mode = "at"
            with gzip.open(filename=self.csv_path, mode=mode) as f:
                w = csv.writer(f)
                w.writerow(self.data2row(data))

    @staticmethod
    def properties(data):
        """Return list of property names.

        Note that results may vary from one item to the next.
        """
        return list(data["body"]["properties"].keys())

    @staticmethod
    def data2row(data):
        """Return list of property values."""
        return list(data["body"]["properties"].values())

    def to_intake_spec(self, data):
        """Return Intake specification file content."""

        attributes = [{"column_name": key} for key in self.properties(data)]
        ext = data["body"]["extension"]

        spec = {
            "esmcat_version": ESMCAT_VERSION,
            "id": self.namespace,
            "description": self.description,
            "catalog_file": self.csv_path,
            "attributes": attributes,
            "assets": {"column_name": "path", "format": ASSET_FORMAT[ext]},
        }
        return spec
