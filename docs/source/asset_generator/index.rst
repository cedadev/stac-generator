.. asset_extractor documentation master file, created by
   sphinx-quickstart on Tue Jun  1 17:21:29 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

***************
Asset Generator
***************

The asset extractor indexes individual file objects.
The asset extractor is used to gather file level metadata where
the file is the source of truth. i.e. Checksum, location, size, modified time.

Installation
============

At present, not all the required libraries are available via package managers. To install, you’ll need to install the dependencies using the requirements.txt


.. code-block:: console

   git clone https://github.com/cedadev/asset-extractor
   cd asset-extractor
   pip install -r requirements.txt
   pip install .



Configuration
=============

Configuration takes the form a YAML formatted file.
There is some dataset level configuration for labelling the file type (e.g. ``data``, ``metadata``)
and is provided in the form of the `item description files <https://cedadev.github.io/asset-scanner/item_descriptions.html>`_.

.. list-table::
   :header-rows: 1

   * - Option
     - Description
   * - ``item_descriptions.root_directory``
     - ``REQUIRED`` Path to the top level directory containing your dataset specific pipelines
   * - ``inputs``
     - ``REQUIRED`` Must have at least one `input plugin <https://cedadev.github.io/asset-scanner/input_plugins.html>`_.
   * - ``outputs``
     - ``REQUIRED`` Must have at least one `output plugin <https://cedadev.github.io/asset-scanner/output_plugins.html>`_
   * - ``extractor``
     - The python import path to the extractor class. If not specified, it picks up the
       class installed with the entry point ``asset_scanner.extractors``
   * - ``media_handlers``
     - Kwargs to be passed to the media handlers


Item Description Relevant Fields
---------------------------------

- `Datasets <https://cedadev.github.io/asset-scanner/item_descriptions.html#datasets>`_
- `Categories <https://cedadev.github.io/asset-scanner/item_descriptions.html#categories>`_

Sample configuration:
---------------------

   .. code-block:: yaml

      extractor: asset_extractor.AssetExtractor
      item_descriptions:
        root_directory: /etc/item-generator/item_descriptions/descriptions
      inputs:
        - name: file_system
          path: /badc/faam/data/2005/b069-jan-05
      outputs:
        - name: standard_out


Usage
=====

The tool is called using the `asset-scanner <https://cedadev.github.io/asset-scanner/usage.html>`_

.. program-output:: asset_scanner -h

Example:

   .. code-block:: console

      $ asset_scanner conf/conf.yml
