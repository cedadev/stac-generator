**************
STAC Generator
**************

:fa:`github` `View on Github <https://github.com/cedadev/stac-generator>`_

The STAC Generator provides a framework that leverages a modular, plugin architecture
to allow users to configure a workflow to generate, extract, and manipulate metadata to
fit their requirements needs.

`Input plugins <stac_generator/inputs>`_ can be configured to produce a series of "events".
For each event the relevant `recipe <recipes/recipes>`_ is found and it's `extraction methods <stac_generator/recipes>`_
are ran against the event, producing the associated metadata. This metadata can then be
mapped to a desired format, such as STAC, with `mapping plugins <stac_generator/mappings>`_
and then output to one or more `output plugins <stac_generator/outputs>`_.

.. image:: images/stac_generator_diagram.png

The framework was constructed to extract metadata for creating STAC catalogs
but could be used to extract metadata for any number of systems.

What is STAC?
==============

The SpatioTemporal Asset Catalog (`STAC <https://stacspec.org/>`_) specification provides a common language to
describe a range of geospatial information, so it can more easily be indexed and discovered.
A "spatiotemporal asset" is any file that represents information about the earth captured
in a certain space and time.

.. toctree::
   :maxdepth: 3
   :caption: Contents:

   stac_generator/index
   recipes/recipes
   stac_generator/user_guide/orientation

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
