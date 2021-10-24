"""
AlarmsFactory

AlarmsFactory receives a group of resources and builds cloudformation
alarms stack templates for them.
"""
import hashlib
import json
import time
from os import environ
from typing import Dict, List

from cloudwedge.models import AWSResource
from cloudwedge.services import ServiceRegistry
from cloudwedge.utils.logger import get_logger
from cloudwedge.utils.s3 import s3_save_object

from resource_alarm_factory import ResourceAlarmFactory

PRIVATE_ASSETS_BUCKET = environ.get('PRIVATE_ASSETS_BUCKET')

LOGGER = get_logger('AlarmsFactory')


class AlarmsFactory():
    def __init__(self, session, owner, resources: Dict[str, List[AWSResource]]):
        LOGGER.info(f'🚨🏭 AlarmsFactory: {owner}')

        # Track the session provided
        self.session = session
        # Owner of the resource
        self.owner = owner
        # Collection of resources, grouped by service
        self.resources = resources

        # Hold the templates that are created
        self.alarms = {
            'stackName': f'cloudwedge-autogen-{self.owner}-alarms-stack',
            's3TemplateKey': None,
            'template': {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Description": f"CloudWedge Alarm Stack for all resources that have owner {self.owner}. This stack is created dynamically by CloudWedge.",
                "Resources": {}
            }
        }

    def get_stack_details(self):
        """Return stack details"""

        return {
            'stackName': self.alarms['stackName'],
            's3TemplateKey': self.alarms['s3TemplateKey'],
            'stackType': 'alarms',
            'stackOwner': self.owner
        }

    def build(self):
        """Build alarms template for all the resources"""

        # Reset the template
        self.alarms['template']['Resources'] = {}
        self.alarms['s3TemplateKey'] = None

        # For each resource in the service group
        for service_name, service_resources in self.resources.items():
            # Get the service class from the registry
            service = ServiceRegistry.get_service(service_name)

            # Build json template for the resource
            for resource in service_resources:
                resource_alarm_factory = ResourceAlarmFactory(resource=resource, service=service)
                # Build all the alarms for the resource
                resource_alarms_template = resource_alarm_factory.build()
                # Add alarms for this resource to the templates Resources section
                self.alarms['template']['Resources'].update(
                    resource_alarms_template)

        # Save the template to s3
        self._save_stack(self.alarms)

        # # LOCAL: write template
        # self._write_template(self.alarms['template'])


    def _save_stack(self, stack):
        """Save the stack to s3 and return the key"""
        # Convert template to string
        s3_content = json.dumps(stack['template'])

        # Make s3 key for this stack
        # s3_key = f'templates/{stack["stackName"]}/template.json'
        s3_key = f'templates/{stack["stackName"]}/{int(time.time())}/template.json'

        # Save the template
        saved_key = s3_save_object(session=self.session, bucket=PRIVATE_ASSETS_BUCKET, key=s3_key,
                              content=s3_content)

        self.alarms['s3TemplateKey'] = saved_key

    # @staticmethod
    # def _write_template(cf_template):
    #     """Local Only: Test function for running locally to write formation to file for review"""
    #     TEMPLATE_NAME = f"/tmp/EXAMPLE_OUTPUT.yaml"
    #     with open(TEMPLATE_NAME, 'w') as f:
    #         f.write(json.dumps(cf_template))
