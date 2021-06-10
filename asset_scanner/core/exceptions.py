# encoding: utf-8
"""
Exceptions
----------

"""
__author__ = 'Richard Smith'
__date__ = '02 Jun 2021'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'


class NoPluginsError(Exception):
    """
    Raised when no plugins have been loaded for a particular section.
    i.e. if no input plugins were successfully loaded, then this exception
    would be raised.
    """
    pass