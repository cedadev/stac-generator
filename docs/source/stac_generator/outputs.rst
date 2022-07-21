
Outputs
=======

.. automodule:: stac_generator.plugins.outputs

.. list-table::
   :header-rows: 1

   * - Plugin Name
     - Description
     - Required packages
   * - :ref:`standard_out <stac_generator/outputs:standard out>`
     - Useful for debugging and preparing workflows. A simple ``print()``.
     - ``None``
   * - :ref:`elasticsearch <stac_generator/outputs:elasticsearch>`
     - Outputs the metadata directly to Elasticsearch.
     - ``pip install stac-generator[elasticsearch]``
   * - :ref:`text_file <stac_generator/outputs:text file>`
     - Outputs the metadata directly to file.
     - ``None``
   * - :ref:`rabbitmq <stac_generator/outputs:rabbitmq>`
     - Outputs the metadata directly to Elasticsearch.
     - ``pip install stac-generator[pika]``
   * - :ref:`intake_ems <stac_generator/outputs:intake ems>`
     - Outputs the metadata directly to Elasticsearch.
     - ``pip install stac-generator[pika]``
   * - :ref:`json_file <stac_generator/outputs:json file>`
     - Outputs the metadata directly to JSON file.
     - ``None``

.. automodule:: stac_generator.plugins.outputs.standard_out

.. automodule:: stac_generator.plugins.outputs.elasticsearch

.. automodule:: stac_generator.plugins.outputs.text_file

.. automodule:: stac_generator.plugins.outputs.rabbit_mq

.. automodule:: stac_generator.plugins.outputs.intake_ems

.. automodule:: stac_generator.plugins.outputs.json_file
