# encoding: utf-8
"""
The input plugins generate a stream of dictionaries to be passed to the generator for processing.

You can configure more than one input plugin, if you wanted
to input the content from more than one place.

Inputs are loaded as named entry points with the namespace:
``stac_generator.inputs``

.. warning::
    Blocking input plugins will prevent others from being run. They are run
    sequentially. For example, with the :ref:`file system input plugin <stac_generator/inputs:File System Input>`, you
    could configure several to scan multiple directories but the rabbit plugin
    creates a listening connection which would block any other inputs.
"""
__author__ = "Richard Smith"
__date__ = "08 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"
