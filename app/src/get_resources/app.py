"""
GetResources

Get a list of resources for the supported services based on tags criteria
"""

import itertools
from typing import Dict, List

from cloudwedge.models import AWSResource
from cloudwedge.services import ServiceRegistry
from cloudwedge.utils.logger import get_logger
from cloudwedge.utils.sts import get_spoke_session

LOGGER = get_logger('GetResources')

SESSION = None

class GetResources():
    def __init__(self, target_account_id):
        self.is_empty = True
        self.target_account_id = target_account_id

    def run(self, event=None):
        """Run"""

        global SESSION

        if not SESSION:
            SESSION = get_spoke_session(self.target_account_id)

        # Get all resources for all services
        resources = self._get_resources()

        # Organize resources by owner
        resources_by_owner = self._organize_by_owner(resources)

        output = {
            "event": event,
            "targetAccountId": self.target_account_id,
            "ownerResources": resources_by_owner,
            "isEmpty": self.is_empty
        }

        return output

    def _get_resources(self):
        # Read the resources for each service and collect together
        resources: Dict[str, List[AWSResource]] = {}

        # Get list of supported services
        supported_services = ServiceRegistry.supported

        # Get resources for each supported service
        for service in supported_services:  # [EC2Service, RDSService, etc..]

            # Get the services name
            service_name: str = service.name

            # Get the resources
            service_resources = service.get_resources(session=SESSION)


            # If we get any resources for any service, toggle is_empty
            if self.is_empty and len(service_resources) > 0:
                self.is_empty = False

            # Set output with the service name
            resources.setdefault(
                service_name, service_resources
            )

        return resources

    def _organize_by_owner(self, resources: Dict[str, List[AWSResource]]):
        """
            Parameters
                resources:
                    {
                        "ec2": [Resources with multiple owners],
                        "rds": [Resources with multiple owners],
                    }

            Returns:
                {
                    'owner1': {
                        'ec2': [LIST],
                        'rds': [LIST]
                    },
                    'owner2': {
                        'ec2': [LIST],
                        'rds': [LIST]
                    }
                }

        """
        try:
            owners = {}

            # Loop over each service and organize by owner
            for service_name, resources in resources.items():
                # Sort the resources by the owner key
                sorted_items = sorted(
                    resources, key=lambda x: x['owner'].lower())

                # Group the resources by the owner
                for owner_name, group in itertools.groupby(sorted_items, key=lambda x: x['owner'].lower()):
                    # Add owner to output
                    owners.setdefault(owner_name, {})
                    # Add this services resources to the owner
                    owners[owner_name].setdefault(service_name, list(group))

            return owners

        except Exception as err:
            raise err
