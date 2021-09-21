# encoding: utf-8
"""
The output plugins determine what happens at the end of the
extraction process.

You can configure more than one active plugin, if you wanted
to output the content to more than one place.

Output plugins are loaded as named entry points with the namespace:
``asset_scanner.output_plugins``
"""
__author__ = 'Richard Smith'
__date__ = '08 Jun 2021'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'