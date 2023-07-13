
***********************
Collection Descriptions
***********************

.. toctree::
    :hidden:

    building_a_workflow


These documents describe how to process the files within a dataset and extract facets.
These documents are aggregated along the branch with the information lower in the tree taking
precendence.
Having multiple files at different points in the tree allow for a narrowing of information.
i.e. A default set at a higher level, if not overwritten, will exist at all points down the tree.

Example Description File
========================

This file applies to all files listed under: ``/badc/faam/data``.

It uses the regex processor in two forms. The first, uses a pre-processor
to reduce the filepath to just the filename and then matches a regex pattern to
extract a date. This is then passed to the ISO Date post-processor which converts
the date into the ISO8601 format.

The second, extracts platform and flight number from the filepath.
No pre or post processing is done in this case.

.. code-block:: yaml

    paths:
      - /badc/faam/data
    asset:
      extraction_methods:
        - method: regex
          inputs:
            regex: '^(?:[^_]*_){2}(?P<datetime>\d*)'

Description file sections
=========================

The description file consists of 5 top level keys:

A :ref:`Full JSON Schema<collection_descriptions/collection_descriptions:schema>` references below.

.. list-table::
  :header-rows: 1

  * - Key
    - Type
    - Description
    - Example
  * - ``paths``
    - list
    - List of paths this workflow applies to.
    - :ref:`Paths<collection_descriptions/collection_descriptions:paths>`
  * - ``asset``
    - :ref:`Collections <collection_descriptions/collection_descriptions:asset>`
    - Defines the extraction methods to create the assets matching the given path.
  * - ``item``
    - :ref:`Collections <collection_descriptions/collection_descriptions:item>`
    - Defines the ID and extraction methods to create the items matching the given path.
  * - ``collection``
    - :ref:`Collections <collection_descriptions/collection_descriptions:collection>`
    - Defines the ID and extraction methods to create the collection matching the given path.
  * - ``Categories``
    - list
    - Used by the asset generator to assign categories to files.
      By default, all files are given the category data.
    - :ref:`Categories <collection_descriptions/collection_descriptions:Categories>`

Paths
-----

Describes the paths where this file applies. Can be multiple locations.
The path references all points below it in the hierarchy.

.. code-block:: yaml

    paths:
        - /badc/faam/data

Asset, Item, & Collection
-------------------------

.. list-table::
   :header-rows: 1

   * - Key
     - Type
     - Description
     - Example
   * - ``id``
     - :ref:`ID extration methods <stac_generator/processors:id-extraction-methods>`
     - ID for the generated object
     - `sentinel3`
   * - ``extration_methods``
     - :ref:`Extration methods <stac_generator/processors:extraction-methods>`
     - A list of functions to run, and their arguments.

.. code-block:: yaml

    collections:
        id:
          method: default
          inputs:
            value: sentinel3
        extraction_methods:
           - method: regex
             inputs:
              regex: '^\/(?:[^/]*/)(?P<platform>\w*)\/(?:[^/]*/){2}(?P<flight_number>\w\d{3})'

Categories
-----------

Used by the asset extractor to assign categories to files.
By default, all files are given the category data.

.. code-block:: yaml

    categories:
        label: metadata
        regex: 00README

Schema
-------

.. program-output:: python -c "from stac_generator.core.item_describer import ItemDescription; import json; print(json.dumps(ItemDescription.schema(), indent=4))"
