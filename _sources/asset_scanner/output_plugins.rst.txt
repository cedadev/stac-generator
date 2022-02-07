
Output Plugins
===============

.. automodule:: asset_scanner.plugins.output_plugins

.. list-table::
   :header-rows: 1

   * - Plugin Name
     - Description
     - Required packages
   * - :ref:`Standard Out <asset_scanner/output_plugins:standard out>`
     - Useful for debugging and preparing workflows. A simple ``print()``.
     - ``None``
   * - :ref:`Elasticsearch <asset_scanner/output_plugins:elasticsearch>`
     - Outputs the metadata directly to Elasticsearch.
     - ``pip install asset-scanner[elasticsearch]``

.. automodule:: asset_scanner.plugins.output_plugins.standard_out
.. automodule:: asset_scanner.plugins.output_plugins.elasticsearch_backend
