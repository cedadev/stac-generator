Usage
=======

There is a console script defined by this package which can be used to run the
extractors ``asset_extractor``.

.. program-output:: asset_scanner -h

The configuration file feeds this top level scrip and configures the input/output
plugins as well as the extractor class. You will need to see you extractor documentation
to get the configurable arguments.

For the base implementation see:
    - `Asset Extractor <https://github.com/cedadev/asset-extractor>`_ - Extracts file level metadata
    - `Facet Extractor <https://github.com/cedadev/item-generator>`_ - Extracts facets using processors

Required configuration options:
    - ``inputs`` - :ref:`input-plugins`
    - ``outputs`` - :ref:`output-plugins`

The extractor can be specified in the configration file or can be loaded from
an entry point. The configuration value take precedence over entry points.

.. warning::
    Only the first extractor will be loaded from entry points.
