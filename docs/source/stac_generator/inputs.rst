
Inputs
======

.. automodule:: stac_generator.plugins.inputs

.. list-table::
   :header-rows: 1

   * - Plugin Name
     - Description
     - Required packages
   * - :ref:`file_system <stac_generator/inputs:file system>`
     - Works with POSIX style file systems and performs a python `os.walk <https://docs.python.org/3/library/os.html#os.walk>`_.
     - ``None``
   * - :ref:`object_store <stac_generator/inputs:object store>`
     - Works with S3 endpoints.
     - ``pip install asset-scanner[boto3]``
   * - :ref:`intake_esm <stac_generator/inputs:intake esm>`
     - Use/search and intake ESM catalog to provide a source of paths.
     - ``pip install asset-scanner[intake-esm]``
   * - :ref:`rabbit_mq <stac_generator/inputs:rabbitmq>`
     - Connect to a RabbitMQ message queue.
     - ``pip install asset-scanner[rabbitmq]``
   * - :ref:`thredds <stac_generator/inputs:thredds>`
     - Use a THREDDS catalog as a source
     - ``pip install asset-scanner[thredds]``

.. automodule:: stac_generator.plugins.inputs.file_system

.. automodule:: stac_generator.plugins.inputs.object_store

.. automodule:: stac_generator.plugins.inputs.intake_esm

.. automodule:: stac_generator.plugins.inputs.rabbit_mq

.. automodule:: stac_generator.plugins.inputs.thredds
