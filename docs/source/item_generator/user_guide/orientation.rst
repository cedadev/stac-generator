Orientation
===========

The Item Generator is part of a framework defined by the :ref:`Asset Scanner <index:asset scanner>`
and is build to be modular and extensible. This can be confusing for new users
but this guide aims to act as an orientation to help new users understand what
this package can do and how the pieces fit together.

There are various pluggable pieces:
    - Input plugins
    - Output plugins
    - Processors
    - Pre/Post processors

These pieces should allow you to construct a workflow which works for your use case and provide
python entry points to allow you to write your own plugins.
The Asset Scanner package stores some common :ref:`input <asset_scanner/input_plugins:input plugins>`
and :ref:`output plugins <asset_scanner/output_plugins:output plugins>` (PRs welcome).
This package, Item Generator, contains some processors which are used to extract attributes from files and
passes them to the output plugin. You can read more about the processors, and how pre/post processors work
:ref:`here <item_generator/processors/processors:processors>`.

The item generator has two levels of configuration. Global configuration, passed at the command line on
invocation, which defines the input and ouput plugins and things like logging configuration.

An example can be found :ref:`here <item_generator/index:sample configuration>`.

The second level of configuration comes in the form of item-descriptions. These YAML files
describe the workflow for extracting facets and other metadata to build the STAC Item.
Background for item-descriptions can be found `here <item_descriptions/item_descriptions:item descriptions>`_
and a guide for how to build, and test these files is :ref:`here <item_descriptions/building_a_workflow:building an item description>`.

The different available processors which can construct these workflows are found :ref:`here <item_generator/processors/processors:processors>`.

The `CEDA repository containing these item-descriptions <https://github.com/cedadev/item-descriptions>`_ can
be used as an example. An example which includes extracting metadata from the NetCDF header is
`sentinel5 <https://github.com/cedadev/item-descriptions/blob/master/descriptions/neodc/sentinel/sentinel5.yml>`_

.. code-block:: yaml

    datasets:
        - /neodc/sentinel5p/data
    collection:
        id: Ic93XnsBhuk7QqVbSFwS
    facets:
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
            - method: header_extract
              description: Extract header metadata
              inputs:
               attributes:
                 - institution
                 - sensor
        aggregation_facets:
            - platform
            - processing_level
            - variable
            - product_version
            - datetime

The “extraction_methods” are the workflow. In the example above I extract some facets from the file path,
some from the file name and some from the header.
To run regex on the filename, I use the ``filename_reducer`` and to convert my extracted dates to ISO 8601
format, I run the ``isodate_processor``.

As all of these “assets” are treated individually, we need a way to make sure they end up together.
The aggregation facets are used to generate a STAC item ID. So for the linked example, all assets
which return the same value for ``platform``, ``processing_level``, ``variable``, ``product_version`` and ``datetime``,
will be considered 1 STAC Item and be assigned the same ID.

This works in Elasticsearch because each individual elasticsearch document has the same id and are
merged in an upsert. If you are using another storage system, it will require an aggregation step
to join these together. Even with elasticsearch, lists are not merged in an upsert, but we have
not had to deal with this yet.
