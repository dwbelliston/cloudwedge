"""
RDS for CloudWedge

Provides implementation details for rds service. It follows contract
outlined in cloudwedge.models.AWSService
"""

import os
from typing import Any, Dict, List

import boto3
import jmespath

from cloudwedge.models import AWSResource, AWSService
from cloudwedge.utils.logger import get_logger
from cloudwedge.utils.tags import TagsApi

LOGGER = get_logger('cloudwedge.rds')


# Model for Service, extending AWSResource
class RDSResource(AWSResource):
    rdsEngine: str
    rdsDBInstanceArn: str


# Class for Service
class RDSService(AWSService):
    # Name of the service, must be unique
    name = "rds"
    # Cloudwatch alarm service specific values
    cloudwatch_namespace = "AWS/RDS"
    cloudwatch_dashboard_section_title = "RDS"
    cloudwatch_dimension = "DBInstanceIdentifier"
    # Default metric to be used when metrics are not explicit in tags
    default_metrics = ["CPUUtilization", "FreeableMemory", "FreeStorageSpace"]
    # Alarm defaults for the service, applied if metric default doesnt exist
    default_alarm_props = {
        'EvaluationPeriods': 15,
        'Statistic': "Average",
        'Period': 60
        # "TreatMissingData": None,
        # "ComparisonOperator": "GreaterThanOrEqualToThreshold"
    }
    # List of supported metrics and default configurations
    supported_metrics = {
        'CPUUtilization': {
            'Threshold': 90,
            'TreatMissingData': "breaching",
            'ComparisonOperator': "GreaterThanOrEqualToThreshold"
        },
        'FreeableMemory': {
            'Threshold': 100000000,
            'ComparisonOperator': "LessThanOrEqualToThreshold"
        },
        'FreeStorageSpace': {
            'Threshold': 500000000,
            'ComparisonOperator': "LessThanOrEqualToThreshold"
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
    def build_dashboard_widgets(resources: List[RDSResource]) -> List[Any]:
        """
        Build dashboard widgets for the resources
        """

        # Get widgets with base method (like calling super)
        return AWSService.build_dashboard_widgets(RDSService, resources)

    @staticmethod
    def get_resources(session: boto3.session.Session) -> List[RDSResource]:
        """
        Return all AWS RDS instances within scope, based on the tags
        """

        try:
            # Collect resources
            cleaned_resources = []

            # Get paginator for rds instances
            paginator = session.client('rds').get_paginator(
                'describe_db_instances').paginate()

            for page_db_instances in paginator:
                # In each paginator, loop through the instances returned for the page
                for db_instance in page_db_instances['DBInstances']:

                    # For each db, get the tags on the instance
                    db_instance_tags = session.client('rds').list_tags_for_resource(
                        ResourceName=db_instance['DBInstanceArn'])

                    # e.g. [{'Key': 'notifications', 'Value': 'true'}]
                    db_tags = db_instance_tags['TagList']

                    # If the active monitoring tag is on the instance, include in resource collection
                    # Stripping key so no whitespace mismatch
                    if any((tag['Key'].strip() == AWSService.TAG_ACTIVE and tag['Value'] == 'true') for tag in db_tags):
                        # This resource has opted in to cloudwedge

                        # Get values from tags if they exist
                        owner_from_tag = TagsApi.get_owner_from_tags(db_tags)
                        name_from_tag = TagsApi.get_name_from_tags(db_tags)
                        database_id = db_instance['DBInstanceIdentifier']

                        # Setup RDSResource values
                        service = RDSService.name
                        resource_name = name_from_tag or database_id
                        resource_id = database_id
                        resource_owner = owner_from_tag
                        tags = db_tags
                        rds_engine = db_instance['Engine']
                        rds_db_arn = db_instance['DBInstanceArn']

                        # Create RDSResource
                        clean_resource = RDSResource(
                            service=service,
                            name=resource_name,
                            uniqueId=resource_id,
                            cloudwatchDimensionId=resource_id,
                            owner=resource_owner,
                            tags=tags,
                            rdsEngine=rds_engine,
                            rdsDBInstanceArn=rds_db_arn
                        )

                        # Add to collection
                        cleaned_resources.append(clean_resource)

            return cleaned_resources

        except Exception as err:
            LOGGER.info(
                f"Failed to get instances information with error: {err}")
            raise err
