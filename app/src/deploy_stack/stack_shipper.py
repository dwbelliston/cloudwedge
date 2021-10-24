"""
StackShipper

StackShipper receives details about a templates location in s3
and uses cloudformation api to deploy the stack
"""

from botocore.exceptions import ClientError
from cloudwedge.models import AWSService
from cloudwedge.utils.logger import get_logger

LOGGER = get_logger('StackShipper')

# Holder for boto3 client
CLIENT_FORMATION = None

class StackShipper():
    def __init__(self, session, s3_bucket: str, s3_key: str, stack_name: str, stack_type: str,
                 stack_owner: str):
        # Place the inputs on self
        self.session = session
        self.bucket = s3_bucket
        self.template_key = s3_key
        self.stack_name = stack_name
        self.stack_type = stack_type
        self.stack_owner = stack_owner

    def ship(self):
        """Receive template and deploy"""

        global CLIENT_FORMATION

        if not CLIENT_FORMATION:
            CLIENT_FORMATION = self.session.client('cloudformation')

        LOGGER.info(
            f"StackShipper: bucket={self.bucket} key={self.template_key} stack={self.stack_name}")

        try:
            # Try to run update stack first
            self._post_stack('update_stack')
            LOGGER.info(f'Updated Stack: {self.stack_name}')

        except ClientError as err:
            # 1) No updates, we can be done
            if 'No updates are to be performed' in err.response['Error']['Message']:
                LOGGER.info(f'No updates are to to be performed.')

            # 2) Stack doesnt exit, run create
            elif 'does not exist' in err.response['Error']['Message']:

                # If it failed on update because it doesnt exist, create instead
                try:
                    self._post_stack('create_stack')
                    LOGGER.info(f'Created Stack: {self.stack_name}')
                except ClientError as err:
                    LOGGER.error(f'Failed to create Stack: {err}')
                    raise err

            # 3) Stack in progress, allow it to finish
            elif any(x in err.response['Error']['Message'] for x in ['UPDATE_IN_PROGRESS', 'CREATE_IN_PROGRESS']):
                # If it failed on update its already being updated, lets take our chance the update in progress is good
                # When an RDS tag is edited, it deletes the tag first which fires an event. Then it updates, another event :)
                LOGGER.info(
                    f'Stack update is in progress, allowing that stack to proceed. Aborting error free.')

            # 4) Something else, the sky is falling
            else:
                LOGGER.error(f'Failed to deploy cloudformation: {err}')
                raise err

        except Exception as err:
            LOGGER.error(f'Failed to deploy cloudformation: {err}')
            raise err

    def _post_stack(self, api_name: str):
        """Create a stack for the Alarms"""

        LOGGER.info(f"Running {api_name} for {self.stack_name}")

        try:
            # Get api method from cloudformation boto3 client and run it
            getattr(CLIENT_FORMATION, api_name)(
                StackName=self.stack_name,
                TemplateURL=f"https://s3.amazonaws.com/{self.bucket}/{self.template_key}",
                Capabilities=[
                    "CAPABILITY_IAM",
                ],
                Tags=[
                    {
                        'Key': AWSService.TAG_STACK_ID_KEY,
                        'Value': AWSService.TAG_STACK_ID_VALUE
                    },
                    {
                        'Key': AWSService.TAG_OWNER,
                        'Value': self.stack_owner
                    },
                    {
                        'Key': AWSService.TAG_STACK_TYPE_KEY,
                        'Value': self.stack_type
                    }
                ]
            )

        except Exception as err:
            raise err
