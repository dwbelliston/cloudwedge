"""
ApiGateway for CloudWedge

Provides implementation details for apigateway service. It follows contract
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

LOGGER = get_logger("cloudwedge.apigateway")


# Model for Service, extending AWSResource
class ApiGatewayResource(AWSResource):
    pass

# Class for Service
class ApiGatewayService(AWSService):
    # Name of the service, must be unique
    name = "apigateway"
    # Cloudwatch alarm service specific values
    cloudwatch_namespace = "AWS/ApiGateway"
    cloudwatch_dashboard_section_title = "Api Gateway"
    cloudwatch_dimension = "EnvironmentName"
    # Default metric to be used when metrics are not explicit in tags
    default_metrics = ["Latency",
                       "IntegrationLatency", "5XXError", "4XXError"]
    # Alarm defaults for the service, applied if metric default doesnt exist
    default_alarm_props = {
        'Statistic': "Sum"
    }

    # List of supported metrics and default configurations
    supported_metrics = {
        'Latency' :{},
        'IntegrationLatency' :{},
        '5XXError' :{},
        '4XXError' :{}
    }

    # There are dashboard additions that can be added at the metric level
    override_dashboard_metric_properties = {}

    @staticmethod
    def build_dashboard_widgets(resources: List[ApiGatewayResource]) -> List[Any]:
        """
        Build dashboard widgets for the resources
        """

        # Get widgets with base method (like calling super)
        return AWSService.build_dashboard_widgets(ApiGatewayService, resources)

    @ staticmethod
    def get_resources(session: boto3.session.Session) -> List[ApiGatewayResource]:
        """
        Return all AWS ApiGateway resources within scope, based on the tags
        """

        try:
            # Get things in a neat apigateway resource object
            cleaned_resources: List[ApiGatewayResource] = []

            # Get paginator for service
            paginator = session.client('apigateway').get_paginator(
                'get_rest_apis').paginate()

            # Collect all resources
            for page_resources in paginator:
                for rest_api in page_resources['items']:

                    rest_api_tags = rest_api.get('tags', {})

                    # Api gateway returns tag as key value dict, convert it to standard format
                    # e.g. {'STAGE': 'prod', 'cloudwedge:active': 'true'}
                    converted_tags = TagsApi.convert_dict_to_tags(rest_api_tags)

                    # If the active monitoring tag is on the instance, include in resource collection
                    # Stripping key so no whitespace mismatch
                    if any((tag['Key'].strip() == AWSService.TAG_ACTIVE and tag['Value'] == 'true') for tag in converted_tags):
                        # This resource has opted in to cloudwedge

                        # Get values from tags if they exist
                        owner_from_tag = TagsApi.get_owner_from_tags(converted_tags)
                        name_from_tag = TagsApi.get_name_from_tags(converted_tags)
                        rest_api_name = rest_api['name']

                        # Setup ApiGateway values
                        service = ApiGatewayService.name
                        resource_name = name_from_tag or rest_api_name
                        resource_id = rest_api_name
                        resource_owner = owner_from_tag
                        tags = converted_tags

                        # Create ApiGateway
                        clean_resource = ApiGatewayResource(
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
