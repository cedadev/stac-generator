# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '23 Sep 2021'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

import pytest
import sys

from asset_scanner.plugins.input_plugins.intake_esm_input import IntakeESMInputPlugin


@pytest.fixture
def intake_input():
    return IntakeESMInputPlugin(
        uri='https://raw.githubusercontent.com/cedadev/cmip6-object-store/master/catalogs/ceda-zarr-cmip6.json',
        search_kwargs=dict(source_id="UKESM1-0-LL",
                           experiment_id=["historical", "ssp585-bgc"],
                           member_id=["r4i1p1f2", "r12i1p1f2"],
                           table_id="Amon",
                           variable_id="tas"),
        object_path_attr='zarr_path'
    )


@pytest.mark.skipif(sys.version_info < (3,7),
                    reason="requires python3.7")
def test_open_remote_catalog(intake_input):
    catalog = intake_input.open_catalog()
    assert len(catalog.df) == 3

