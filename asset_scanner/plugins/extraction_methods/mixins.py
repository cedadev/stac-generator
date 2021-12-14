# encoding: utf-8
"""

"""
__author__ = "Richard Smith"
__date__ = "15 Jul 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


class PropertiesOutputKeyMixin:
    """
    Adds an output key attribute to the processor.
    Dot separated strings can be used to created nested attributes.

    Defaults to 'properties'
    """

    def __init__(self, **kwargs):

        if kwargs.get("output_key") is None:
            kwargs["output_key"] = "properties"

        super().__init__(**kwargs)
