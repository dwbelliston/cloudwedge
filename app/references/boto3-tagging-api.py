"""
Here is an implementation of the tagging api.

Decided not to use it because we may need additional information about resources and the tagging api
only returns arn and tags.

For instance, ec2 alarms are different if its detailed monitoring is on/off


"""




"""
GetResources

Get a list of resources for the supported services based on tags criteria
"""

import itertools
from typing import Dict, List

import boto3
from cloudwedge.models import AWSResource, AWSService
from cloudwedge.services import ServiceRegistry
from cloudwedge.utils.arnparse import arnparse
from cloudwedge.utils.logger import get_logger

LOGGER = get_logger('GetResources')


# Setup boto3 session
SESSION = boto3.session.Session()


class GetResources():
    def __init__(self):
        self.is_empty = True

    def run(self, event=None):
        """Run"""

        # Get all resources for all services
        resources = self._get_resources()

        # Organize resources by owner
        resources_by_owner = self._organize_by_owner(resources)

        output = {
            "event": event,
            "ownerResources": resources_by_owner,
            "isEmpty": self.is_empty
        }

        return output

    def _get_resources(self) -> Dict[str, List[AWSResource]]:

        # Tagging api
        client = SESSION.client('resourcegroupstaggingapi')

        response = client.get_resources(
            TagFilters=[
                {
                    'Key': AWSService.TAG_ACTIVE,
                    'Values': [
                        'true',
                    ]
                },
            ],
            # ResourcesPerPage=123,
            # TagsPerPage=123,
            ResourceTypeFilters=[
                'ec2:instance',
                'rds:db'
            ],
            IncludeComplianceDetails=False,
            ExcludeCompliantResources=False
        )

        services_resources: Dict[str, List[AWSResource]] = {}

        for resource in response['ResourceTagMappingList']:
            # {
            #     'ResourceARN': 'arn:aws:ec2:us-west-2:ACCOUNTID:instance/i-07c281f74d763f868',
            #     'Tags': [{'Key': 'Name', 'Value': 'artillery'}, {'Key': 'cloudwedge:alert:active', 'Value': 'true'}]
            # }

            # Parse arn to get values from it
            arn = arnparse(resource['ResourceARN'])

            # Pull values from arn
            service = arn.service
            resource_id = arn.resource_id

            # Get tags from resource
            tags = resource.get('Tags')

            # Find owner tag and return value if it exists, else fallback to default owner
            resource_owner = next((tag['Value'] for tag in tags if tag['Key'] ==
                                   AWSService.TAG_OWNER), AWSService.DEFAULT_OWNER)
            # Find name tag and return value if it exists, else use the resource_id from arn as name
            resource_name = next((tag['Value'] for tag in tags if tag['Key'] ==
                                  'Name'), resource_id)

            clean_resource = AWSResource(
                service=service, name=resource_name, uniqueId=resource_id, owner=resource_owner, tags=tags)

            # Set output with the service name
            services_resources.setdefault(
                clean_resource['service'], []
            ).append(clean_resource)

        return services_resources

        # # Read the resources for each service and collect together
        # resources: Dict[str, List[AWSResource]] = {}

        # # Get list of supported services
        # supported_services = ServiceRegistry.supported

        # # Get resources for each supported service
        # for service in supported_services: # [EC2Service, RDSService, etc..]
        #     # Get the services name
        #     service_name: str = service.name
        #     # Get the resources
        #     service_resources = service.get_resources(session=SESSION)

        #     # If we get any reasources for any service, toggle is_empty
        #     if self.is_empty and len(service_resources) > 0:
        #         self.is_empty = False

        #     # Set output with the service name
        #     resources.setdefault(
        #         service_name, service_resources
        #     )

        # return resources

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
