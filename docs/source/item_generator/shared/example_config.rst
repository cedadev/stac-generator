   .. code-block:: yaml

      item_descriptions:
        root_directory: /etc/item-generator/item_descriptions/descriptions
      inputs:
        - method: file_system
          path: /badc/faam/data/2005/b069-jan-05
      outputs:
        - method: standard_out
          namespace: assets
        - method: standard_out
          namespace: facets
