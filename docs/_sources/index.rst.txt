.. asset_scanner documentation master file, created by
   sphinx-quickstart on Tue Jun  8 15:30:14 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Asset Scanner
===============

The asset scanner provides base functionality and a script to run various different
scanners which operate at a file level. These extractors run on each file and return
content based on the configuration file.

Current implementations of the Extractor are:
   - `Asset Extractor <https://github.com/cedadev/asset-extractor>`_
   - `Facet Extractor <https://github.com/cedadev/item-generator>`_

Both of these implementation make use of :ref:`item description <item-descriptions>` files

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   usage
   item_descriptions
   input_plugins
   output_plugins


.. toctree::
   :maxdepth: 2
   :caption: API:

   extractor



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
