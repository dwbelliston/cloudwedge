"""
DeployStack

Deploys the stack using the template referenced by
the s3 key input.
"""

import itertools
from os import environ
from typing import Dict, List

from cloudwedge.utils.logger import get_logger
from cloudwedge.utils.sts import get_spoke_session

from stack_shipper import StackShipper

PRIVATE_ASSETS_BUCKET = environ.get('PRIVATE_ASSETS_BUCKET')

LOGGER = get_logger('DeployStack')

# Setup boto3 session
SESSION = None


class DeployStack():
    def __init__(self, target_account_id=None, event=None):

        # Pull values off event
        self.target_account_id = target_account_id
        self.stack_name = event['stackName']
        self.s3_template_key = event['s3TemplateKey']
        self.stack_type = event['stackType']
        self.stack_owner = event['stackOwner']

    def run(self):
        """Run"""

        global SESSION

        if not SESSION:
            SESSION = get_spoke_session(self.target_account_id)

        output = {
            'inProgress': True,
            'stackName': self.stack_name,
            'waitAttempts': 0
        }

        StackShipper(
                     session=SESSION,
                     s3_bucket=PRIVATE_ASSETS_BUCKET,
                     s3_key=self.s3_template_key,
                     stack_type=self.stack_type,
                     stack_owner=self.stack_owner,
                     stack_name=self.stack_name).ship()

        return output
