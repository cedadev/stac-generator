
Input Plugins
=============

.. automodule:: asset_scanner.plugins.input_plugins

.. list-table::
   :header-rows: 1

   * - Plugin Name
     - Description
   * - :ref:`File System Input <asset_scanner/input_plugins:file system input>`
     - Works with POSIX style file systems and performs a python `os.walk <https://docs.python.org/3/library/os.html#os.walk>`_.
   * - :ref:`Object Store Input <asset_scanner/input_plugins:object store input>`
     - Works with S3 endpoints.

.. automodule:: asset_scanner.plugins.input_plugins.file_system_input

.. automodule:: asset_scanner.plugins.input_plugins.object_store_input

.. automodule:: asset_scanner.plugins.input_plugins.intake_esm_input