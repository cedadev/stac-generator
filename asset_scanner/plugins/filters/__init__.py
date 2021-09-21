# encoding: utf-8
"""

In some cases, it might be useful to be able to filter the response from the
plugins. E.g ignoring certain paths.

If more than one filter is specified, all tests must pass before processing will
continue.

Plugin filters are loaded as named entry points with the namespace:
``asset_scanner.plugin_filters``
"""
__author__ = 'Richard Smith'
__date__ = '20 Sep 2021'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'