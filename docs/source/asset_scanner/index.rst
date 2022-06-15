*************
Asset Scanner
*************

:fa:`github` `View on Github <https://github.com/cedadev/asset-scanner>`_

Installing
==========

.. code-block:: console

   pip install asset-scanner

Usage
======

There is a console script defined by this package which can be used to run the
extractors ``asset_generator``.

.. code-block:: console

    usage: asset_scanner [-h] conf

    Run the asset scanner as configured

    positional arguments:
      conf        Path to a yaml configuration file

    optional arguments:
      -h, --help  show this help message and exit


Configuration
==============

The configuration file feeds this top level script and configures the input/output
plugins as well as the extractor class. You will need to see the extractor documentation
to get additional configuration options.

Base configuration options:
---------------------------

.. list-table::
   :header-rows: 1

   * - Option
     - Description
   * - ``extractor``
     - The python import path to the extractor class. If not specified, it picks up the class installed with the entry point ``asset_scanner.extractors``
   * - ``item_descriptions``
     - ``REQUIRED`` Path to the root directory for the item descriptions. Used to describe workflows.
   * - ``inputs``
     - ``REQUIRED`` Must have at least one `input plugin <https://cedadev.github.io/asset-scanner/input_plugins.html>`_.
   * - ``outputs``
     - ``REQUIRED`` Must have at least one `output plugin <https://cedadev.github.io/asset-scanner/output_plugins.html>`_
   * - ``logging``
     - Kwargs passed to the `logging.basicConfig <https://docs.python.org/3/library/logging.html#logging.basicConfig>`_ setup method

The extractor can be specified in the configuration file or can be loaded from
an entry point. The configuration value takes precedence over entry points.

.. warning::
    Only the first extractor will be loaded from entry points.

Sample configuration
--------------------

   .. code-block:: yaml

      extractor: item_generator.FacetGenerator
      item_descriptions:
         root_directory: /home/users/rsmith013/search_futures/item-descriptions/descriptions
      inputs:
        - method: file_system
          path: /badc/faam/data/2005/b069-jan-05
      outputs:
        - method: standard_out
      logging:
         level: INFO


Plugins
=======

Plugins are used to add modular components and allow extension of the base
capabilities to fit your needs. The Asset Scanner holds the Input/Output plugins,
filters to modify these plugins and "processors" which are used to extract values
from the files.

The processors are used to either extract content from the filename/path, headers
or third-party sources.


.. toctree::
   :maxdepth: 3

   input_plugins
   output_plugins
   plugin_filters
   processors
