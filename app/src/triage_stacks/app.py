"""
TriageStacks

Identify stacks that have been orphaned. A stack is orphaned when
the owner for a stack no longer exists on any resource. We will
delete the stack because it will never have any more updates.

Output:
List of objects containing orphaned stacks details
"""

import boto3
from cloudwedge.models import AWSService
from cloudwedge.utils.logger import get_logger
from cloudwedge.utils.sts import get_spoke_session

LOGGER = get_logger('TriageStacks')


# Setup boto3 session
SESSION = None
CLIENT_FORMATION = None


class TriageStacks():
    def __init__(self, target_account_id=None, event=None):
        # Set up event
        self.target_account_id = target_account_id
        self.owner_resources = event['ownerResources']
        self.has_orphaned_stacks = False


    def run(self):
        """Run"""

        global SESSION
        global CLIENT_FORMATION

        if not SESSION:
            SESSION = get_spoke_session(self.target_account_id)


        if not CLIENT_FORMATION:
            CLIENT_FORMATION = SESSION.client('cloudformation')

        output = {
            "orphanedStacks": [],
            "hasOrphanedStacks": self.has_orphaned_stacks,
            "targetAccountId": self.target_account_id
        }

        # Get list of stacks grouped by owner
        stacks_grouped_by_owner = self._get_stacks_by_owner()
        stack_owners = list(stacks_grouped_by_owner.keys())

        # Check for no stacks condition
        if not stacks_grouped_by_owner:
            LOGGER.info(
                f'No Stacks found, no pruning needed. Returning output: {output}')
        else:
            LOGGER.info(
                f'Found stacks for {len(stack_owners)} owner(s): {stack_owners}')

        # Compare the owners of the stacks with the owners of the resources
        # Mark for deletion any stacks that dont have resources
        orphaned_stacks = self._get_orphaned_stacks(stacks_grouped_by_owner)

        output = {
            "orphanedStacks": orphaned_stacks,
            "hasOrphanedStacks": bool(orphaned_stacks)
        }

        LOGGER.info(f'Returning output: {output}')
        return output

    def _get_stacks_by_owner(self):
        '''
        Return all stacks that are in the account
        '''
        stacks = {}

        try:
            paginator = CLIENT_FORMATION.get_paginator(
                'describe_stacks').paginate()

            for page_instances in paginator:

                for stack in page_instances['Stacks']:
                    # Filter to stacks that have a tag with cloudwedge identifier
                    if any((
                        tag['Key'].strip() == AWSService.TAG_STACK_ID_KEY and
                        tag['Value'] == AWSService.TAG_STACK_ID_VALUE
                    ) for tag in stack['Tags']):

                        # Get owner tag from the keys
                        owner_tag = next(
                            (tag for tag in stack['Tags'] if tag['Key'] == AWSService.TAG_OWNER), {})

                        if owner_tag:
                            # Has an owner, put stack on owner key for tracking
                            stacks.setdefault(
                                owner_tag['Value'].lower(), []).append(stack)
                        else:
                            stacks.setdefault(AWSService.DEFAULT_OWNER, []).append(stack)

            return stacks
        except Exception as err:
            LOGGER.info(f'Failed to get stacks with error: {err}')
            raise err

    def _get_orphaned_stacks(self, stacks):
        """
        Get orphaned stacks by comparing the current stack owners to the
        owners of the current resources. Any stack that doesnt have the same
        owner on a resource is orphaned.
        """
        orphaned_stacks = []

        # Get list of owners of resources
        resource_owners = list(self.owner_resources.keys()
                               ) if self.owner_resources else []

        # Get list of owners of stacks
        stack_owners = list(stacks.keys())

        # Compare owners and get orphaned stack owners
        orphaned_stack_owners = [
            stack for stack in stack_owners if stack not in set(resource_owners)]

        if orphaned_stack_owners:
            LOGGER.info(f'Stacks owners to delete: {orphaned_stack_owners}')

            for owner in orphaned_stack_owners:
                for owner_stack in stacks[owner]:
                    print(owner_stack['StackName'])
                    orphaned_stack_details = {
                        'stackOwner': owner,
                        'stackName': owner_stack['StackName']
                    }

                    orphaned_stacks.append(orphaned_stack_details)

        else:
            LOGGER.info(f'No stacks need to be deleted.')

        return orphaned_stacks
