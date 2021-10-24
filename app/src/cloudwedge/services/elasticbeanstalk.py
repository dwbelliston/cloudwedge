"""
ElasticBeanstalk for CloudWedge

Provides implementation details for elasticbeanstalk service. It follows contract
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

LOGGER = get_logger("cloudwedge.elasticbeanstalk")


# Model for Service, extending AWSResource
class ElasticBeanstalkResource(AWSResource):
    pass

# Class for Service
class ElasticBeanstalkService(AWSService):
    # Name of the service, must be unique
    name = "elasticbeanstalk"
    # Cloudwatch alarm service specific values
    cloudwatch_namespace = "AWS/ElasticBeanstalk"
    cloudwatch_dashboard_section_title = "Elastic Beanstalk"
    cloudwatch_dimension = "EnvironmentName"
    # Default metric to be used when metrics are not explicit in tags
    default_metrics = ["ApplicationRequests2xx",
                       "ApplicationRequests3xx", "ApplicationRequests4xx", "ApplicationRequests5xx"]
    # Alarm defaults for the service, applied if metric default doesnt exist
    default_alarm_props = {
        'Statistic': "Average"
    }

    # List of supported metrics and default configurations
    supported_metrics = {
        'ApplicationRequests2xx' :{},
        'ApplicationRequests3xx' :{},
        'ApplicationRequests4xx' :{},
        'ApplicationRequests5xx' :{}
    }

    # There are dashboard additions that can be added at the metric level
    override_dashboard_metric_properties = {}

    @staticmethod
    def build_dashboard_widgets(resources: List[ElasticBeanstalkResource]) -> List[Any]:
        """
        Build dashboard widgets for the resources
        """

        # Get widgets with base method (like calling super)
        return AWSService.build_dashboard_widgets(ElasticBeanstalkService, resources)

    @ staticmethod
    def get_resources(session: boto3.session.Session) -> List[ElasticBeanstalkResource]:
        """
        Return all AWS ElasticBeanstalk resources within scope, based on the tags
        """

        try:
            # Get things in a neat elasticbeanstalk resource object
            cleaned_resources: List[ElasticBeanstalkResource] = []

            # Get paginator for service
            paginator = session.client('elasticbeanstalk').get_paginator(
                'describe_environments').paginate()

            # Collect all resources
            for page_resources in paginator:
                for environment in page_resources['Environments']:

                    # For each env, get the tags
                    env_resource_tags = session.client('elasticbeanstalk').list_tags_for_resource(
                        ResourceArn=environment['EnvironmentArn'])

                    env_tags = env_resource_tags['ResourceTags']

                    # If the active monitoring tag is on the instance, include in resource collection
                    # Stripping key so no whitespace mismatch
                    if any((tag['Key'].strip() == AWSService.TAG_ACTIVE and tag['Value'] == 'true') for tag in env_tags):
                        # This resource has opted in to cloudwedge

                        # Get values from tags if they exist
                        owner_from_tag = TagsApi.get_owner_from_tags(env_tags)
                        name_from_tag = TagsApi.get_name_from_tags(env_tags)
                        environment_id = environment['EnvironmentName']

                        # Setup ElasticBeanstalk values
                        service = ElasticBeanstalkService.name
                        resource_name = name_from_tag or environment_id
                        resource_id = environment_id
                        resource_owner = owner_from_tag
                        tags = env_tags

                        # Create ElasticBeanstalk
                        clean_resource = ElasticBeanstalkResource(
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
                f"Failed to get resources information with error: {err}")
            raise err
