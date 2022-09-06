from setuptools import find_packages, setup

with open("README.md") as readme_file:
    _long_description = readme_file.read()

setup(
    name="stac_generator",
    version="1.0.2",
    description="Framework to provide plugin architecture to allow the scanning of assets to extract metadata and facets.",
    author="Richard Smith",
    url="https://github.com/cedadev/stac-scanner/",
    long_description=_long_description,
    long_description_content_type="text/markdown",
    license="BSD - See stac_generator/LICENSE file for details",
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
        "stac_generator.inputs": [
            "file_system = stac_generator.plugins.inputs.file_system:FileSystemInput",
            "object_store = stac_generator.plugins.inputs.object_store:ObjectStoreInput",
            "intake_esm = stac_generator.plugins.inputs.intake_esm:IntakeESMInput",
            "rabbitmq = stac_generator.plugins.inputs.rabbit_mq:RabbitMQInput",
            "thredds = stac_generator.plugins.inputs.thredds:ThreddsInput",
            "text_file = stac_generator.plugins.inputs.text_file:TextFileInput",
            "solr = stac_generator.plugins.inputs.solr:SolrInput",
        ],
        "stac_generator.outputs": [
            "standard_out = stac_generator.plugins.outputs.standard_out:StandardOutOutput",
            "elasticsearch = stac_generator.plugins.outputs.elasticsearch:ElasticsearchOutput",
            "text_file = stac_generator.plugins.outputs.text_file:TextFileOutput",
            "json_file = stac_generator.plugins.outputs.json_file:JsonFileOutput",
            "rabbitmq = stac_generator.plugins.outputs.rabbit_mq:RabbitMQOutput",
            "intake_esm = stac_generator.plugins.outputs.intake_esm:IntakeESMOutput",
        ],
        "stac_generator.filters": [
            "path_regex = stac_generator.plugins.filters.path_regex:PathRegexFilter",
        ],
        "stac_generator.extraction_methods": [
            "regex = stac_generator.plugins.extraction_methods.regex:RegexExtract",
            "default = stac_generator.plugins.extraction_methods.default:DefaultExtract",
            "header = stac_generator.plugins.extraction_methods.header.header:HeaderExtract",
            "file_stats = stac_generator.plugins.extraction_methods.file_stats.file_stats:FileStatsExtract",
            "iso19115 = stac_generator.plugins.extraction_methods.iso19115:ISO19115Extract",
            "xml = stac_generator.plugins.extraction_methods.xml:XMLExtract",
            "elasticsearch = stac_generator.plugins.extraction_methods.elasticsearch:ElasticsearchExtract",
            "json_file = stac_generator.plugins.extraction_methods.json_file:JsonFileExtract",
            "posix_stats = stac_generator.plugins.extraction_methods.posix_stats:PosixStatsExtract",
            "object_store_stats = stac_generator.plugins.extraction_methods.object_store_stats:ObjectStoreStatsExtract",
        ],
        "stac_generator.post_extraction_methods": [
            "ceda_vocabulary = stac_generator.plugins.post_extraction_methods.ceda_vocabulary:CEDAVocabularyPostExtract",
            "controlled_vocabulary = stac_generator.plugins.post_extraction_methods.controlled_vocabulary:ControlledVocabularyPostExtract",
        ],
        "stac_generator.id_extraction_methods": [
            "default = stac_generator.plugins.id_extraction_methods.default:DefaultIdExtract",
            "hash = stac_generator.plugins.id_extraction_methods.hash:HashIdExtract",
        ],
        "stac_generator.extraction_methods.header.backends": [
            "ncml = stac_generator.plugins.extraction_methods.header.backends.ncml:NcMLBackend",
            "xarray = stac_generator.plugins.extraction_methods.header.backends.xarray:XarrayBackend",
            "cf = stac_generator.plugins.extraction_methods.header.backends.cf:CfBackend",
        ],
        "stac_generator.extraction_methods.file_stats.backends": [
            "boto = stac_generator.plugins.extraction_methods.file_stats.backends.boto:BotoStats",
            "fsspec = stac_generator.plugins.extraction_methods.file_stats.backends.fsspec:FsSpecStats",
            "os = stac_generator.plugins.extraction_methods.file_stats.backends.os:OsStats",
        ],
        "stac_generator.pre_processors": [
            "basename = stac_generator.plugins.preprocessors.basename:BasenamePreProcessor",
            "ceda_observation = stac_generator.plugins.preprocessors.ceda_observation:CEDAObservationPreProcessor",
        ],
        "stac_generator.post_processors": [
            "isodate = stac_generator.plugins.postprocessors.iso_date:ISODatePostProcessor",
            "facet_map = stac_generator.plugins.postprocessors.facet_map:FacetMapPostProcessor",
            "stac_bbox = stac_generator.plugins.postprocessors.bbox:BboxPostProcessor",
            "geometry_line = stac_generator.plugins.postprocessors.geometry_line:GeometryLinePostProcessor",
            "geometry_point = stac_generator.plugins.postprocessors.geometry_point:GeometryPointPostProcessor",
            "geometry_polygon = stac_generator.plugins.postprocessors.geometry_polygon:GeometryPolygonPostProcessor",
            "string_join = stac_generator.plugins.postprocessors.string_join:StringJoinPostProcessor",
            "date_combinator = stac_generator.plugins.postprocessors.date_combinator:DateCombinatorPostProcessor",
            "facet_prefix = stac_generator.plugins.postprocessors.facet_prefix:FacetPrefixPostProcessor",
        ],
        "stac_generator.generators": [
            "asset = stac_generator.plugins.generators.asset:AssetGenerator",
            "item = stac_generator.plugins.generators.item:ItemGenerator",
            "collection = stac_generator.plugins.generators.collection:CollectionGenerator",
        ],
    },
)
