# Asset Scanner

[![Test](https://github.com/cedadev/asset-scanner/actions/workflows/tests.yml/badge.svg)](https://github.com/cedadev/asset-scanner/actions/workflows/tests.yml)
[![Docs](https://github.com/cedadev/asset-scanner/actions/workflows/docs_build.yml/badge.svg)](https://github.com/cedadev/asset-scanner/actions/workflows/docs_build.yml)
[![Upload Python Package](https://github.com/cedadev/asset-scanner/actions/workflows/release.yml/badge.svg)](https://pypi.org/project/asset-scanner/)

Documentation: https://cedadev.github.io/asset-scanner/

The asset scanner provides the framework and access to shared tools. 
The framework allows you to build extractors to get metadata from file objects using plugins to change the source of the 
files, the output of the metadata and the processing chain which extracts the metadata. 
The framework leverages a modular, plugin architecture to allow users to modify the workflow to fit their needs.

![Asset Scanner Diagram](docs/source/images/asset_scanner_diagram.png)