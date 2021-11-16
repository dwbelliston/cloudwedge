"""
StateMachine for CloudWedge

Provides implementation details for statemachine service. It follows contract
outlined in cloudwedge.models.AWSService
"""

from os import environ
from typing import Any, List, Tuple

import boto3

from cloudwedge.models import AWSResource, AWSService
from cloudwedge.utils.logger import get_logger
from cloudwedge.utils.tags import TagsApi

REGION = environ.get('REGION')

LOGGER = get_logger("cloudwedge.statemachine")


# Model for Service, extending AWSResource
class StateMachineResource(AWSResource):
    pass

# Class for Service
class StateMachineService(AWSService):
    # Name of the service, must be unique
    name = "statemachine"
    # Cloudwatch alarm service specific values
    cloudwatch_namespace = "AWS/States"
    cloudwatch_dashboard_section_title = "States"
    cloudwatch_dimension = "StateMachineArn"

    # Default metric to be used when metrics are not explicit in tags
    default_metrics = ["ExecutionsFailed",
                        "ExecutionThrottled",
                        "ExecutionTime"]

    default_dashboard_metrics = ["ExecutionTime"]
    # Alarm defaults for the service, applied if metric default doesnt exist
    default_alarm_props = {
        'Statistic': "Sum"
    }

    # List of supported metrics and default configurations
    supported_metrics = {
        'ExecutionsStarted': {},
        'ExecutionThrottled': {},
        'ExecutionsAborted': {},
        'ExecutionsSucceeded': {},
        'ExecutionsFailed': {},
        'ExecutionsTimedOut': {},
        'ExecutionTime': {}
    }

    # There are dashboard additions that can be added at the metric level
    override_dashboard_metric_properties = {}

    # There are dashboard additions that can be added at the metric level
    override_dashboard_widget_properties = {
        'ExecutionTime': {
            'width': 24,
            'height': 6
        }
    }

    @staticmethod
    def build_dashboard_widgets(resources: List[StateMachineResource]) -> List[Any]:
        """
        Build dashboard widgets for the resources
        """

        # Get widgets with base method (like calling super)
        return AWSService.build_dashboard_widgets(StateMachineService, resources, is_group_resources=False)

    @staticmethod
    def build_dashboard_widgets_byresource_extra(resource: StateMachineResource) -> Tuple[List[Any], List[Any]]:
        """
        Build extra dashboard widgets for the resource
        """

        front_widgets = []
        back_widgets = []

        front_widgets = [
            {
                "height": 4,
                "width": 6,
                "type": "metric",
                "properties": {
                    "metrics": [
                        [ { "expression": "m1-m2-m3-m4-m5-m6", "label": "Running", "id": "e3", "period": 86400, "region": "us-west-2" } ],
                        [ { "expression": "m1/m5", "label": "Success Rate", "id": "e1", "yAxis": "left", "period": 86400, "region": "us-west-2", "visible": False } ],
                        [ "AWS/States", "ExecutionsStarted", "StateMachineArn", resource['cloudwatchDimensionId'], { "id": "m1", "label": "Started Today", "visible": False } ],
                        [ ".", "ExecutionsTimedOut", ".", ".", { "id": "m2", "visible": False } ],
                        [ ".", "ExecutionThrottled", ".", ".", { "id": "m3", "visible": False } ],
                        [ ".", "ExecutionsAborted", ".", ".", { "id": "m4", "visible": False } ],
                        [ ".", "ExecutionsSucceeded", ".", ".", { "id": "m5", "visible": False } ],
                        [ ".", "ExecutionsFailed", ".", ".", { "id": "m6", "visible": False } ]
                    ],
                    "view": "singleValue",
                    "region": REGION,
                    "setPeriodToTimeRange": False,
                    "stat": "Sum",
                    "period": 86400,
                    "title": "Status"
                }
            },
            {
                "height": 4,
                "width": 12,
                "type": "metric",
                "properties": {
                    "metrics": [
                        [ { "expression": "m1-m2-m3-m4-m5-m6", "label": "Running", "id": "e3", "period": 86400, "region": "us-west-2", "visible": False } ],
                        [ { "expression": "(m5/m1)*100", "label": "Success Rate", "id": "e1", "yAxis": "left", "period": 86400, "region": "us-west-2", "color": "#c7c7c7" } ],
                        [ { "expression": "FLOOR(METRICS())", "label": "Expression2", "id": "e2", "visible": False, "color": "#1f77b4" } ],
                        [ "AWS/States", "ExecutionsStarted", "StateMachineArn", resource['cloudwatchDimensionId'], { "id": "m1", "label": "Started", "color": "#1f77b4", "visible": False } ],
                        [ ".", "ExecutionsTimedOut", ".", ".", { "id": "m2", "visible": False } ],
                        [ ".", "ExecutionThrottled", ".", ".", { "id": "m3", "visible": False } ],
                        [ ".", "ExecutionsAborted", ".", ".", { "id": "m4", "visible": False } ],
                        [ ".", "ExecutionsSucceeded", ".", ".", { "id": "m5", "color": "#2ca02c", "label": "Succeeded" } ],
                        [ ".", "ExecutionsFailed", ".", ".", { "id": "m6", "label": "Failed", "color": "#d62728" } ]
                    ],
                    "view": "singleValue",
                    "region": REGION,
                    "stat": "Sum",
                    "setPeriodToTimeRange": False,
                    "period": 86400,
                    "title": "Activity Last 24 hrs"
                }
            },
            {
                "height": 4,
                "width": 6,
                "type": "metric",
                "properties": {
                    "metrics": [
                        [ "AWS/States", "ExecutionsTimedOut", "StateMachineArn", resource['cloudwatchDimensionId'] ],
                        [ ".", "ExecutionThrottled", ".", "." ],
                        [ ".", "ExecutionsAborted", ".", "." ],
                        [ ".", "ExecutionsSucceeded", ".", "." ],
                        [ ".", "ExecutionsFailed", ".", "." ]
                    ],
                    "view": "pie",
                    "region": REGION,
                    "stat": "Sum",
                    "period": 300,
                    "title": "Execution Results",
                    "legend": {
                        "position": "right"
                    },
                    "labels": {
                        "visible": False
                    },
                    "stacked": False,
                    "setPeriodToTimeRange": True
                }
            },
        ]

        return front_widgets, back_widgets

    @ staticmethod
    def get_resources(session: boto3.session.Session) -> List[StateMachineResource]:
        """
        Return all AWS StateMachine resources within scope, based on the tags
        """

        try:

            # Get things in a neat statemachine resource object
            cleaned_resources: List[StateMachineResource] = []

            # Get paginator for service
            paginator = session.client('stepfunctions').get_paginator(
                'list_state_machines').paginate()

            # Collect all resources
            for page_resources in paginator:
                for state_machine in page_resources['stateMachines']:

                    state_arn = state_machine['stateMachineArn']

                    # For each state, get the tags
                    states_resource_tags = session.client('stepfunctions').list_tags_for_resource(
                        resourceArn=state_arn)

                    states_tags = states_resource_tags['tags']

                    # Keys for the tags are 'key' and 'value' so convert that to capitalize
                    converted_tags = TagsApi.convert_lowercase_tags_keys(
                        states_tags)

                    # If the active monitoring tag is on the instance, include in resource collection
                    # Stripping key so no whitespace mismatch
                    if any((tag['Key'].strip() == AWSService.TAG_ACTIVE and tag['Value'] == 'true') for tag in converted_tags):
                        # This resource has opted in to cloudwedge

                        # Get values from tags if they exist
                        owner_from_tag = TagsApi.get_owner_from_tags(converted_tags)
                        name_from_tag = TagsApi.get_name_from_tags(converted_tags)
                        state_name = state_machine['name']

                        # Setup StateMachine values
                        service = StateMachineService.name
                        resource_name = name_from_tag or state_name
                        resource_id = state_arn
                        resource_owner = owner_from_tag
                        tags = converted_tags

                        # Create StateMachine
                        clean_resource = StateMachineResource(
                            service=service,
                            name=resource_name,
                            uniqueId=resource_name,
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
