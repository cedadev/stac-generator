Orientation
===========

The :ref:`STAC Generator <index:stac generator>` is a framework for generating
STAC catalogs and is built to be modular and extensible. This can be confusing
for new users but this guide aims to act as an orientation to help new users
understand what this package can do and how the pieces fit together.

There are various pluggable pieces:
    - Inputs
    - Outputs
    - Extraction Methods
    - Pre/Post Processors
    - Post Extraction Methods
    - ID Extraction Methods

These pieces should allow you to construct a workflow which works for your use case and provide
python entry points to allow you to write your own plugins.
The STAC Generator package stores some :ref:`inputs <stac_generator/inputs:inputs>` which can be used to read from a range of different
sources messages of STAC objects to genertate.
The :ref:`asset <stac_generator/generators:asset>`, :ref:`item <stac_generator/generators:item>`, and :ref:`collection <stac_generator/generators:collection>`
generators take these messages and extract the required facets to buil the relevant STAC object using a variety of :ref:`processors <stac_generator/processors:processors>`.
These generated objects can then be passed to a range of :ref:`outputs <stac_generator/outputs:outputs>`.

The generators have two levels of configuration. Global configuration, passed at the command line on
invocation, which defines the inputs, ouputs, logging etc.

An example can be found :ref:`here <stac_generator/index:example config>`.

The second level of configuration comes in the form of collection-descriptions. These YAML files
describe the workflow for extracting facets and other metadata to build the assets, items, and collections of the STAC Catalog.
Background for collection-descriptions can be found `here <collection_descriptions/collection_descriptions:collection descriptions>`_
and a guide for how to build, and test these files is :ref:`here <collection_descriptions/building_a_workflow:building an collection description>`.

The different available processors which can construct these workflows are found :ref:`here <stac_generator/processors:processors>`.

The `CEDA repository containing these collection-descriptions <https://github.com/cedadev/collection-descriptions>`_ can
be used as an example. An example which includes extracting metadata from the NetCDF header is
`sentinel5 <https://github.com/cedadev/collection-descriptions/blob/master/descriptions/neodc/sentinel/sentinel5.yml>`_

.. code-block:: yaml

    paths:
      - /neodc/sentinel5p/data

    asset:
      extraction_methods:
        - method: regex
          description: Extract facets from the file path
          inputs:
            regex: '^\/(?:[^/]*/)(?P<platform>\w*)(?:[^/]*/){3}(?P<product_version>[0-9v.]+)/'
        - method: regex
          description: Extract facets from the filename
          inputs:
            regex: '^(?:[^_]*_){2}(?P<processing_level>[^_]+)__(?P<variable>[^_]+)_{4}(?P<start_datetime>[0-9T]+)_(?P<end_datetime>[0-9T]+)_(?P<orbit>\d+)(?:[^_]*_){3}(?P<datetime>[0-9T]+)'
          pre_processors:
            - method: filename_reducer
          post_processors:
            - method: isodate_processor
              inputs:
                date_keys:
                  - start_datetime
                  - end_datetime
                  - datetime
        - method: header
          description: Extract header metadata
          inputs:
            attributes:
              - institution
              - sensor

    item:
      id:
        method: hash
        inputs:
          terms:
            - platform
            - processing_level
            - variable
            - product_version
            - datetime
      extration_methods:
        - elasticsearch:
          default:
            - platform
            - processing_level
            - variable
            - product_version
            - datetime
          min:
            - start_datetime
          max:
            - end_datetime
          list:
            - orbit
            - institution
            - sensor

    collection:
        id:
          method: default
          inputs:
            value: Ic93XnsBhuk7QqVbSFwS
      extration_methods:
        - elasticsearch:
          default:
            - platform
            - processing_level
            - variable
            - product_version
            - datetime
          min:
            - start_datetime
          max:
            - end_datetime
          list:
            - orbit
            - institution
            - sensor

The “extraction_methods” are the workflow. In the example above I extract some facets from the file path,
some from the file name and some from the header.
To run regex on the filename, I use the ``filename_reducer`` and to convert my extracted dates to ISO 8601
format, I run the ``isodate_processor``.

As all of these “assets” are treated individually, but are grouped using the item id. So for the linked example, all assets
which return the same value for ``platform``, ``processing_level``, ``variable``, ``product_version`` and ``datetime``,
will be considered 1 STAC Item and be assigned the same ID.

The same can be said for items and the collection id.

This works in Elasticsearch because each individual elasticsearch document has the same id and are
merged in an upsert. If you are using another storage system, it will require an aggregation step
to join these together. Even with elasticsearch, lists are not merged in an upsert, but we have
not had to deal with this yet.
