
**********
Processors
**********

Processors take a uri and return a dictionary of extracted information. They
can be chained, one after the other and the results are merged such that arrays
are appended to and key:value pairs are overwritten by subsequent write operations.

Some processors can also take :ref:`pre-processors` and :ref:`post-processors`. Pre-processors modify
the input arguments whilst post-processors modify the output from the main processor.

.. _extraction-methods:

Extraction Methods
==================

.. list-table::
    :header-rows: 1

    * - Processor Name
      - Description
    * - :ref:`header <header-extract>`
      - Takes a uri string and a list of attributes and returns a dictionary of the values extracted from the file header.
    * - :ref:`regex <regex>`
      - Takes an input string and a regex with named capture groups and returns a dictionary of the values extracted using the named capture groups.
    * - :ref:`iso19115 <iso19115-extract>`
      - Extracts attributes from an formatted ISO19115 record at a given URL. Supports URL templating.
    * - :ref:`xml <xml-extract>`
      - Extracts attributes from an xml record at a given URL. Supports URL templating.
    * - :ref:`default <default-extract>`
      - Takes input dict of attributes and values to add generated object.
    * - :ref:`elasticsearch <elasticsearch-extract>`
      - Aggregates attributes for a given id from a elasticsearch endpoint.
    * - :ref:`json_file <json-file-extract>`
      - Aggregates attributes for a given id from a json file.
    * - :ref:`posix_stats <posix-stats-extract>`
      - Extracts file stats (name, size, mod_time, etc.).
    * - :ref:`object_store_stats <object-store-stats-extract>`
      - Extracts file stats (name, size, mod_time, etc.).

.. _header-extract:

Header
------

.. automodule:: stac_generator.plugins.extraction_methods.header_extract

.. autoclass:: stac_generator.plugins.extraction_methods.header_extract.HeaderExtract

.. _regex-extract:

Regex
-----

.. automodule:: stac_generator.plugins.extraction_methods.regex_extract
    :members:

.. _iso19115-extract:

ISO19115
--------

.. automodule:: stac_generator.plugins.extraction_methods.iso19115_extract
    :members:

.. _xml-extract:

XML
---

.. automodule:: stac_generator.plugins.extraction_methods.xml_extract
    :members:

.. _default-extract:

Default
-------

.. automodule:: stac_generator.plugins.extraction_methods.default_extract
    :members:

.. _elasticsearch-extract:

Elasticsearch
-------------

.. automodule:: stac_generator.plugins.extraction_methods.elasticsearch_extract
    :members:

.. _json-file-extract:

JSON File
---------

.. automodule:: stac_generator.plugins.extraction_methods.json_file_extract
    :members:

.. _posix-stats-extract:

POSIX Stats
-----------

.. automodule:: stac_generator.plugins.extraction_methods.posix_stats_extract
    :members:

.. _object-store-stats-extract:

Object Store Stats
------------------

.. automodule:: stac_generator.plugins.extraction_methods.object_store_stats_extract
    :members:

.. _pre-processors:

Pre Processors
==============

.. automodule:: stac_generator.plugins.preprocessors

.. list-table::
    :header-rows: 1

    * - Processor Name
      - Description
    * - :ref:`basename <basename-pre>`
      - Takes a file path and returns the filename using ``os.path.basename``.
    * - :ref:`ceda_observation <ceda-observation-pre>`
      - Takes a file path and returns the uuid from the `CEDA Catalogue <http://catalogue.ceda.ac.uk/>`_.

.. _basename-pre:

Basename
--------

.. automodule:: stac_generator.plugins.preprocessors.basename

.. _ceda-observation-pre:

CEDA Observation
----------------

.. automodule:: stac_generator.plugins.preprocessors.ceda_observation

.. _post-processors:

Post Processors
===============

