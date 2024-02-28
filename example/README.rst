**********************
STAC Generator Example
**********************

This is a basic example to provide a working introduction to the `stac-generator`_ framework.
It uses an intake catalog to provide URLs to public data in an S3 Object Store. These are
then turned into a STAC Catalog of Items and Collections.

Getting Started
================

You can either run locally or launch in Binder:
 
Running in Binder
-----------------

Click 

.. image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/cedadev/stac-generator/example/HEAD

To just run it and see the example output, open ``example_notebook.ipynb``.


Local deployment
-----------------

1. Install the requirements

    .. code-block::

        pip install -r requirements.txt

2. Generate items by running the `stac-generator`_

    .. code-block::

        stac_generator -c example/conf/item-generator.yaml

3. Generate collections by running the `stac-generator`_

    .. code-block::

        stac_generator -c example/conf/collection-generator.yaml

Inputs Explained
================

The yaml files in conf setup the input and outputs for the script. In this case, the input is an intake-esm catalog and the output is the terminal.

The file in collection-descriptions, describes the workflow to extract the facets.

.. code-block:: yaml

    paths:
  - https://cmip6-zarr-o.s3-ext.jc.rl.ac.uk/CMIP6.CMIP.MOHC.UKESM1-0-LL

    asset:
    # The default asset id is a hash of the assets uri
    extraction_methods:
        # - method: posix_stats
        - method: regex
        inputs:
            regex: 'https://cmip6-zarr-o.s3-ext.jc.rl.ac.uk\/(?P<mip_era>\w+)\.(?P<activity_id>\w+)\.(?P<institution_id>[\w-]+)\.(?P<source_id>[\w-]+)\/(?P<experiment_id>[\w-]+)\.(?P<member_id>\w+)\.(?P<table_id>\w+)\.(?P<var_id>\w+)\.(?P<grid_label>\w+)\.(?P<version>\w+)'

    item:
    # The default item id is a hash of the collection id
    id:
        method: hash
        inputs:
        terms:
            - mip_era
            - activity_id
            - institution_id
            - source_id
            - table_id
            - var_id
            - version
    extraction_methods:
        - method: json_file
        inputs:
            filepath: tests/file-io/assets.json
            terms:
            - mip_era
            - activity_id
            - institution_id
            - source_id
            - table_id
            - var_id
            - version

    collection:
    # The default collection id is "undefined"
    id:
        method: default
        inputs:
        value: cmip6
    extraction_methods:
        - method: json_file
        inputs:
            filepath: tests/file-io/items.json
            terms:
            - mip_era
            - activity_id
            - institution_id
            - source_id
            - table_id
            - var_id
            - version


Outputs Explained
=================

STAC Generation
---------------

The stac-genetator outputs:

.. code-block:: python

    {
        'activity_id': 'C4MIP',
        'assets': {
            'data0001': {
                'href': 'https://cmip6-zarr-o.s3-ext.jc.rl.ac.uk/CMIP6.CMIP.MOHC.UKESM1-0-LL/historical.r2i1p1f2.Amon.tas.gn.v20190502.zarr',
                'roles': ['data']
            },
            'data0002': {
                'href': 'https://cmip6-zarr-o.s3-ext.jc.rl.ac.uk/CMIP6.CMIP.MOHC.UKESM1-0-LL/historical.r3i1p1f2.Amon.tas.gn.v20190502.zarr',
                'roles': ['data']
            },
            'data0003': {
                'href': 'https://cmip6-zarr-o.s3-ext.jc.rl.ac.uk/CMIP6.CMIP.MOHC.UKESM1-0-LL/historical.r4i1p1f2.Amon.tas.gn.v20190502.zarr',
                'roles': ['data']
            },
            'data0004': {
               'href': 'https://cmip6-zarr-o.s3-ext.jc.rl.ac.uk/CMIP6.CMIP.MOHC.UKESM1-0-LL/historical.r8i1p1f2.Amon.tas.gn.v20190502.zarr',
                'roles': ['data']
            }
        },
        'collection_id': ['cmip6'],
        'experiment_id': 'ssp585-bgc',
        'grid_label': 'gn',
        'instance_id': 'CMIP6.C4MIP.MOHC.UKESM1-0-LL.Amon.tas.v20190806',
        'institution_id': 'MOHC',
        'item_id': 'CMIP6.C4MIP.MOHC.UKESM1-0-LL.Amon.tas.v20190806',
        'member_id': 'r4i1p1f2',
        'member_of_recipes': {'cmip6': '338fbab3bb532d3f071ab068ba71283c'},
        'mip_era': 'CMIP6',
        'source_id': 'UKESM1-0-LL',
        'table_id': 'Amon',
        'var_id': 'tas',
        'version': 'v20190806'
    }

Mappings
--------

The mappings can be used to re-arange the output to the desired framework. For example the STAC mapping:

.. code-block:: python

    {
        "type": "Feature",
        "stac_version": "1.0.0",
        "stac_extensions": [],
        "id": "CMIP6.C4MIP.MOHC.UKESM1-0-LL.Amon.tas.v20190806",
        "geometry": null,
        "assets": {
            "data0001": {
                "href": "https://cmip6-zarr-o.s3-ext.jc.rl.ac.uk/CMIP6.CMIP.MOHC.UKESM1-0-LL/historical.r2i1p1f2.Amon.tas.gn.v20190502.zarr",
                "roles": [
                    "data"
                ]
            },
            "data0002": {
                "href": "https://cmip6-zarr-o.s3-ext.jc.rl.ac.uk/CMIP6.CMIP.MOHC.UKESM1-0-LL/historical.r3i1p1f2.Amon.tas.gn.v20190502.zarr",
                "roles": [
                    "data"
                ]
            },
            "data0003": {
                "href": "https://cmip6-zarr-o.s3-ext.jc.rl.ac.uk/CMIP6.CMIP.MOHC.UKESM1-0-LL/historical.r4i1p1f2.Amon.tas.gn.v20190502.zarr",
                "roles": [
                    "data"
                ]
            },
            "data0004": {
                "href": "https://cmip6-zarr-o.s3-ext.jc.rl.ac.uk/CMIP6.CMIP.MOHC.UKESM1-0-LL/historical.r8i1p1f2.Amon.tas.gn.v20190502.zarr",
                "roles": [
                    "data"
                ]
            }
        },
        "properties": {
            "datetime": null,
            "mip_era": "CMIP6",
            "activity_id": "C4MIP",
            "institution_id": "MOHC",
            "source_id": "UKESM1-0-LL",
            "experiment_id": "ssp585-bgc",
            "member_id": "r4i1p1f2",
            "table_id": "Amon",
            "var_id": "tas",
            "grid_label": "gn",
            "version": "v20190806",
            "instance_id": "CMIP6.C4MIP.MOHC.UKESM1-0-LL.Amon.tas.v20190806"
        },
        "collection": "cmip6"
    }

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _`stac-generator`: https://cedadev.github.io/stac-generator/
