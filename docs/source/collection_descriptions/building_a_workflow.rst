**********************************
Building an Collection Description
**********************************

Building an STAC catalog workflow consists of 4 mains steps:
    1. Write an :ref:`item_description <collection_descriptions/collection_descriptions:collection descriptions>` file to describe the workflow
    2. Test the workflow on a subset of data
    3. Index that subset of data to check it works as expected
    4. Index full dataset

Parts 1 and 2 will likely go round in a loop, whilst you are developing the
workflow file, with several iterations until you are happy.

1. Write a collection-description
=================================

A basic collection-description consists of 5 sections:
    1. ``paths``
    2. ``collection``
    3. ``item``
    4. ``asset``

An example collection-description can be found :ref:`here <collection_descriptions/collection_descriptions:example description file>`

The extraction methods section describes how the facets are extracted from the data.

Assets are aggregated into items based on the item ID

.. warning::

    All assets you want to end up together, should have the same item ID.
    If you generate your item ID from the filename, and not all assets you want to group
    together have the same filename convention (e.g. metadata files) then they will end up independent.

To check your collection-description works as expected, you will need to run it.

2. Running the collection-description on a subset of data
=========================================================

To run your workflow, you will need to create a config file.
This will define an input path and output to standard out.

Example configuration
---------------------

.. include:: ../stac_generator/user_guide/example_config.rst

You should choose a filepath with a relatively small number of files to
make iteration quick and allow you to make tweaks.

You can then run your workflow using:

``stac_generator <path_to_config_file>``

.. program-output:: stac_generator -h

.. note::

    It is likely that this will be an iterative process to make sure that the correct
    assets end up together and that all the facets are extracted as desired.

3. Indexing the data
====================

.. caution::

    Have you indexed the assets? Things may not work fully if the assets have
    not been indexed as well.

This step is as simple as changing your output plugin to point to the final destination.

Here is an example for the elasticsearch output making use of additional kwargs:

.. code-block::

      - method: elasticsearch
        connection_kwargs:
          hosts: [host1]
          headers:
            x-api-key: <api_key>
          use_ssl: true
          verify_certs: false
          ssl_show_warn: false
        index:
            name: ceda-items-2021-06-09
      - method: elasticsearch
        connection_kwargs:
          hosts: [host1]
          headers:
            x-api-key: <api_key>
          use_ssl: true
          verify_certs: false
          ssl_show_warn: false
        index:
            name: ceda-assets-2021-06-09

Once this works as expected...

4. Indexing the full dataset
============================

This is done by increasing the scope of the input plugin.
In the example we used the path ``/badc/faam/data/2005/b069-jan-05``. If our
description file covered ``/badc/faam/data`` we could now expand our input to cover
``/badc/faam/data``.

.. note::

    The higher up the tree you put the input, the longer it will take. You might
    wish to consider splitting the run into smaller segments and running in parallel.
