# encoding: utf-8
"""

"""
__author__ = "Richard Smith"
__date__ = "01 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

from pydantic import BaseModel


class SetConfig():
    config_class: BaseModel | None = None

    def __init__(self, **kwargs):
        """
        Set the objects config

        :param kwargs:
        """
        if self.config_class:
            self.conf = self.config_class(**kwargs["conf"])
