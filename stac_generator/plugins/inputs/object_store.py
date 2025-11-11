# encoding: utf-8
"""
Object Store Input
------------------

Takes an endpoint url and optionally a bucket prefix and delimiter and will
scan the items at these points in the object store, submitting each to the
asset generator

**Plugin name:** ``object_store``

.. list-table::
    :header-rows: 1

    * - Option
      - Value Type
      - Description
    * - ``session_kwargs``
      - ``dict``
      - ``REQUIRED`` Dictionary containing the S3 access and secret keys
    * - ``endpoint_url``
      - ``string``
      - ``REQUIRED`` URL for S3 endpoint
    * - ``bucket``
      - ``string``
      - Bucket to be scanned. If ``None`` all buckets in endpoint will be scanned.
    * - ``prefix``
      - ``string``
      - Only items with prefix will be scanned
    * - ``delimiter``
      - ``string``
      - Group items after delimiter into one object

Example Configuration:
    .. code-block:: yaml

        inputs:
            - method: object_store
                endpoint_url: https://cedadev-o.s3-ext.jc.rl.ac.uk
                session_kwargs: {
                    aws_access_key_id: ACCESS_KEY,
                    aws_secret_access_key: SECRET_KEY
                }
                buckets:
                  - my_bucket
                prefix: directory_or_file
                delimiter: .zarr/

"""
__author__ = "Rhys Evans"
__date__ = "02 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "rhys.r.evans@stfc.ac.uk"


import logging

import boto3
from pydantic import BaseModel, Field

# Package imports
from stac_generator.core.input import Input

LOGGER = logging.getLogger(__name__)


class ObjectStoreConf(BaseModel):
    """Object Store Config."""

    url: str = Field(
        description="URL of datastore.",
    )
    buckets: list[str] = Field(
        default=-1,
        description="Number of rows to skip.",
    )
    prefix: str = Field(
        description="URL of datastore.",
    )
    delimiter: str = Field(
        description="URL of datastore.",
    )
    session_kwargs: dict = Field(
        default={},
        description="session kwargs.",
    )


class ObjectStoreInput(Input):
    """ """

    config_class = ObjectStoreConf

    def run(self):

        session = boto3.session.Session(**self.conf.session_kwargs)
        s3 = session.resource(
            "s3",
            endpoint_url=self.conf.url,
        )

        buckets = (
            [s3.Bucket(bucket) for bucket in self.conf.buckets]
            if self.conf.buckets
            else s3.buckets.all()
        )

        for bucket in buckets:
            total_files = 0

            for obj in bucket.objects.filter(
                Prefix=self.conf.prefix, Delimiter=self.conf.delimiter
            ):

                yield {
                    "uri": f"{self.conf.url}/{bucket.name}/{obj.key}",
                    "client": s3.meta.client,
                }
                total_files += 1

            LOGGER.info("Processed %s files from %s", total_files, bucket)
