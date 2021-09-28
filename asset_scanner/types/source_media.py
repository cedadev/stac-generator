# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '23 Sep 2021'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

import enum


class StorageType(enum.Enum):
    """Enum values for storage classes"""
    POSIX = 'POSIX'
    OBJECT_STORE = 'OBJECT_STORE'
    TAPE = 'TAPE'