**************
STAC Generator
**************

:fa:`github` `View on Github <https://github.com/cedadev/stac-generator>`_

This library aims to be a generic tool for generating JSON documents which are `STAC <https://github.com/radiantearth/stac-spec/>`_-like.
You should be able to generate fully STAC compliant JSON or generate content which contains
all the relevant information to allow you to construct a valid `STAC item <https://github.com/radiantearth/stac-spec/blob/master/item-spec/item-spec.md>`_.

This library works on the premise that you can build a processing chain for each of your datasets
by chaining together different processors to extract the relevant information. The core facet
extraction chain works on an atomic basis, where input plugins provide a single object for inspection
and output a single JSON object. Item IDs can be generated based on selected facets.
Downstream processing can then be used to aggregate this information together.

Datastores such as Elasticsearch can make use of upserts which will merge the JSON documents in indexing.

Read the :ref:`Orientation <stac_generator/user_guide/orientation>` guide as a introduction into the framework.

Installing
==========

.. code-block:: console

   pip install stac-generator

Usage
======

There is a console script defined by this package which can be used to run the
extractors ``stac_generator``.

.. code-block:: console

    usage: stac_generator [-h] conf

    Run the STAC Generator as configured

    positional arguments:
      conf        Path to a yaml configuration file

    optional arguments:
      -h, --help  show this help message and exit


Configuration
==============

The configuration file feeds this top level script and configures the inputs/outputs 
as well as the generator.

Base configuration options:
---------------------------

.. list-table::
   :header-rows: 1

   * - Option
     - Description
   * - ``generator``
     - The name of the generator ``asset``, ``item``, ``collection``
   * - ``collection_descriptions``
     - ``REQUIRED`` Path to the root directory for the collection descriptions. Used to describe workflows.
   * - ``inputs``
     - ``REQUIRED`` Must have at least one `input <stac_generator/inputs>`_.
   * - ``outputs``
     - ``REQUIRED`` Must have at least one `output <stac_generator/outputs>`_
   * - ``logging``
     - Kwargs passed to the `logging.basicConfig <https://docs.python.org/3/library/logging.html#logging.basicConfig>`_ setup method

The generator can be specified in the configuration file or can be loaded from
an entry point. The configuration value takes precedence over entry points.

.. warning::
    Only the first generator will be loaded from entry points.

Sample configuration
--------------------

   .. code-block:: yaml

      generator: item
      item_descriptions:
         root_directory: /home/users/rsmith013/search_futures/collections-descriptions/descriptions
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
capabilities to fit your needs. The Asset Scanner holds the Inputs/Outputs,
filters to modify these plugins and "processors" which are used to extract values
from the files.

The processors are used to either extract content from the filename/path, headers
or third-party sources.


.. toctree::
   :maxdepth: 3

   inputs
   outputs
   filters
   processors
