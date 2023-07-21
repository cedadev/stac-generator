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
            "elasticsearch = stac_generator.plugins.inputs.elasticsearch:ElasticsearchInput",
        ],
        "stac_generator.outputs": [
            "standard_out = stac_generator.plugins.outputs.standard_out:StandardOutOutput",
            "standard_out_bulk = stac_generator.plugins.bulk_outputs.standard_out:StandardOutBulkOutput",
            "elasticsearch = stac_generator.plugins.outputs.elasticsearch:ElasticsearchOutput",
            "elasticsearch_bulk = stac_generator.plugins.bulk_outputs.elasticsearch:ElasticsearchBulkOutput",
            "stacapi = stac_generator.plugins.outputs.stacapi_backend:StacApiOutputBackend",
            "text_file = stac_generator.plugins.outputs.text_file:TextFileOutput",
            "json_file = stac_generator.plugins.outputs.json_file:JsonFileOutput",
            "rabbitmq = stac_generator.plugins.outputs.rabbit_mq:RabbitMQOutput",
            "rabbitmq_bulk = stac_generator.plugins.bulk_outputs.rabbit_mq:RabbitMQBulkOutput",
            "intake_esm = stac_generator.plugins.outputs.intake_esm:IntakeESMOutput",
        ],
        "stac_generator.extraction_methods": [
            "regex = stac_generator.plugins.extraction_methods.regex:RegexExtract",
            "default = stac_generator.plugins.extraction_methods.default:DefaultExtract",
            "categories = stac_generator.plugins.extraction_methods.categories:CategoriesExtract",
            "header = stac_generator.plugins.extraction_methods.header.header:HeaderExtract",
            "iso19115 = stac_generator.plugins.extraction_methods.iso19115:ISO19115Extract",
            "xml = stac_generator.plugins.extraction_methods.xml:XMLExtract",
            "elasticsearch = stac_generator.plugins.extraction_methods.elasticsearch:ElasticsearchExtract",
            "json_file = stac_generator.plugins.extraction_methods.json_file:JsonFileExtract",
            "path_parts = stac_generator.plugins.extraction_methods.path_parts:PathPartsExtract",
            "os_stats = stac_generator.plugins.extraction_methods.os_stats:OsStatsExtract",
            "boto_stats = stac_generator.plugins.extraction_methods.boto_stats:BotoStatsExtract",
            "fsspec_stats = stac_generator.plugins.extraction_methods.fsspec_stats:FsSpecStatsExtract",
            "ceda_vocabulary = stac_generator.plugins.extraction_methods.ceda_vocabulary:CEDAVocabularyExtract",
            "controlled_vocabulary = stac_generator.plugins.extraction_methods.controlled_vocabulary:ControlledVocabularyExtract",
            "dot_seperated_str = stac_generator.plugins.extraction_methods.dot_seperated_str:DotSeperatedStrExtract",
            "hash = stac_generator.plugins.extraction_methods.hash:HashExtract",
            "basename = stac_generator.plugins.extraction_methods.basename:BasenameExtract",
            "ceda_observation = stac_generator.plugins.extraction_methods.ceda_observation:CEDAObservationExtract",
            "iso_date = stac_generator.plugins.extraction_methods.iso_date:ISODateExtract",
            "facet_map = stac_generator.plugins.extraction_methods.facet_map:FacetMapExtract",
            "bbox = stac_generator.plugins.extraction_methods.bbox:BboxExtract",
            "geometry_line = stac_generator.plugins.extraction_methods.geometry_line:GeometryLineExtract",
            "geometry_point = stac_generator.plugins.extraction_methods.geometry_point:GeometryPointExtract",
            "geometry_polygon = stac_generator.plugins.extraction_methods.geometry_polygon:GeometryPolygonExtract",
            "string_join = stac_generator.plugins.extraction_methods.string_join:StringJoinExtract",
            "date_combinator = stac_generator.plugins.extraction_methods.date_combinator:DateCombinatorExtract",
            "facet_prefix = stac_generator.plugins.extraction_methods.facet_prefix:FacetPrefixExtract",
        ],
        "stac_generator.extraction_methods.header.backends": [
            "ncml = stac_generator.plugins.extraction_methods.header.backends.ncml:NcMLBackend",
            "xarray = stac_generator.plugins.extraction_methods.header.backends.xarray:XarrayBackend",
            "cf = stac_generator.plugins.extraction_methods.header.backends.cf:CfBackend",
        ],
        "stac_generator.mappings": [
            "ceda = stac_generator.plugins.mappings.ceda:CEDAMapping"
        ],
        "stac_generator.generators": [
            "asset = stac_generator.plugins.generators.asset:AssetGenerator",
            "item = stac_generator.plugins.generators.item:ItemGenerator",
            "collection = stac_generator.plugins.generators.collection:CollectionGenerator",
        ],
    },
)
