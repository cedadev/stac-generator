# encoding: utf-8
"""

"""
__author__ = "Richard Smith"
__date__ = "08 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import argparse
import cProfile
import logging

import click
import pkg_resources
import yaml

from stac_generator.core.exceptions import NoPluginsError
from stac_generator.core.generator import BaseGenerator
from stac_generator.core.utils import load_plugins

def load_config(path):
    with open(path) as reader:
        conf = yaml.safe_load(reader)
    return conf


def load_generator(conf: dict) -> BaseGenerator:
    """
    Load the generator.

    Looks for generator defined in the configuration in preference
    and falls back to the first defined entry point
    at ``stac_generator.generators``

    :param conf: Configuration dict
    :return: Generator
    """

    generator = None

    if conf.get("generator"):
        entry_points = pkg_resources.iter_entry_points(
            "stac_generator.generators", conf.get("generator")
        )

        for entry_point in entry_points:
            generator = entry_point.load()

            # Only load the first one
            break

    if not generator:
        raise NoPluginsError("No extraction plugins have been loaded")

    return generator(conf)


@click.command()
@click.option(
    "--conf",
    "-c",
    "conf",
    required=True,
    help="Path for generator configuration.",
)
def main(conf):

    conf = load_config(conf)

    generator = load_generator(conf)

    paths_map, location_map = generator.recipes.get_maps()

    print("Path map", path_map)
    print("Location map", location_map)


if __name__ == "__main__":
    main()
