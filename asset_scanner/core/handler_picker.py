# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '01 Jun 2021'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

import pkg_resources
from .processor import BaseProcessor

from typing import Optional


class HandlerPicker:
    def __init__(self, entry_point_key: str):
        """
        Entry points to load from in the setup.py

        :param entry_point_key: name of the entry point source
        """
        self.handlers = {}

        if not entry_point_key:
            raise ValueError('No entry point specified. No handlers will be loaded')

        for entry_point in pkg_resources.iter_entry_points(entry_point_key):
            # print(vars(entry_point))
            # e_point = entry_point.load()
            self.handlers[entry_point.name] = entry_point

            # Only load entry points which inherit from the base class

    def get_processor(self, name: str, **kwargs) -> Optional[BaseProcessor]:
        """
        Get the processor by name

        :param name: The name of the requested processor

        :return: Processor class
        """

        # Get the processor
        entry_point = self.handlers.get(name)

        if not entry_point:
            LOGGER.error(f'Failed to load processor: {name}')
            return

        # Try to load the processor
        processor = entry_point.load()

        return processor(**kwargs)
