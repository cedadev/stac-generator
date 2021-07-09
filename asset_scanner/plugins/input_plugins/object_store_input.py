# encoding: utf-8
"""
Object Store Input
-----------------

Takes a enpoint url and optionally a bucket prefix and delimiter and will
scan the items at these points in the object store, submitting each to the
asset extractor

**Plugin name:** ``object_store``

Example Configuration:
    .. code-block:: yaml

        inputs:
            - name: object_store
                endpoint_url: https://cedadev-o.s3-ext.jc.rl.ac.uk
                session_kwargs: {
                    aws_access_key_id: ACCESS_KEY,
                    aws_secret_access_key: SECRET_KEY
                }
                bucket: my_bucket
                prefix: directory_or_file
                delimiter: .zarr/

Config Arguments:
    session_kwargs
        ``REQUIRED`` dictionary containing the aws access and secret keys
    endpoint_url
        ``REQUIRED`` url for aws endpoint
    bucket
        bucket to be scanned if none all buckets in endpoint will be scanned
    prefix
        only items with prefix will be scanned
    delimiter
        group items after delimiter into one object

"""
__author__ = 'Rhys Evans'
__date__ = '02 Jun 2021'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'rhys.r.evans@stfc.ac.uk'


from .base import BaseInputPlugin

import boto3

from typing import TYPE_CHECKING
import logging

LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from asset_scanner.core import BaseExtractor


class ObjectStoreInputPlugin(BaseInputPlugin):
    """
    """

    def __init__(self, **kwargs):

        self.endpoint_url = kwargs.get('endpoint_url')
        session = boto3.session.Session(**kwargs['session_kwargs'])
        s3 = session.resource(
            's3',
            endpoint_url=self.endpoint_url,
        )

        self.client = s3.meta.client
        self.buckets = [s3.Bucket(kwargs['bucket'])] if 'bucket' in kwargs else s3.buckets.all()
        self.prefix = kwargs.get('prefix', '')
        self.delimiter = kwargs.get('delimiter', '')

    def run(self, extractor: 'BaseExtractor' ):

        for bucket in self.buckets:
            total_files = 0
            for obj in bucket.objects.filter(Prefix=self.prefix, Delimiter=self.delimiter):
                extractor.process_file(f'{self.endpoint_url}/{bucket.name}/{obj.key}', 'object_store', client=self.client)
                total_files += 1

            LOGGER.info(f'Processed {total_files} files from {bucket}')
