'''s3.py'''
from os import environ

import boto3
from cloudwedge.utils.logger import get_logger

# Setup logger
LOGGER = get_logger('util.s3')

SESSION = boto3.session.Session()
STS_CLIENT = SESSION.client('sts')

SPOKE_WORKER_ROLE_NAME = environ.get('SPOKE_WORKER_ROLE_NAME')


def get_spoke_session(target_account_id):
    '''Get boto3 session for target spoke aws account'''
    LOGGER.info(f"Getting session in the spoke target account: {target_account_id}")

    spoke_target_role = f"arn:aws:iam::{target_account_id}:role/{SPOKE_WORKER_ROLE_NAME}"

    try:
        spoke_assume_role=STS_CLIENT.assume_role(
            RoleArn=spoke_target_role,
            RoleSessionName="CloudWedgeAssumeRoleHubToSpoke"
        )
    except Exception as err:
        LOGGER.error(f"Failed to assume the role in the tools account with error: {err}")
        raise err

    try:
        spoke_session = boto3.session.Session(
            aws_access_key_id=spoke_assume_role['Credentials']['AccessKeyId'],
            aws_secret_access_key=spoke_assume_role['Credentials']['SecretAccessKey'],
            aws_session_token=spoke_assume_role['Credentials']['SessionToken'],
        )
    except Exception as err:
        LOGGER.error(f"Failed to create boto3 session for spoke using the assumed role credentials with error: {err}")
        raise err

    return spoke_session
