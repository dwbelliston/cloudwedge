"""
ECS for CloudWedge

Provides implementation details for ecs service. It follows contract
outlined in cloudwedge.models.AWSService

https://www.bluematador.com/blog/how-to-monitor-amazon-ecs-with-cloudwatch
https://www.datadoghq.com/blog/amazon-ecs-metrics/
"""

from os import environ
import boto3
import jmespath
from typing import List, Any, Dict, Optional

from cloudwedge.utils.logger import get_logger
from cloudwedge.utils.tags import TagsApi
from cloudwedge.models import AWSService, AWSResource

REGION = environ.get('REGION')

LOGGER = get_logger('cloudwedge.ecs')


# Model for Service, extending AWSResource
class ECSResource(AWSResource):
    pass


# Class for Service
class ECSService(AWSService):
    # Name of the service, must be unique
    name = "ecs"
    # Cloudwatch alarm service specific values
    cloudwatch_namespace = "AWS/ECS"
    cloudwatch_dashboard_section_title = "ECS"
    cloudwatch_dimension = "ClusterName"
    # Default metric to be used when metrics are not explicit in tags
    default_metrics = ["CPUUtilization", "MemoryUtilization"]
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
        'MemoryUtilization': {
            'Threshold': "70",
        },
        'CPUReservation': {},
        'MemoryReservation': {},
        'GPUReservation': {}
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
    def build_dashboard_widgets(resources: List[ECSResource]) -> List[Any]:
        """
        Build dashboard widgets for the resources
        """

        # Get widgets with base method (like calling super)
        return AWSService.build_dashboard_widgets(ECSService, resources)

    @ staticmethod
    def get_resources(session: boto3.session.Session) -> List[ECSResource]:
        """
        Return all AWS ECS clusters within scope, based on the tags
        """

        try:
            cleaned_resources: List[ECSResource] = []

            # Get paginator for service
            paginator = (
                session.client('ecs')
                .get_paginator('list_clusters')
                .paginate()
            )

            # Collect all clusters
            for page_clusters in paginator:
                # Get clusters details
                res_clusters = session.client('ecs').describe_clusters(
                    clusters=page_clusters['clusterArns'],
                    include=['TAGS']
                )

                for cluster in res_clusters['clusters']:

                    cluster_tags = cluster.get('tags', {})

                    converted_tags = TagsApi.convert_lowercase_tags_keys(cluster_tags)

                    if any((tag['Key'].strip() == AWSService.TAG_ACTIVE and tag['Value'] == 'true') for tag in converted_tags):
                        # This resource has opted in to cloudwedge

                        # Get values from tags if they exist
                        owner_from_tag = TagsApi.get_owner_from_tags(converted_tags)
                        name_from_tag = TagsApi.get_name_from_tags(converted_tags)
                        cluster_name = cluster['clusterName']

                        # Setup ECS values
                        service = ECSService.name
                        resource_name = name_from_tag or cluster_name
                        resource_id = cluster_name
                        resource_owner = owner_from_tag
                        tags = converted_tags

                        # Create ECS
                        clean_resource = ECSResource(
                            service=service,
                            name=resource_name,
                            uniqueId=resource_id,
                            cloudwatchDimensionId=resource_id,
                            owner=resource_owner,
                            tags=tags
                        )

                        # Add to collection
                        cleaned_resources.append(clean_resource)

            return cleaned_resources

        except Exception as err:
            LOGGER.info(
                f"Failed to get clusters information with error: {err}")
            raise err
