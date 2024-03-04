# STAC Generator

[![Test](https://github.com/cedadev/stac-generator/actions/workflows/tests.yml/badge.svg)](https://github.com/cedadev/stac-generator/actions/workflows/tests.yml)
[![Docs](https://github.com/cedadev/stac-generator/actions/workflows/docs_build.yml/badge.svg)](https://github.com/cedadev/stac-generator/actions/workflows/docs_build.yml)
[![Documentation Status](https://readthedocs.org/projects/pip/badge/?version=stable)](https://pip.pypa.io/en/stable/?badge=stable)
[![Upload Python Package](https://github.com/cedadev/stac-generator/actions/workflows/release.yml/badge.svg)](https://pypi.org/project/stac-generator/)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

Documentation: https://cedadev.github.io/stac-generator/

The STAC Generator provides the framework and access to shared tools.
The framework allows you to build generators to get metadata from file objects using plugins to change the source of the
files, the output of the metadata and the processing chain which extracts the metadata.
The framework leverages a modular, plugin architecture to allow users to modify the workflow to fit their needs.

![STAC Generator Diagram](docs/source/images/stac_generator_diagram.png)
