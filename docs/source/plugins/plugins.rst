Plugins
=======

Plugins are used to add modular components and allow extension of the base
capabilities to fit your needs. The Asset Scanner holds the Input/Output plugins
as well as filters to modify these plugins.

Input Plugins
--------------

These are used to provide a stream of file objects to the extractor.

Entrypoint: ``asset_scanner.input_plugins``

.. list-table::
   :header-rows: 1

   * - Plugin Name
     - Description
   * - :ref:`File System Input <plugins/input_plugins:file system input>`
     - Works with POSIX style file systems and performs a python `os.walk <https://docs.python.org/3/library/os.html#os.walk>`_.
   * - :ref:`Object Store Input <plugins/input_plugins:object store input>`
     - Works with S3 endpoints.

.. toctree::
   :maxdepth: 3
   :hidden:

   input_plugins

Output Plugins
--------------

These are used to handle the output from the extraction phase. This could be to disk, a database or queue for further processing.

Entrypoint: ``asset_scanner.output_plugins``

.. list-table::
   :header-rows: 1

   * - Plugin Name
     - Description
   * - :ref:`Standard Out <plugins/output_plugins:standard out>`
     - Useful for debugging and preparing workflows. A simple ``print()``.
   * - :ref:`Elasticsearch <plugins/output_plugins:elasticsearch>`
     - Outputs the metadata directly to Elasticsearch.

.. toctree::
   :maxdepth: 3
   :hidden:

   output_plugins

Plugin Filters
---------------

Filters can be used to modify the stream of events and intercept them before any action is performed. E.g. Only process
certain files from an input plugin.

Entrypoint: ``asset_scanner.plugin_filters``

.. list-table::
   :header-rows: 1

   * - Plugin Name
     - Description
   * - :ref:`Path Regex <plugins/plugin_filters:path regex filter>`
     - Can be used to pattern match against the path to either include/exclude.

.. toctree::
   :maxdepth: 3
   :hidden:

   plugin_filters