.. list-table::
    :header-rows: 1

    * - Processor Name
      - Description
    * - :ref:`facet_map <facet-map-post>`
      - In some cases, you may wish to map the header attributes to different facets. This method takes a map and converts the facet labels into those specified.
    * - :ref:`isodate <iso-date-post>`
      - Takes the source dict and the key to access the date and converts the date to ISO 8601 Format.
    * - :ref:`date_combinator <date-combinator-post>`
      - Automatically converts year, month, day, hour, minunte, second keys into an ISO 8601 date.
    * - :ref:`bbox <bbox-post>`
      - Converts coordinates from a dictionary into `RFC 7946, section 5 <https://tools.ietf.org/html/rfc7946#section-5>`_
        formatted coordinates
    * - :ref:`geometry_point <geometry-point-post>`
      - Converts coordinates from a dictionary into `RFC 7946, section 3.1.2 <https://datatracker.ietf.org/doc/html/rfc7946#section-3.1.2>`_
        formatted coordinates
    * - :ref:`geometry_line <geometry-line-post>`
      - Converts coordinates from a dictionary into `RFC 7946, section 3.1.4 <https://datatracker.ietf.org/doc/html/rfc7946#section-3.1.4>`_
        formatted coordinates
    * - :ref:`geometry_polygon <geometry-polygon-post>`
      - Converts coordinates from a dictionary into `RFC 7946, section 3.1.6 <https://datatracker.ietf.org/doc/html/rfc7946#section-3.1.6>`_
        formatted coordinates
    * - :ref:`string_join <string-join-post>`
      - Join facets together to create a new value.
    * - :ref:`facet_prefix <facet-prefix-post>`
      - Add prefix to given atributes.

.. _facet-map-post:

Facet Map
---------

.. automodule:: stac_generator.plugins.postprocessors.facet_map

.. _iso-date-post:

ISO Date
--------
.. automodule:: stac_generator.plugins.postprocessors.isodate

.. _date-combinator-post:

Date Combinator
---------------

.. automodule:: stac_generator.plugins.postprocessors.date_combinator

.. _bbox-post:

BBOX
----
.. automodule:: stac_generator.plugins.postprocessors.bbox

.. _geometry-point-post:

Geometry Point
--------------
.. automodule:: stac_generator.plugins.postprocessors.geometry_point

.. _geometry-line-post:

Geometry Line
-------------
.. automodule:: stac_generator.plugins.postprocessors.geometry_line

.. _geometry-polygon-post:

Geometry Polygon
----------------
.. automodule:: stac_generator.plugins.postprocessors.geometry_polygon

.. _string-join-post:

String Join
-----------
.. automodule:: stac_generator.plugins.postprocessors.string_join

.. _date-combinator-post:

Facet Prefix
------------
.. automodule:: stac_generator.plugins.postprocessors.facet_prefix

.. _post-extraction-methods-post:

Post Extraction Methods
=======================

.. automodule:: stac_generator.plugins.post_extraction_methods

.. list-table::
    :header-rows: 1

    * - Processor Name
      - Description
    * - :ref:`controlled_vocabulary <controlled-vocab-post-extract>`
      - Compare properties to a controlled vocabulary defined by a ``pydantic.BaseModel``.
    * - :ref:`ceda_vocabulary <ceda-vocab-post-extract>`
      - Validates and sorts properties into vocabs and generates the ``general`` vocab for specified properties.

.. _controlled-vocab-post-extract:

Controlled Vocabulary
---------------------
.. automodule:: stac_generator.plugins.post_extraction_methods.controlled_vocabulary

.. _ceda-vocab-post-extract:

CEDA Vocabulary
---------------
.. automodule:: stac_generator.plugins.post_extraction_methods.ceda_vocabulary

.. _id-extraction-methods:

ID Extraction Methods
=====================

.. automodule:: stac_generator.plugins.id_extraction_methods

.. list-table::
    :header-rows: 1

    * - Processor Name
      - Description
    * - :ref:`default <default-id-extract>`
      - Sets the ID to the given value.
    * - :ref:`hash <hash-id-extract>`
      - Sets the ID to the hash of the given terms.

.. _default-id-extract:

Default
-------
.. automodule:: stac_generator.plugins.id_extraction_methods.default

.. _hash-id-extract:

Hash
----
.. automodule:: stac_generator.plugins.id_extraction_methods.hash

.. _third-party:

Third-Party Processors
======================

The plugin nature lends itself to third-party plugins. If you develop a plugin which might
be useful for others' workflows. Please make a pull request to add it to this table.

.. list-table::
    :header-rows: 1

    * - Processor Name
      - Description
      - Vendor
    * -
      -
      -