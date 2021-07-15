# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '15 Jul 2021'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from asset_scanner.core import utils


def test_dot2dict_single():
    """
    Check that dot2dict can generate dicts from a single key
    """
    value = 'test_value'
    key = 'single_key'
    expected = {key: value}

    output = utils.dot2dict(key, value)

    assert output == expected


def test_dot2dict_nested():
    """
    Check that dot2dict can generate dicts from a single key
    """
    value = 'test_value'
    key = 'single_key.nested'
    expected = {'single_key': {'nested': value}}

    output = utils.dot2dict(key, value)

    assert output == expected
