from setuptools import find_packages, setup

with open("README.md") as readme_file:
    _long_description = readme_file.read()

setup(
    name="stac_generator",
    version="1.0.2",
    description="Framework to provide plugin architecture to allow the scanning of assets to extract metadata and facets.",
    author="Richard Smith",
    url="https://github.com/cedadev/asset-scanner/",
    long_description=_long_description,
    long_description_content_type="text/markdown",
    license="BSD - See asset_extractor/LICENSE file for details",
    packages=find_packages(),
    test_suite="tests",
    package_data={"stac_generator": ["LICENSE"]},
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
    python_requires=">=3.7",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "stac_generator = stac_generator.scripts.stac_generator:main",
        ],
        "stac_generator.input_plugins": [
            "file_system = stac_generator.plugins.input_plugins.file_system_input:FileSystemInputPlugin",
            "object_store = stac_generator.plugins.input_plugins.object_store_input:ObjectStoreInputPlugin",
            "intake_esm = stac_generator.plugins.input_plugins.intake_esm_input:IntakeESMInputPlugin",
            "rabbitmq_in = stac_generator.plugins.input_plugins.rabbit_mq_input:RabbitMQInputPlugin",
            "thredds = stac_generator.plugins.input_plugins.thredds_input:ThreddsInputPlugin",
            "file_input = stac_generator.plugins.input_plugins.file_input:FileInputPlugin",
            "solr_input = stac_generator.plugins.input_plugins.solr_input:SolrInputPlugin",
        ],
        "stac_generator.output_plugins": [
            "standard_out = stac_generator.plugins.output_plugins.standard_out:StdoutOutputBackend",
            "elasticsearch = stac_generator.plugins.output_plugins.elasticsearch_backend:ElasticsearchOutputBackend",
            "file_out = stac_generator.plugins.output_plugins.file_out:FileoutOutputBackend",
            "json_out = stac_generator.plugins.output_plugins.json_out:JsonOutputBackend",
            "rabbitmq_out = stac_generator.plugins.output_plugins.rabbit_mq_output:RabbitMQOutBackend",
        ],
        "stac_generator.plugin_filters": [
            "path_regex = stac_generator.plugins.filters.path_regex:PathRegexFilter",
        ],
        "stac_generator.extraction_methods": [
            "regex = stac_generator.plugins.extraction_methods.regex_extract:RegexExtract",
            "header = stac_generator.plugins.extraction_methods.header_extract.header_extract:HeaderExtract",
            "iso19115 = stac_generator.plugins.extraction_methods.iso19115_extract:ISO19115Extract",
            "xml = stac_generator.plugins.extraction_methods.xml_extract:XMLExtract",
            "elasticsearch = stac_generator.plugins.extraction_methods.elasticsearch_extract:ElasticsearchExtract",
            "json_file = stac_generator.plugins.extraction_methods.json_file_extract:JsonFileExtract",
            "posix_stats = stac_generator.plugins.extraction_methods.posix_stats_extract:PosixStatsExtract",
            "object_store_stats = stac_generator.plugins.extraction_methods.object_store_stats_extract:ObjectStoreStatsExtract",
        ],
        "stac_generator.post_extraction_methods": [
            "vocab = stac_generator.plugins.post_extraction_methods.vocab_extract:VocabExtract",
        ],
        "stac_generator.id_extraction_methods": [
            "default = stac_generator.plugins.id_extraction_methods.default_extract:DefaultExtract",
            "hash = stac_generator.plugins.id_extraction_methods.hash_extract:HashExtract",
        ],
        "stac_generator.extraction_methods.header_extract.backends": [
            "xarray = stac_generator.plugins.extraction_methods.header_extract.backends.xarray:XarrayBackend",
            "cf = stac_generator.plugins.extraction_methods.header_extract.backends.cf:CfBackend",
        ],
        "stac_generator.pre_processors": [
            "filename_reducer = stac_generator.plugins.extraction_methods.preprocessors:ReducePathtoName",
            "ceda_observation = stac_generator.plugins.extraction_methods.preprocessors:CEDAObservation",
        ],
        "stac_generator.post_processors": [
            "isodate_processor = stac_generator.plugins.extraction_methods.postprocessors:ISODateProcessor",
            "facet_map = stac_generator.plugins.extraction_methods.postprocessors:FacetMapProcessor",
            "stac_bbox = stac_generator.plugins.extraction_methods.postprocessors:BBOXProcessor",
            "string_join = stac_generator.plugins.extraction_methods.postprocessors:StringJoinProcessor",
            "date_combinator = stac_generator.plugins.extraction_methods.postprocessors:DateCombinatorProcessor",
            "facet_prefix = stac_generator.plugins.extraction_methods.postprocessors:FacetPrefixProcessor",
        ],
        "stac_generator.generators": [
            "asset = stac_generator.plugins.generators.asset_generator:AssetGenerator",
            "item = stac_generator.plugins.generators.item_generator:ItemGenerator",
            "collection = stac_generator.plugins.generators.collection_generator:CollectionGenerator",
        ],
    },
)
