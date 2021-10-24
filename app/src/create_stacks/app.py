"""
CreateStacks

Takes resources and creates a cloudformation template that includes
cloud watch alarms for each of the resources grouped by the owner.
Then saves the template to s3.
"""

import itertools
from typing import Dict, List

from cloudwedge.utils.logger import get_logger
from cloudwedge.utils.sts import get_spoke_session

from alarms_factory import AlarmsFactory
from dashboard_factory import DashboardFactory

LOGGER = get_logger('CreateStacks')

SESSION = None


class CreateStacks():
    def __init__(self, target_account_id):
        self.target_account_id = target_account_id

    def run(self, event=None):
        """Run"""

        global SESSION

        if not SESSION:
            SESSION = get_spoke_session(self.target_account_id)

        output = {
            'stacks': [],
            'targetAccountId': self.target_account_id
        }

        owner_resources = event['ownerResources']

        # Build out alarms cloud formation for each owner
        for owner, owner_resources in owner_resources.items():
            # Build stacks for owner
            stacks_details = self._create_stacks(owner, owner_resources)

            # Add stack to list of stacks that were created
            output['stacks'].extend(stacks_details)

        return output

    def _create_stacks(self, owner_name: str, owner_resources) -> List[Dict[str, str]]:
        """
        Create stack based on owner name
        Include every service and its resources
        """

        stacks = []

        # Setup stack factory for this owners set of resources
        alarms = AlarmsFactory(SESSION, owner_name, owner_resources)
        # Build the alarms template
        alarms.build()
        # Get details on what was created for tracking
        alarm_stack_details = alarms.get_stack_details()
        # Add account id to details
        alarm_stack_details['targetAccountId'] = self.target_account_id
        stacks.append(alarm_stack_details)
        LOGGER.info(f"Alarm Stack: {alarm_stack_details}")

        # Setup stack factory for this owners set of resources
        dashboard = DashboardFactory(SESSION, owner_name, owner_resources)
        # Build the dashboard template
        dashboard.build()
        # Get details on what was created for tracking
        dashboard_stack_details = dashboard.get_stack_details()
        # Add account id to details
        dashboard_stack_details['targetAccountId'] = self.target_account_id
        stacks.append(dashboard_stack_details)
        LOGGER.info(f"Dashboard Stack: {dashboard_stack_details}")

        return stacks
