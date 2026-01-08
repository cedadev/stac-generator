
# Recipes


Recipes describe how metadata should be extracted and manipulated for an event.

## Recipe sections

The description file consists of 3 top level keys:

A [Full JSON Schema](#schema) references below.

| Key                | Type                                                | Description                                          |
| ------------------ | --------------------------------------------------- | ---------------------------------------------------- |
| paths              | list[str]                                           | Paths the recipe applies to.                         |
| type               | str                                                 | The type of generator. Can be used to group recipes. |
| extraction_methods | list[[Extraction Methods](#extraction-methods)]  | The extraction methods to generate the metadata.     |


## Paths

Defines the set of paths which the recipe is applicable to.
When multiple recipes match a record the most specific will be chosen.

``` yaml
paths:
  - /badc/faam/data
```

## Type

Defines the type of record that will be produced. This allow recipes to be grouped.

``` yaml
type: item
```

## Extraction Methods

Defines a list of extraction methods used to generate the record's metadata.

``` yaml
extraction_methods:
  - method: lambda
    inputs:
      function: 'lambda uri: uri.replace("/badc/cmip6/data", "").strip("/").replace("/", ".")'
      args:
        - $uri
      output_key: instance_id
```

## Schema

.. program-output:: python -c "from stac_generator.core.baker import Recipe; import json; print(json.dumps(Recipe.schema(), indent=4))"
