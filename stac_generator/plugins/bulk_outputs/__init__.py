# encoding: utf-8
"""
The outputs determine what happens at the end of the
extraction process.

Bulk outputs store collect a configured number of message
before outputting and output any remaining message after
the input has finished.

You can configure more than one active plugin, if you wanted
to output the content to more than one place.

Bulk Outputs are loaded with standard outputs as named entry points with the namespace:
``stac_generator.outputs``

Example Configuration:
    .. code-block:: yaml

        outputs:
            - name: elasticsearch_bulk
              conf:
                client_kwargs:
                  hosts: ['host1','host2']
                  index:
                    name: 'assets-2021-06-02'
"""
__author__ = "Richard Smith"
__date__ = "08 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"
