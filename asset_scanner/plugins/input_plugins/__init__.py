# encoding: utf-8
"""
The input plugins determine the source of the list. Files are processed
atomically and the input plugins provide this atomic action.

You can configure more than one input plugin, if you wanted
to input the content from more than one place.

Input plugins are loaded as named entry points with the namespace:
``asset_scanner.input_plugins``

.. warning::
    Blocking input plugins will prevent others from being run. They are run
    sequentially. For example, with the `file system input`_ plugin, you could configure
    several to scan multiple directories but the rabbit plugin creates a listening connection
    which would block any other inputs.
"""
__author__ = 'Richard Smith'
__date__ = '08 Jun 2021'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'