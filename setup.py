from setuptools import find_packages, setup

with open("README.md") as readme_file:
    _long_description = readme_file.read()

setup(
    name="asset_scanner",
    version="1.0.2",
    description="Framework to provide plugin architecture to allow the scanning of assets to extract metadata and facets.",
    author="Richard Smith",
    url="https://github.com/cedadev/asset-scanner/",
    long_description=_long_description,
    long_description_content_type="text/markdown",
    license="BSD - See asset_extractor/LICENSE file for details",
    packages=find_packages(),
    test_suite="tests",
    package_data={"asset_scanner": ["LICENSE"]},
    install_requires=["pyyaml", "ceda-directory-tree", "tqdm", "pydantic"],
    extras_require={
        "docs": [
            "sphinx",
            "sphinx-rtd-theme",
            "elasticsearch",
            "sphinxcontrib-programoutput",
        ],
        "elasticsearch": ["elasticsearch"],
        "intake-esm": ["intake-esm"],
        "rabbitmq": ["pika"],
        "thredds": ["siphon"],
    },
    python_requires=">=3.5",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "asset_scanner = asset_scanner.scripts.asset_scanner:main",
        ],
        "asset_scanner.input_plugins": [
            "file_system = asset_scanner.plugins.input_plugins.file_system_input:FileSystemInputPlugin",
            "object_store = asset_scanner.plugins.input_plugins.object_store_input:ObjectStoreInputPlugin",
            "intake_esm = asset_scanner.plugins.input_plugins.intake_esm_input:IntakeESMInputPlugin",
            "rabbit_mq = asset_scanner.plugins.input_plugins.rabbit_mq_input:RabbitMQInputPlugin",
            "thredds = asset_scanner.plugins.input_plugins.thredds_input:ThreddsInputPlugin",
        ],
        "asset_scanner.output_plugins": [
            "standard_out = asset_scanner.plugins.output_plugins.standard_out:StdoutOutputBackend",
            "elasticsearch = asset_scanner.plugins.output_plugins.elasticsearch_backend:ElasticsearchOutputBackend",
        ],
        "asset_scanner.plugin_filters": [
            "path_regex = asset_scanner.plugins.filters.path_regex:PathRegexFilter",
        ],
        "asset_scanner.facet_extractors": [
            "regex = asset_scanner.plugins.extraction_methods.regex_extract:RegexExtract",
            "header_extract = asset_scanner.plugins.extraction_methods.header_extract.header_extract:HeaderExtract",
            "iso19115 = asset_scanner.plugins.extraction_methods.iso19115_extract:ISO19115Extract",
            "xml_extract = asset_scanner.plugins.extraction_methods.xml_extract:XMLExtract",
        ],
        "asset_scanner.extraction_methods.header_extract.backends": [
            "xarray = asset_scanner.plugins.extraction_methods.header_extract.backends.xarray:XarrayBackend",
            "cf = asset_scanner.plugins.extraction_methods.header_extract.backends.cf:CfBackend",
        ],
        "asset_scanner.pre_processors": [
            "filename_reducer = asset_scanner.plugins.extraction_methods.preprocessors:ReducePathtoName",
            "ceda_observation = asset_scanner.plugins.extraction_methods.preprocessors:CEDAObservation",
        ],
        "asset_scanner.post_processors": [
            "isodate_processor = asset_scanner.plugins.extraction_methods.postprocessors:ISODateProcessor",
            "facet_map = asset_scanner.plugins.extraction_methods.postprocessors:FacetMapProcessor",
            "stac_bbox = asset_scanner.plugins.extraction_methods.postprocessors:BBOXProcessor",
            "string_join = asset_scanner.plugins.extraction_methods.postprocessors:StringJoinProcessor",
            "date_combinator = asset_scanner.plugins.extraction_methods.postprocessors:DateCombinatorProcessor",
        ],
    },
)
