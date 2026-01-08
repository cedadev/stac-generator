# Generator Configuration

Generators consit of 4 components:

| Key         | Type                                        | Description                        |
| ----------- | ------------------------------------------- | ---------------------------------- |
| generator   | str                                         | Type of generator to be run.       |
| recipe_root | str                                         | The root directory of the recipes. |
| inputs      | list[[Inputs](inputs.md)]                   | Inputs to collect initial data.    |
| outputs     | list[[Outputs \| Bulk Outputs](outputs.md)] | Ouputs to post produced data to.   |

Example:
``` yaml
generator: item

recipes_root: recipes/

inputs:
  - name: text_file
    conf:
      filepath: input/assets.txt

outputs:
  - name: standard_out
    mappings:
      - name: stac
        stac_version: '1.0.0'
        stac_extensions: []
```