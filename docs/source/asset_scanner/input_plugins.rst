
Input Plugins
=============

.. automodule:: stac_generator.plugins.input_plugins

.. list-table::
   :header-rows: 1

   * - Plugin Name
     - Description
     - Required packages
   * - :ref:`File System Input <stac_generator/input_plugins:file system input>`
     - Works with POSIX style file systems and performs a python `os.walk <https://docs.python.org/3/library/os.html#os.walk>`_.
     - ``None``
   * - :ref:`Object Store Input <stac_generator/input_plugins:object store input>`
     - Works with S3 endpoints.
     -
   * - :ref:`Intake ESM Input <stac_generator/input_plugins:intake input>`
     - Use/search and intake ESM catalog to provide a source of paths.
     - ``pip install asset-scanner[intake-esm]``
   * - :ref:`RabbitMQ Input <stac_generator/input_plugins:rabbitmq input>`
     - Connect to a RabbitMQ message queue.
     - ``pip install asset-scanner[rabbitmq]``
   * - :ref:`Thredds Input <stac_generator/input_plugins:thredds input>`
     - Use a THREDDS catalog as a source
     - ``pip install asset-scanner[thredds]``

.. automodule:: stac_generator.plugins.input_plugins.file_system_input

.. automodule:: stac_generator.plugins.input_plugins.object_store_input

.. automodule:: stac_generator.plugins.input_plugins.intake_esm_input

.. automodule:: stac_generator.plugins.input_plugins.rabbit_mq_input

.. automodule:: stac_generator.plugins.input_plugins.thredds_input
