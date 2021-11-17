
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

    datasets:
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

Datasets
--------

Describes the paths where this file applies. Can be multiple locations.
The path references all points below it in the hierarchy.

.. code-block:: yaml

    datasets:
        - /badc/faam/data

Defaults
--------

Default facet values to apply for all files in the absence of any other information.

.. code-block:: yaml

    defaults:
        facet1: value

Mappings
---------

Allows you to map one term to another. This can be used to map multi-values or
correct values where they are known to be incorrect.

.. code-block:: yaml

    mappings:
        facet1:
          term1: value1
          term2: value2

Overrides
---------

No matter what comes from the file, this is the value to be used

.. code-block:: yaml

    overrides:
        facet1: term1


Facets
-------

This section describes how the facets are extracted and has a few nested sections

.. code-block:: yaml

    facets:
        extraction_methods:
          - name: string_regex
            inputs:
              regex: '^\/(?:[^/]*/)(?P<project>\w*)\/(?:[^/]*/){2}(?P<flight_number>[\w\d]*).*\/(?:[^_]*_){2}(?P<date>\d*)'
        aggregation_facets:
          - project
          - flight_number


Extraction Methods
~~~~~~~~~~~~~~~~~~~

A list of functions to run, and their arguments. A full list of functions and their
expected parameters can be found `here <https://cedadev.github.io/item-generator/processors.html>`_.

Extraction methods can use the ``description`` key to allow you to write notes to your future self
about what the extractor is for. This is not used in running the code.

Aggregation Facets
~~~~~~~~~~~~~~~~~~

Facets to be used when creating an ID and aggregating files into STAC items.
The item ID is generated using a hash of the specified aggregation facets.
It is then down to the upstream application to aggregate and handle merging
these objects.

Categories
~~~~~~~~~~

Used by the asset extractor to assign categories to files.
By default, all files are given the category data.

.. code-block:: yaml

    categories:
        label: metadata
        regex: 00README


Schema
=======

.. program-output:: python -c "from asset_scanner.core.item_describer import ItemDescription; import json; print(json.dumps(ItemDescription.schema(), indent=4))"