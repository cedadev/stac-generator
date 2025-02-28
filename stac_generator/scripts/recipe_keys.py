# encoding: utf-8
"""

"""
__author__ = "Richard Smith"
__date__ = "08 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import click
import yaml

from stac_generator.core.generator import Generator


@click.command()
@click.option(
    "--conf",
    "-c",
    "conf",
    required=True,
    help="Path for generator configuration.",
)
def main(conf):
    with open(conf, mode="r", encoding="utf-8") as reader:
        conf = yaml.safe_load(reader)

    generator = Generator(conf)

    path_map, location_map = generator.recipes.get_maps()

    print("Path map", path_map)
    print("Location map", location_map)


if __name__ == "__main__":
    main()
