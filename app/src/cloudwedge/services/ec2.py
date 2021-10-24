"""
EC2 for CloudWedge

Provides implementation details for ec2 service. It follows contract
outlined in cloudwedge.models.AWSService
"""

from os import environ
import boto3
import jmespath
from typing import List, Any, Dict, Optional

from cloudwedge.utils.logger import get_logger
from cloudwedge.utils.tags import TagsApi
from cloudwedge.models import AWSService, AWSResource

REGION = environ.get('REGION')

LOGGER = get_logger('cloudwedge.ec2')


# Model for Service, extending AWSResource
class EC2Resource(AWSResource):
    ec2State: str
    ec2DetailedMonitoring: str


# Class for Service
class EC2Service(AWSService):
    # Name of the service, must be unique
    name = "ec2"
    # Cloudwatch alarm service specific values
    cloudwatch_namespace = "AWS/EC2"
    cloudwatch_dashboard_section_title = "EC2"
    cloudwatch_dimension = "InstanceId"
    # Default metric to be used when metrics are not explicit in tags
    default_metrics = ["CPUUtilization",
                       "StatusCheckFailed_Instance", "StatusCheckFailed_System", "DiskWriteOps"]
    # Alarm defaults for the service, applied if metric default doesnt exist
    default_alarm_props = {
        'EvaluationPeriods': "5",
        'Statistic': "Average",
        'Period': "300",
        "ComparisonOperator": "GreaterThanOrEqualToThreshold"
        # "TreatMissingData": None
    }

    # List of supported metrics and default configurations
    supported_metrics = {
        'CPUUtilization': {
            'Threshold': "85",
        },
        'StatusCheckFailed_Instance': {
            'Threshold': "1",
            'EvaluationPeriods': "3"
        },
        'StatusCheckFailed_System': {
            'Threshold': "1",
            'EvaluationPeriods': "2"
        },
        'DiskReadOps': {
            'Threshold': "5000"
        },
        'DiskWriteOps': {
            'Threshold': "5000"
        },
        'NetworkIn': {
            'Threshold': "1000000"
        },
        'NetworkOut': {
            'Threshold': "1000000"
        }
    }

    # There are dashboard additions that can be added at the metric level
    override_dashboard_metric_properties = {
        'CPUUtilization': {
            "annotations": {
                "horizontal": [
                    {
                        "label": "High",
                        "value": 90
                    }
                ]
            }
        }
    }

    @staticmethod
    def get_default_resource_alarm_props(resource: EC2Resource) -> Dict[str, str]:
        """
        Get default alarm props based on the resource values
        """

        default_alarm_props = {}

        # If detailed monitoring is on, lower the period by default to 60
        if resource.get('ec2DetailedMonitoring') == "enabled":
            prop_period = "60"
            default_alarm_props['Period'] = "60"

        return default_alarm_props

    @staticmethod
    def validate_prop_period(value: str, resource: Optional[EC2Resource]) -> str:
        """
        Validate alarm property 'Period'
        """

        # Validate prop with base method (like calling super)
        validated_base_prop = AWSService.validate_prop_period(value, resource)

        # After validation, check its not below 300 if detailed monitoring is not on
        if int(validated_base_prop) < 300 and not resource.get('ec2DetailedMonitoring') == "enabled":
            # Fallback to default because we had an invalid override somewhere in the chain
            validated_base_prop = EC2Service.default_alarm_props['Period']

        return validated_base_prop

    @staticmethod
    def build_dashboard_widgets(resources: List[EC2Resource]) -> List[Any]:
        """
        Build dashboard widgets for the resources
        """

        # Get widgets with base method (like calling super)
        return AWSService.build_dashboard_widgets(EC2Service, resources)

    @ staticmethod
    def get_resources(session: boto3.session.Session) -> List[EC2Resource]:
        """
        Return all AWS EC2 instances within scope, based on the tags
        """

        try:
            instances: List[EC2Resource] = []

            # Get paginator for service
            paginator = (
                session.client('ec2')
                .get_paginator('describe_instances')
                .paginate(
                    Filters=[
                        # Filter for only resources that have cloudwedge tag
                        {'Name': f"tag:{AWSService.TAG_ACTIVE}",
                            'Values': ["true"]},
                        # Additionally, filter to only get instances that are on
                        {
                            'Name': "instance-state-name",
                            'Values': ["pending", "running"],
                        },
                    ]
                )
            )

            # Collect all instances
            for page_instances in paginator:
                for reservation in page_instances['Reservations']:
                    instances.extend(reservation['Instances'])

            # Get things in a neat ec2 resource object
            cleaned_resources: List[EC2Resource] = []

            for instance in instances:

                # Get values from instance details
                instance_id = instance['InstanceId']
                tags = instance.get('Tags')
                resource_owner = TagsApi.get_owner_from_tags(tags)
                resource_name = TagsApi.get_name_from_tags(tags)

                instance_state = instance.get('State', {}).get('Name', None)
                monitoring_state = instance.get(
                    'Monitoring', {}).get('State', None)

                # Setup EC2Resource values
                service = EC2Service.name
                resource_name = resource_name
                resource_id = instance_id
                resource_owner = resource_owner
                tags = tags
                ec2_state = instance_state
                ec2_detailed_monitoring = monitoring_state

                # Create EC2Resource
                clean_resource = EC2Resource(
                    service=service,
                    name=resource_name,
                    uniqueId=resource_id,
                    cloudwatchDimensionId=resource_id,
                    owner=resource_owner,
                    tags=tags,
                    ec2State=ec2_state,
                    ec2DetailedMonitoring=ec2_detailed_monitoring
                )

                # Add to collection
                cleaned_resources.append(clean_resource)

            return cleaned_resources

        except Exception as err:
            LOGGER.info(
                f"Failed to get instances information with error: {err}")
            raise err
