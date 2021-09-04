.. asset_scanner documentation master file, created by
   sphinx-quickstart on Tue Jun  8 15:30:14 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

**************
Asset Scanner
**************

The asset scanner provides base functionality and a script to run various different
scanners which operate at a file level. These extractors run on each file and return
content based on the configuration file.

Current implementations of the Extractor are:
   - `Asset Extractor <https://github.com/cedadev/asset-extractor>`_
   - `Facet Extractor <https://github.com/cedadev/item-generator>`_

Both of these implementation make use of :ref:`item description <item-descriptions>` files.

Installing
==========

.. code-block:: console

   pip install git+https://github.com/cedadev/asset-scanner

Usage
======

There is a console script defined by this package which can be used to run the
extractors ``asset_extractor``.

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
an entry point. The configuration value take precedence over entry points.

.. warning::
    Only the first extractor will be loaded from entry points.

Sample configuration
--------------------

   .. code-block:: yaml

      extractor: item_generator.FacetExtractor
      item_descriptions:
         root_directory: /home/users/rsmith013/search_futures/item-descriptions/descriptions
      inputs:
        - name: file_system
          path: /badc/faam/data/2005/b069-jan-05
      outputs:
        - name: standard_out
      logging:
         level: INFO


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   item_descriptions
   input_plugins
   output_plugins


.. toctree::
   :maxdepth: 2
   :caption: API:

   extractor



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
