
******************
Item Descriptions
******************

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

Finally the platform and flight number are used to generate a string which will
identify all files in this dataset as belonging together.

.. code-block:: yaml

    paths:
      - /badc/faam/data
    facets:
      extraction_methods:
        - name: regex
          inputs:
            regex: '^(?:[^_]*_){2}(?P<datetime>\d*)'
          pre_processors:
            - name: filename_reducer
          post_processors:
            - name: isodate_processor
              inputs:
                date_key: datetime
        - name: regex
          inputs:
            regex: '^\/(?:[^/]*/)(?P<platform>\w*)\/(?:[^/]*/){2}(?P<flight_number>\w\d{3})'
      aggregation_facets:
        - platform
        - flight_number


Description file sections
==========================

The description file consists of 4 top level keys:

A :ref:`Full JSON Schema<item_descriptions/item_descriptions:schema>` references below.

.. list-table::
   :header-rows: 1

   * - Key
     - Type
     - Description
     - Example
   * - ``paths``
     - list
     - List of paths this workflow applies to.
     - :ref:`Paths<item_descriptions/item_descriptions:Paths>`
   * - ``Collections``
     - :ref:`Collections <item_descriptions/item_descriptions:Collections>`
     - Defines the workflow and ID to create a collection for the applicable files.
     - :ref:`Collections <item_descriptions/item_descriptions:Collections>`
   * - ``Facets``
     - :ref:`Facets <item_descriptions/item_descriptions:Facets>`
     - Defines the workflow to create items.
     - :ref:`Facets <item_descriptions/item_descriptions:Facets>`
   * - ``Categories``
     - list
     - Used by the asset extractor to assign categories to files.
       By default, all files are given the category data.
     - :ref:`Categories <item_descriptions/item_descriptions:Categories>`

Paths
--------

Describes the paths where this file applies. Can be multiple locations.
The path references all points below it in the hierarchy.

.. code-block:: yaml

    paths:
        - /badc/faam/data

Collections
-----------

.. list-table::
   :header-rows: 1

   * - Key
     - Type
     - Description
     - Example
   * - ``id``
     - string
     - ID for the defined collection
     - `sentinel3`
   * - ``templates``
     - :ref:
     - ID for the defined collection
     - `sentinel3`
   * -
     - :ref:`Processor <item_descriptions/item_descriptions:processor>`
     - Defines the keys for the processor workflow.
     -

.. code-block:: yaml

    collections:
        id: sentinel3
        extraction_methods:
           ...

Facets
-------

.. list-table::
   :header-rows: 1

   * - Key
     - Type
     - Description
     - Example
   * - ``aggregation_facets``
     - list
     - List of facets which define files which should be grouped together. e.g.
       All files which have the same value for the facets listed here, should become
       a single item.
     - .. code-block:: yaml

            aggregation_facets:
                - platform
                - flight_number
   * - ``search_facets``
     - list
     - List of facets additonal facets which are useful for searching.
       This list will be added to the aggregation facets list to generate a summary
       at the collection level. This is used to feed faceted search.
     - .. code-block:: yaml

            search_facets:
                - platform
                - flight_number
   * -
     - :ref:`Processor <item_descriptions/item_descriptions:processor>`
     - Defines the keys for the processor workflow.
     -

.. code-block:: yaml

    facets:
        extraction_methods:
        - name: regex
          inputs:
            regex: '^(?:[^_]*_){2}(?P<datetime>\d*)'
          pre_processors:
            - name: filename_reducer
          post_processors:
            - name: isodate_processor
              inputs:
                date_key: datetime
        - name: regex
          inputs:
            regex: '^\/(?:[^/]*/)(?P<platform>\w*)\/(?:[^/]*/){2}(?P<flight_number>\w\d{3})'
      aggregation_facets:
        - platform
        - flight_number
      search_facets:
         -

Categories
-----------

Used by the asset extractor to assign categories to files.
By default, all files are given the category data.

.. code-block:: yaml

    categories:
        label: metadata
        regex: 00README

Processor
~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Key
     - Type
     - Description
     - Example
   * - ``defaults``
     - mapping
     - Default facet values to apply for all files in the absence of any other information.
     -  .. code-block:: yaml

            defaults:
                datetime: "2020-05-01T10:03:00"

   * - ``mappings``
     - mapping
     - Allows you to map one term to another. This can be used to map multi-values or
       correct values where they are known to be incorrect.
     - .. code-block:: yaml

            mappings:
                term1: value1
                term2: value2

   * - ``overrides``
     - mapping
     - No matter what comes from the file, this is the value to be used
     - .. code-block:: yaml

            overrides:
                platform: sentinel3

   * - ``extraction_methods``
     - mapping
     - A list of functions to run, and their arguments. A full list of functions and their
       expected parameters can be found `here <https://cedadev.github.io/item-generator/processors.html>`_.

       Extraction methods can use the ``description`` key to allow you to write notes to your future self
       about what the extractor is for. This is not used in running the code.
     - .. code-block:: yaml

            facets:
                extraction_methods:
                - name: regex
                  inputs:
                    regex: '^\/(?:[^/]*/)(?P<platform>\w*)\/(?:[^/]*/){2}(?P<flight_number>\w\d{3})'

   * - ``templates``
     - mapping
     - Used to generate title and description properties from facets using python `string templates <https://docs.python.org/3/library/string.html#template-strings>`_
     - .. code-block:: yaml

            templates:
                title: $platform flight no. $flight_number
                description: Data recorded as part of the $platform project during flight number $flight_number which took place on $datetime.


Schema
-------

.. program-output:: python -c "from asset_scanner.core.item_describer import ItemDescription; import json; print(json.dumps(ItemDescription.schema(), indent=4))"
