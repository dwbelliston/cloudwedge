'''s3.py'''
import os

import boto3
from cloudwedge.utils.logger import get_logger

# Setup logger
LOGGER = get_logger('util.s3')

RESOURCE_S3 = None


def s3_save_object(session, bucket: str, key: str, content=None):
    '''Save the contents to the given target object'''

    global RESOURCE_S3

    if not RESOURCE_S3:
        RESOURCE_S3 = session.resource('s3')

    s3_object = RESOURCE_S3.Object(bucket, key)

    try:
        s3_object.put(Body=content)

        return s3_object.key

    except Exception as err:
        raise err
