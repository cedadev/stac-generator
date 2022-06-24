
Output Plugins
===============

.. automodule:: stac_generator.plugins.output_plugins

.. list-table::
   :header-rows: 1

   * - Plugin Name
     - Description
     - Required packages
   * - :ref:`Standard Out <stac_generator/output_plugins:standard out>`
     - Useful for debugging and preparing workflows. A simple ``print()``.
     - ``None``
   * - :ref:`Elasticsearch <stac_generator/output_plugins:elasticsearch>`
     - Outputs the metadata directly to Elasticsearch.
     - ``pip install asset-scanner[elasticsearch]``

.. automodule:: stac_generator.plugins.output_plugins.standard_out
.. automodule:: stac_generator.plugins.output_plugins.elasticsearch_backend
