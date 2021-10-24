"""
DeleteStack

Deletes a cloudformation stack by its name
"""

from botocore.exceptions import WaiterError
from cloudwedge.utils.logger import get_logger
from cloudwedge.utils.sts import get_spoke_session

LOGGER = get_logger('DeleteStack')


# Setup boto3 session
SESSION = None
CLIENT_FORMATION = None


class DeleteStack():
    def __init__(self, target_account_id=None, event=None):

        self.target_account_id = target_account_id
        # Pull values off event
        self.stack_owner = event['stack']['stackOwner']
        self.stack_name = event['stack']['stackName']

    def run(self):
        """Run"""

        global SESSION
        global CLIENT_FORMATION

        if not SESSION:
            SESSION = get_spoke_session(self.target_account_id)

        if not CLIENT_FORMATION:
            CLIENT_FORMATION = SESSION.client('cloudformation')

        # Delete the stack, catch response to know
        stack_deleted = self._delete_stack()

        output = {
            'inProgress': not stack_deleted,
            'stackOwner': self.stack_owner,
            'stackName': self.stack_name,
            'targetAccountId': self.target_account_id,
            'waitAttempts': 0
        }

        return output

    def _delete_stack(self) -> bool:
        """Delete stack and do quick check if its deleted or not"""

        try:
            LOGGER.info(f'Attempting to delete stack: {self.stack_name}')
            response = CLIENT_FORMATION.delete_stack(StackName=self.stack_name)

            # Wait just a little, it could have been a speedy delivery
            try:
                res = CLIENT_FORMATION.get_waiter('stack_delete_complete').wait(
                    StackName=self.stack_name,
                    WaiterConfig={
                        'Delay': 1,
                        'MaxAttempts': 1
                    }
                )

                LOGGER.info(f'Stack delete is completed')
                return True

            except WaiterError as err:
                LOGGER.info(f'Stack delete is still in progress, even after a little wait')
                return False

        except Exception as err:
            LOGGER.error('Error deleting stack {err}')
            raise err
