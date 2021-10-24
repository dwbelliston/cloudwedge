import hashlib
from botocore.exceptions import ClientError

from configuration.logger import LOGGER
from configuration import env as ENV
from lib.alarm_instance import Ec2Instance, RdsInstance
from lib.dashboard import DashboardMaker


class AlarmStackMaker(object):
    def __init__(self, session, service, owner, instances):
        self.spoke_session = session
        self.service = service
        self.owner = owner
        self.instances = instances
        self.template = ''
        self.stack_name = f"{ENV.SPOKE_STACK_TAG_VALUE_FOR_IDENTIFICATION}-{owner}-{service}-stack"
        self.dashboard_values = {}

    def make_yaml(self):
        # Build yaml for the service
        make_alarms_service = getattr(self, f'_make_alarms_{self.service}')
        alarm_yaml = make_alarms_service()

        make_dashboard_service = getattr(self, f'_make_dashboards_{self.service}')
        dashboad_yaml = make_dashboard_service()

        # Wrap alarm yaml in full template
        self.template = self._complete_template(alarm_yaml, dashboad_yaml)

    def deploy_stack(self):
        LOGGER.info(f"Deploying generated template for stack: {self.stack_name}")

        try:
            self._post_stack('update_stack')
            LOGGER.info(f'Updated Stack: {self.stack_name}')

        except ClientError as err:
            if 'No updates are to be performed' in err.response['Error']['Message']:
                LOGGER.info(f"No updates are to to be performed.")
            elif 'does not exist' in err.response['Error']['Message']:
                # If it failed on update because it doesnt exist, create instead
                try:
                    self._post_stack('create_stack')
                    LOGGER.info(f"Created Stack: {self.stack_name}")

                except ClientError as err:
                    LOGGER.error(f"Failed to create Stack: {err}")
                    raise err
            elif any(x in err.response['Error']['Message'] for x in ['UPDATE_IN_PROGRESS', 'CREATE_IN_PROGRESS']):
                # If it failed on update its already being updated, lets take our chance the update in progress is good
                # When an RDS tag is edited, it deletes the tag first which fires an event. Then it updates, another event :)
                LOGGER.info(
                    f"Stack update is in progress, allowing that stack to proceed. Aborting error free.")
            else:
                LOGGER.error(f"Failed to deploy cloudformation: {err}")
                raise err
        except Exception as err:
            LOGGER.error(f"Failed to deploy cloudformation: {err}")
            raise err

    def _post_stack(self, api_name):
        '''Create a stack for the Alarms'''
        LOGGER.info(f"Running {api_name} on {self.stack_name}")
        try:
            getattr(self.spoke_session.client('cloudformation'), api_name)(
                StackName=self.stack_name,
                TemplateBody=self.template,
                Capabilities=[
                    'CAPABILITY_IAM',
                ],
                Tags=[
                    {
                        'Key': ENV.SPOKE_STACK_TAG_NAME_FOR_IDENTIFICATION,
                        'Value': ENV.SPOKE_STACK_TAG_VALUE_FOR_IDENTIFICATION
                    },
                    {
                        'Key': ENV.SPOKE_STACK_TAG_NAME_FOR_OWNER,
                        'Value': self.owner.lower()
                    },
                    {
                        'Key': ENV.SPOKE_STACK_TAG_NAME_FOR_SERVICE,
                        'Value': self.service.lower()
                    }
                ]
            )
        except Exception as err:
            raise err


    def _wait_stack(self, waiter_name):
        '''Wait for stack'''
        LOGGER.info(f"Running waiter {waiter_name} on {self.stack_name}")

        try:
            waiter = self.spoke_session.client(
                'cloudformation').get_waiter(waiter_name)
            waiter.wait(StackName=self.stack_name)
        except Exception as err:
            raise err
