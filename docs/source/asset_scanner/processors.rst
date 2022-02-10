
******************
Processors
******************

Processors take a file and return a dictionary of extracted information. They
can be chained, one after the other and the results are merged such that arrays
are appended to and key:value pairs are overwritten by subsequent write operations.

Some processors can also take :ref:`pre-processors` and :ref:`post-processors`. Pre-processors modify
the input arguments whilst post-processors modify the output from the main processor.

Core Processors
================

.. list-table::
    :header-rows: 1

    * - Processor Name
      - Description
    * - :ref:`header_extract <header-extract>`
      - Takes a filepath string and a list of attributes and returns a dictionary of the values extracted from the file header.
    * - :ref:`regex <regex>`
      - Takes an input string and a regex with named capture groups and returns a dictionary of the values extracted using the named capture groups.
    * - :ref:`iso19115 <iso19115-extract>`
      - Extracts attributes from an xml formatted ISO19115 record at a given URL. Supports URL templating.
    * - :ref:`xml_extract <xml-extract>`
      - Extracts attributes from an xml formatted ISO19115 record at a given URL. Supports URL templating.


.. automodule:: asset_scanner.plugins.extraction_methods.header_extract

.. autoclass:: asset_scanner.plugins.extraction_methods.header_extract.HeaderExtract

.. automodule:: asset_scanner.plugins.extraction_methods.regex_extract
    :members:

.. automodule:: asset_scanner.plugins.extraction_methods.iso19115_extract
    :members:

.. automodule:: asset_scanner.plugins.extraction_methods.xml_extract
    :members:

Third-Party Processors
-----------------------

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

.. _pre-processors:

Pre Processors
==============

.. automodule:: asset_scanner.plugins.extraction_methods.preprocessors

.. list-table::
    :header-rows: 1

    * - Processor Name
      - Description
    * - :ref:`filename_reducer <filename-reducer>`
      - Takes a file path and returns the filename using ``os.path.basename``.
    * - :ref:`ceda_observation <ceda-observation>`
      - Takes a file path and returns the uuid from the `CEDA Catalogue <http://catalogue.ceda.ac.uk/>`_.

.. _filename-reducer:

Filename Reducer
----------------

.. autoclass:: asset_scanner.plugins.extraction_methods.preprocessors.ReducePathtoName

.. _ceda-observation:

CEDA Observation
----------------

.. autoclass:: asset_scanner.plugins.extraction_methods.preprocessors.CEDAObservation


Third-Party Pre-processors
---------------------------

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


.. _post-processors:

Post Processors
===============

.. automodule:: asset_scanner.plugins.extraction_methods.postprocessors

.. list-table::
    :header-rows: 1

    * - Processor Name
      - Description
    * - :ref:`facet_map <asset_scanner/processors:facet map processor>`
      - In some cases, you may wish to map the header attributes to different facets. This method takes a map and converts the facet labels into those specified.
    * - :ref:`isodate_processor <asset_scanner/processors:iso date processor>`
      - Takes the source dict and the key to access the date and converts the date to ISO 8601 Format.
    * - :ref:`date_combinator <asset_scanner/processors:date combinator processor>`
      - Automatically converts year, month, day, hour, minunte, second keys into an ISO 8601 date.
    * - :ref:`stac_bbox <asset_scanner/processors:stac bbox processor>`
      - Converts coordinates from a dictionary into `RFC 7946, section 5 <https://tools.ietf.org/html/rfc7946#section-5>`_
        formatted coordinates
    * - :ref:`string_join <asset_scanner/processors:string join processor>`
      - Join facets together to create a new value.

Facet Map Processor
-------------------

.. autoclass:: asset_scanner.plugins.extraction_methods.postprocessors.FacetMapProcessor

ISO Date Processor
-------------------
.. autoclass:: asset_scanner.plugins.extraction_methods.postprocessors.ISODateProcessor

Date Combinator Processor
--------------------------

.. autoclass:: asset_scanner.plugins.extraction_methods.postprocessors.DateCombinatorProcessor

STAC BBOX Processor
-------------------
.. autoclass:: asset_scanner.plugins.extraction_methods.postprocessors.BBOXProcessor

String Join Processor
---------------------
.. autoclass:: asset_scanner.plugins.extraction_methods.postprocessors.StringJoinProcessor

Facet Prefix Processor
-------------------
.. autoclass:: asset_scanner.plugins.extraction_methods.postprocessors.FacetPrefixProcessor


Third-Party Post-processors
---------------------------

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
