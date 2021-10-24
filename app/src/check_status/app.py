"""
CheckStatus

Checks the status of the stack and returns current status
"""

import boto3
from botocore.exceptions import ClientError
from cloudwedge.utils.logger import get_logger
from cloudwedge.utils.sts import get_spoke_session

LOGGER = get_logger('CheckStatus')


# Setup boto3 session
SESSION = None
CLIENT_FORMATION = None


# Status that will be marked complete with no more actions needed
TRIGGER_COMPLETE = [
    'CREATE_COMPLETE',
    'UPDATE_COMPLETE',
    'DELETE_COMPLETE'
]

# Status that will remain in progress
TRIGGER_INPROGRESS = [
    'CREATE_IN_PROGRESS',
    'UPDATE_IN_PROGRESS',
    'ROLLBACK_IN_PROGRESS',
    'DELETE_IN_PROGRESS',
    'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS',
    'UPDATE_ROLLBACK_IN_PROGRESS',
    'REVIEW_IN_PROGRESS',
    'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS'
]

# Status that will need intervention to recover from
TRIGGER_ERROR = [
    'DELETE_FAILED',
    'CREATE_FAILED',
    'ROLLBACK_FAILED',
    'UPDATE_ROLLBACK_FAILED',
    'UPDATE_ROLLBACK_COMPLETE'
]

# Status that will trigger a delete stack operation
TRIGGER_DELETE = [
    'ROLLBACK_COMPLETE'
]


class CheckStatus():
    def __init__(self, target_account_id=None, event=None):
        # Set up event
        self.target_account_id = target_account_id
        self.event = event
        # Get stack name from event
        self.stack_name = self.event['stackStatus']['stackName']

    def run(self):
        """Run"""

        global SESSION
        global CLIENT_FORMATION

        if not SESSION:
            SESSION = get_spoke_session(self.target_account_id)

        if not CLIENT_FORMATION:
            CLIENT_FORMATION = SESSION.client('cloudformation')

        # Setup output for return
        output = {
            'inProgress': False,
            'stackName': self.stack_name,
            'hasError': False,
            'stackErrors': []
        }

        # Add wait attempt
        output['waitAttempts'] = self.event['stackStatus']['waitAttempts'] + 1

        # Get status for the stack
        stack_status = self._get_stack_status()

        # Triage the status and handle accordingly
        if self._stack_status_is_complete(stack_status):
            # Stack is done, dont need to continue
            pass

        elif self._stack_status_is_inprogress(stack_status):
            # Stack is still in progress, wait for it to finish, and have it loop back through
            output['inProgress'] = True

        elif self._stack_status_is_delete(stack_status):
            stack_error = {
                'StackName': self.stack_name,
                'Message': f'Stack ({self.stack_name}) is in state {stack_status}: create failed and has been deleted. Please review and see whats going to figure out what needs to change.'
            }

            # Stack has a status, that cant be recovered, must delete
            try:
                self._delete_stack()
            except Exception as err:
                # Not going to raise here, but it will be published later
                stack_error['DeleteError'] = err

            output['hasError'] = True
            output['stackErrors'].append(stack_error)

        elif self.stack_status_is_error(stack_status):
            # Stack has an error status
            stack_error = {
                'StackName': self.stack_name,
                'Message': f'Stack ({self.stack_name}) is in state {stack_status} and unrecoverable right now, need some help to fix this up. Please review and see whats going to figure out what needs to change.'
            }

            output['hasError'] = True
            output['stackErrors'].append(stack_error)

        return output

    def _get_stack_status(self):
        '''Get the status of the stack'''

        try:

            response = CLIENT_FORMATION.describe_stacks(
                StackName=self.stack_name)
            stack = response['Stacks'][0]
            stack_status = stack['StackStatus']

            return stack_status

        except ClientError as err:
            if 'does not exist' in err.response['Error']['Message']:
                return 'DELETE_COMPLETE'

        except Exception as err:
            LOGGER.info(f'Failed to get stack status with error: {err}')
            raise err

    def _delete_stack(self):
        '''Delete stack'''
        LOGGER.info(f'Attempting to delete stack: {self.stack_name}')

        try:
            response = CLIENT_FORMATION.delete_stack(StackName=self.stack_name)
            LOGGER.info(f'Delete stack response: {response}')
        except Exception as err:
            LOGGER.error(f'Error deleting stack: {err}')
            raise err

    @staticmethod
    def _stack_status_is_complete(status):
        '''Return status'''
        return bool(status in TRIGGER_COMPLETE)

    @staticmethod
    def _stack_status_is_inprogress(status):
        '''Return status'''
        return bool(status in TRIGGER_INPROGRESS)

    @staticmethod
    def stack_status_is_error(status):
        '''Return status'''
        return bool(status in TRIGGER_ERROR)

    @staticmethod
    def _stack_status_is_delete(status):
        '''Return status'''
        return bool(status in TRIGGER_DELETE)
