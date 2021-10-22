
Input Plugins
=============

.. automodule:: asset_scanner.plugins.input_plugins

.. list-table::
   :header-rows: 1

   * - Plugin Name
     - Description
     - Required packages
   * - :ref:`File System Input <asset_scanner/input_plugins:file system input>`
     - Works with POSIX style file systems and performs a python `os.walk <https://docs.python.org/3/library/os.html#os.walk>`_.
     - ``None``
   * - :ref:`Object Store Input <asset_scanner/input_plugins:object store input>`
     - Works with S3 endpoints.
     -
   * - :ref:`Intake ESM Input <asset_scanner/input_plugins:intake input>`
     - Use/search and intake ESM catalog to provide a source of paths.
     - ``pip install asset-scanner[intake-esm]``
   * - :ref:`RabbitMQ Input <asset_scanner/input_plugins:rabbitmq input>`
     - Connect to a RabbitMQ message queue.
     - ``pip install asset-scanner[rabbitmq]``

.. automodule:: asset_scanner.plugins.input_plugins.file_system_input

.. automodule:: asset_scanner.plugins.input_plugins.object_store_input

.. automodule:: asset_scanner.plugins.input_plugins.intake_esm_input

.. automodule:: asset_scanner.plugins.input_plugins.rabbit_mq_input