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

1. Install the generator

    .. code-block::

        pip install -r .

2. Generate items by running the `stac-generator`_

    .. code-block::

        stac_generator -c conf/item-generator.yaml

3. Generate collections by running the `stac-generator`_

    .. code-block::

        stac_generator -c conf/collection-generator.yaml

Inputs Explained
================

The yaml files in conf setup the input and outputs for the script. In this case, the input is an intake-esm catalog and the output is the terminal, json file, and a text file. The text file is then used for collection generation.

.. code-block:: yaml
    # The type of generator to be run
    generator: item

    # The root directory of the recipes
    recipes_root: recipes/

    # The input plugins to be run for the generator
    inputs:
      - name: text_file
        filepath: input/assets.txt

    # The output plugins to be run for the generator
    outputs:
      - name: standard_out
    # Output plugins can use mappings to reshape the output
        mappings:
          - name: stac
            stac_version: '1.0.0'
            stac_extensions: []
      - name: json_file
        dirpath: output/items
        filename_term: id
        mappings:
          - name: stac
            stac_version: '1.0.0'
            stac_extensions: []
      - name: text_file
        filepath: input/collections.txt

The recipes in example/recipes, describes the steps needed to extract and manipulate the metadata.

.. code-block:: yaml

    # The paths that the recipe will be run on
    paths:
      - https://cmip6-zarr-o.s3-ext.jc.rl.ac.uk/CMIP6.CMIP.MOHC.UKESM1-0-LL
      - https://cmip6-zarr-o.s3-ext.jc.rl.ac.uk/CMIP6.C4MIP.MOHC.UKESM1-0-LL

    # The type of STAC record that will be generated
    type: item

    # These extraction methods will be run after `extraction_methods` and should generate the id of the record
    id:
      - method: default
        inputs:
          defaults:
            item_id: $instance_id

    # The extaction methods are run in series with the output dictionary is passed from one to the next
    # extaction methods add, update or remove the data from the output dictionary
    extraction_methods:
      - method: regex
        inputs:
          regex: '\/(?P<mip_era>\w*)\.(?P<activity_id>\w*)\.(?P<institution_id>[\w-]*)\.(?P<source_id>[\w-]*)\/(?P<experiment_id>[\w-]*)\.(?P<member_id>\w*)\.(?P<table_id>\w*)\.(?P<var_id>\w*)\.(?P<grid_label>\w*)\.(?P<version>\w*)'

      - method: string_template
        inputs:
          template: '{mip_era}.{activity_id}.{institution_id}.{source_id}.{table_id}.{var_id}.{version}'
          output_key: instance_id

    # Some extraction methods generate assets which can also include their own list of extration methods to be run on the assets
      - method: intake_assets
        inputs:
          uri: https://raw.githubusercontent.com/cedadev/cmip6-object-store/master/catalogs/ceda-zarr-cmip6.json
          object_path_attr: zarr_path
          search_kwargs:
            mip_era: $mip_era
            activity_id: $activity_id
            institution_id: $institution_id
            source_id: $source_id
            table_id: $table_id
            variable_id: $var_id
            version: $version
          extraction_methods:
            - method: default
              inputs:
                defaults:
                  roles: ["data"]

      - method: lambda
        inputs:
          function: 'lambda assets: {f"data{str(en+1).zfill(4)}": assets[key] for en, key in enumerate(sorted(assets))}'
          input_args:
            - $assets
          output_key: assets

      - method: remove
        inputs:
          keys:
            - uri

    # member of defines the other recipes that define a parent of this record
    member_of:
      - recipes/collection/CMIP6.CMIP.MOHC.UKESM1-0-LL.yaml


Outputs Explained
=================

STAC Generation
---------------

The output of the extraction methods is a dictionary of the metadata:

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

The mappings can be used to re-arange the output into a desired framework. For example using the STAC mapping:

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
