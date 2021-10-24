"""
CleanupResources

Custom resources lambda to cleanup resources when application is deleted
"""

import json

import boto3
from botocore.exceptions import ClientError
import cfnresponse

from cloudwedge.utils.logger import get_logger
from cloudwedge.models import AWSService


LOGGER = get_logger('CleanupResources')


# Setup boto3 session
SESSION = boto3.session.Session()
CLIENT_FORMATION = SESSION.client('cloudformation')


class CleanupResources():
    def __init__(self, event=None):
        # Set up event
        self.event = event

    def run(self):
        """Run"""

        # Setup output for return
        output = {}

        try:
            # Delete has been issued, cleaning up stacks

            # Get Stacks in target account
            stacks = self._get_stacks()

            # Check for no stacks condition
            if not stacks:
                LOGGER.info(
                    f'No Stacks found, no cleanup needed. Returning success.')
            else:
                LOGGER.info(
                    f'Found {len(stacks)} stacks. Deleting them.')

                deleted_stacks = []


                for d_stack in stacks:
                    deleted_stacks.append(d_stack['StackName'])
                    self._delete_stack(d_stack['StackName'])

                output = {
                    'deleted_stacks': json.dumps(deleted_stacks, default=str)
                }

        except Exception as err:
            LOGGER.error(f'Failed to run cleanup with error: {err}')
            raise err

        return output


    def _get_stacks(self):
        '''Return all alarm stacks for the application'''
        stacks = []

        try:
            paginator = CLIENT_FORMATION.get_paginator(
                'describe_stacks').paginate()

            for page_instances in paginator:

                for stack in page_instances['Stacks']:
                    # Filter to stacks that have a tag with identifier
                    if any((
                        tag['Key'].strip() == AWSService.TAG_STACK_ID_KEY and
                        tag['Value'] == AWSService.TAG_STACK_ID_VALUE
                    ) for tag in stack['Tags']):

                        stacks.append(stack)

            return stacks
        except Exception as err:
            LOGGER.info(f'Failed to get stacks with error: {err}')
            raise err


    def _delete_stack(self, stack_name):
        '''Delete stack'''
        LOGGER.info(f'Attempting to delete stack: {stack_name}')

        try:
            response = CLIENT_FORMATION.delete_stack(
                StackName=stack_name
            )
            LOGGER.info(f'Delete stack response: {response}')
        except Exception as err:
            LOGGER.error('Error deleting stack {err}')
            raise err
