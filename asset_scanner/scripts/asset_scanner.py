# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '08 Jun 2021'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

import argparse
import yaml
from pydoc import locate
import pkg_resources

from asset_scanner.core import BaseExtractor
from asset_scanner.core.utils import load_plugins
from asset_scanner.core.exceptions import NoPluginsError

import logging


def command_args():
    """
    Sets the command line arguments and handles their parsing
    :return: command line options
    """
    parser = argparse.ArgumentParser(description='Run the asset scanner as configured')
    parser.add_argument('conf', help='Path to a yaml configuration file')
    args = parser.parse_args()

    return args


def setup_logging(conf):
    config = conf.get('logging', {})
    if not config or (config and not config.get('format')):
        config['format'] = '%(asctime)s %(name)s %(levelname)s %(message)s'

    logging.basicConfig(**config)


def load_config(path):
    with open(path) as reader:
        conf = yaml.safe_load(reader)
    return conf


def load_extractor(conf: dict) -> BaseExtractor:
    """
    Load the extractor.

    Looks for extractor defined in the configuration in preference
    and falls back to the first defined entry point at ``asset_scanner.extractors``

    :param conf: Configuration dict
    :return: Extractor
    """

    extractor = None

    if conf.get('extractor'):
        extractor = locate(conf['extractor'])
        if not extractor:
            raise ImportError(f'Unable to find {conf["extractor"]}. Check that it is installed.')

    if not extractor:
        for entry_point in pkg_resources.iter_entry_points('asset_scanner.extractors'):
            extractor = entry_point.load()

            # Only load the first one
            break

    if not extractor:
        raise NoPluginsError('No extraction plugins have been loaded')

    return extractor(conf)


def main():
    args = command_args()

    conf = load_config(args.conf)

    setup_logging(conf)

    extractor = load_extractor(conf)

    input_plugins = load_plugins(conf, 'asset_scanner.input_plugins', 'inputs')

    for input in input_plugins:
        input.run(extractor)


if __name__ == '__main__':
    main()
