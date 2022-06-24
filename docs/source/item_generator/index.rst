***************
Item Generator
***************

:fa:`github` `View on Github <https://github.com/cedadev/item-generator>`_

.. toctree::
   :maxdepth: 2
   :hidden:

   user_guide/orientation
   /stac_generator/processors


This library aims to be a generic tool for generating JSON documents which are `STAC <https://github.com/radiantearth/stac-spec/>`_-like.
You should be able to generate fully STAC compliant JSON or generate content which contains
all the relevant information to allow you to construct a valid `STAC item <https://github.com/radiantearth/stac-spec/blob/master/item-spec/item-spec.md>`_.

This library works on the premise that you can build a processing chain for each of your datasets
by chaining together different processors to extract the relevant information. The core facet
extraction chain works on an atomic basis, where input plugins provide a single object for inspection
and output a single JSON object. Item IDs are generated based on selected facets. It is then
up to your downstream processing to aggregate this information together.

Datastores such as Elasticsearch can make use of upserts which will merge the JSON documents in indexing.

Read the :ref:`Orientation <item_generator/user_guide/orientation:orientation>` guide as a introduction into the framework.

Installation
============

At present, not all the required libraries are available via package managers. To install, you'll
need to install the dependencies using the ``requirements.txt``

.. code-block:: console

   $ git clone https://github.com/cedadev/item-generator
   $ cd item-generator
   $ pip install -r requirements.txt
   $ pip install .

Configuration
=============

Configuration takes the form a YAML formatted file.

.. list-table::
   :header-rows: 1

   * - Option
     - Description
   * - ``extractor``
     - The python import path to the extractor class. If not specified, it picks up the
       class installed with the entry point ``stac_generator.extractors``
   * - ``item_descriptions.root_directory``
     - ``REQUIRED`` Path to the top level directory containing your dataset specific pipelines
   * - ``inputs``
     - ``REQUIRED`` Must have at least one `input plugin <https://cedadev.github.io/asset-scanner/input_plugins.html>`_.
   * - ``outputs``
     - ``REQUIRED`` Must have at least one `output plugin <https://cedadev.github.io/asset-scanner/output_plugins.html>`_

Sample configuration
---------------------

.. include:: shared/example_config.rst

Configuration for the extraction pipelines is done separately. This could be stored in a different
repository to manage versions and additions from multiple sources. You could then clone or download
this repository and reference it using the ``item_descriptions.root_directory``.
These pipeline files are in the form of `item description files <https://cedadev.github.io/asset-scanner/item_descriptions.html>`_.
These YAML files specify the :ref:`processors <stac_generator/processors:processors>` to use to extract your desired facets.

.. note::
   The item-generator outputs two things:
   1. An item, including facets
   2. An item ID to be applied to the asset.

   These are separated using the namespace argument on the output plugin.


Usage
=====

The tool is called using the `asset-scanner <https://cedadev.github.io/asset-scanner/usage.html>`_

.. program-output:: stac_generator -h

Example:

   .. code-block:: console

      $ stac_generator conf/conf.yml
