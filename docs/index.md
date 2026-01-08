# STAC Generator

The STAC Generator provides a framework that leverages a modular, plugin architecture
to allow users to configure a workflow to generate, extract, and manipulate metadata to
fit their requirement's needs.

The framework was constructed to extract metadata for STAC catalogs but could be used to extract
metadata for any number of systems.

## How the Generator works?

[Input plugins](inputs.md) can be configured to produce a series of "events".
For each event the relevant [recipe](recipes.md) is found and it's [extraction methods](recipes.md#extraction-methods)
are ran to produce a metadata record. This record can then be mapped to a desired format, 
such as STAC, using [mapping plugins](mappings.md) and then output to one or more [output plugins](outputs.md).

## How to configure the Generator?

Generator configutation is spread across two levels. The main configuration defines which Inputs are to be run, if the data needs to be mapped, where the 
generated data should be output to, and the location of the other configuration. The second level of configuration, known as recipes, define which extraction methods
should be run for each event. Having this second level allows different extraction methods to be run on different events to produce more specific metadata.

## What is STAC?

The SpatioTemporal Asset Catalog ([STAC](https://stacspec.org/)) specification provides a common language to
describe a range of geospatial information, so it can more easily be indexed and discovered.
A "spatiotemporal asset" is any file that represents information about the earth captured
in a certain space and time.
