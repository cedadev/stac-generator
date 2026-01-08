# encoding: utf-8
"""
The mappings are run before an output and map the data into the
desired format.

You can configure more than one mapping per output. Mappings run
in the order they are given.

Mappings are loaded as named entry points with the namespace:
``stac_generator.mappings``

Example Configuration:
    .. code-block:: yaml

        mappings:
          - name: jinja2_mapping
            conf:
              template_directory: /path/to/template/directory
              template: template_name

"""
__author__ = "Rhys Evans"
__date__ = "26 Feb 2024"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "rhys.r.evans@stfc.ac.uk"
