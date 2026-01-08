# encoding: utf-8
""" """
__author__ = "Richard Smith"
__date__ = "08 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import cProfile
import logging

import click
import yaml

from stac_generator.core.generator import Generator


def setup_logging(conf):
    config = conf.get("logging", {})
    if not config or (config and not config.get("format")):
        config["format"] = "%(asctime)s %(name)s %(levelname)s %(message)s"

    logging.basicConfig(**config)


@click.command()
@click.option(
    "--conf",
    "-c",
    "conf",
    required=True,
    help="Path for generator configuration.",
)
@click.option(
    "--prof",
    "-p",
    "prof",
    help="Path for profile output file.",
)
def main(conf, prof):
    if prof:
        if not prof.lower().endswith((".pstats")):
            prof += ".pstats"
        profiler = cProfile.Profile()
        profiler.enable()

    with open(conf, mode="r", encoding="utf-8") as reader:
        conf = yaml.safe_load(reader)

    generator = Generator(conf)

    generator.run()

    if prof:
        profiler.disable()
        profiler.dump_stats(prof)


if __name__ == "__main__":
    main()
