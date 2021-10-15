from setuptools import setup, find_packages

with open("README.md") as readme_file:
    _long_description = readme_file.read()

setup(
    name='asset_scanner',
    version='0.1.0',
    description='High level library to provide I/O packages',
    author='Richard Smith',
    url='https://github.com/cedadev/asset-scanner/',
    long_description=_long_description,
    long_description_content_type='text/markdown',
    license='BSD - See asset_extractor/LICENSE file for details',
    packages=find_packages(),
    test_suite='tests',
    package_data={
        'asset_scanner': [
            'LICENSE'
        ]
    },
    install_requires=[
        'pyyaml',
        'directory_tree',
        'tqdm'
    ],
    extras_require={
        'docs': [
            'sphinx',
            'sphinx-rtd-theme',
            'elasticsearch',
            'sphinxcontrib-programoutput'
        ],
        'elasticsearch': [
            'elasticsearch'
        ],
        'intake-esm': [
            'intake-esm'
        ],
        'rabbitmq': [
            'pika'
        ]
    },
    python_requires='>=3.5',
    tests_require=[
        'pytest'
    ],
    entry_points={
        'console_scripts': [
            'asset_scanner = asset_scanner.scripts.asset_scanner:main',
        ],
        'asset_scanner.output_plugins': [
            'standard_out = asset_scanner.plugins.output_plugins.standard_out:StdoutOutputBackend',
            'elasticsearch = asset_scanner.plugins.output_plugins.elasticsearch_backend:ElasticsearchOutputBackend',
        ],
        'asset_scanner.plugin_filters': [
            'path_regex = asset_scanner.plugins.filters.path_regex:PathRegexFilter',
        ],
        'asset_scanner.input_plugins': [
            'file_system = asset_scanner.plugins.input_plugins.file_system_input:FileSystemInputPlugin',
            'object_store = asset_scanner.plugins.input_plugins.object_store_input:ObjectStoreInputPlugin',
            'intake_esm = asset_scanner.plugins.input_plugins.intake_esm_input:IntakeESMInputPlugin',
            'rabbit_mq = asset_scanner.plugins.input_plugins.rabbit_mq_input:RabbitMQInputPlugin',
        ]
    }
)
