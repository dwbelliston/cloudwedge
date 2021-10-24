"""
AutoScalingGroup for CloudWedge

Provides implementation details for autoscalinggroup service. It follows contract
outlined in cloudwedge.models.AWSService
"""

from os import environ
from typing import Any, Dict, List, Optional

import boto3
import jmespath
from cloudwedge.models import AWSResource, AWSService
from cloudwedge.utils.logger import get_logger
from cloudwedge.utils.tags import TagsApi

REGION = environ.get("REGION")

LOGGER = get_logger("cloudwedge.autoscalinggroup")


# Model for Service, extending AWSResource
class AutoScalingGroupResource(AWSResource):
    status: str
    metrics_enabled: bool


# Class for Service
class AutoScalingGroupService(AWSService):
    # Name of the service, must be unique
    name = "autoscalinggroup"
    # Cloudwatch alarm service specific values
    cloudwatch_namespace = "AWS/EC2"
    cloudwatch_dashboard_section_title = "Autoscaling"
    cloudwatch_dimension = "AutoScalingGroupName"
    # Default metric to be used when metrics are not explicit in tags
    default_metrics = ["CPUUtilization", "NetworkIn", "NetworkOut"]
    # Alarm defaults for the service, applied if metric default doesnt exist
    default_alarm_props = {
        "EvaluationPeriods": "5",
        "Statistic": "Average",
        "Period": "300",
        "ComparisonOperator": "GreaterThanOrEqualToThreshold"
        # "TreatMissingData": None
    }

    # List of supported metrics and default configurations
    supported_metrics = {
        "CPUUtilization": {"Threshold": "85",},
        "StatusCheckFailed_Instance": {"Threshold": "1", "EvaluationPeriods": "3"},
        "StatusCheckFailed_System": {"Threshold": "1", "EvaluationPeriods": "2"},
        "DiskReadOps": {"Threshold": "5000"},
        "DiskWriteOps": {"Threshold": "5000"},
        "NetworkIn": {"Threshold": "1000000"},
        "NetworkOut": {"Threshold": "1000000"},
    }

    # There are dashboard additions that can be added at the metric level
    override_dashboard_metric_properties = {}

    @classmethod
    def build_dashboard_widgets(
        cls, resources: List[AutoScalingGroupResource]
    ) -> List[Any]:
        """
        Build dashboard widgets for the resources
        """

        # Build widgets for autoscaling
        asg_widgets = []

        for asg_resource in resources:

            widget_metric_network = cls._build_dashboard_widget_network(asg_resource)
            asg_widgets.append(widget_metric_network)

            # If the asg has autoscaling metrics on, make widget for that
            if asg_resource['metrics_enabled']:
                widget_metric_asg = cls._build_dashboard_widget_asg(asg_resource)
                asg_widgets.append(widget_metric_asg)

        # Get widgets with base method (like calling super)
        return AWSService.build_dashboard_widgets(
            AutoScalingGroupService, resources, asg_widgets
        )

    @classmethod
    def get_resources(
        cls, session: boto3.session.Session
    ) -> List[AutoScalingGroupResource]:
        """
        Return all AWS AutoScalingGroup resources within scope, based on the tags
        """

        try:
            # Get things in a neat autoscalinggroup resource object
            cleaned_resources: List[AutoScalingGroupResource] = []

            # Get paginator for service
            paginator = (
                session.client("autoscaling")
                .get_paginator("describe_auto_scaling_groups")
                .paginate()
            )

            # Collect all resources
            for page_resources in paginator:

                for asg in page_resources["AutoScalingGroups"]:

                    asg_tags = asg["Tags"]

                    # If the active monitoring tag is on the instance, include in resource collection,
                    # Stripping key so no whitespace mismatch
                    if any(
                        (
                            tag["Key"].strip() == AWSService.TAG_ACTIVE
                            and tag["Value"] == "true"
                        )
                        for tag in asg_tags
                    ):
                        # This resource has opted in to cloudwedge

                        # Get values from tags if they exist
                        owner_from_tag = TagsApi.get_owner_from_tags(asg_tags)
                        name_from_tag = TagsApi.get_name_from_tags(asg_tags)

                        # Setup AutoScalingGroup values
                        asg_id = asg["AutoScalingGroupARN"]
                        service = cls.name
                        resource_name = name_from_tag or asg_id
                        resource_name = asg["AutoScalingGroupName"]
                        resource_id = asg_id
                        resource_owner = owner_from_tag
                        tags = asg_tags
                        asg_metrics_enabled = asg["EnabledMetrics"]

                        # Create AutoScalingGroup
                        clean_resource = AutoScalingGroupResource(
                            service=service,
                            name=resource_name,
                            uniqueId=resource_id,
                            cloudwatchDimensionId=resource_name,
                            owner=resource_owner,
                            tags=tags,
                            metrics_enabled=asg_metrics_enabled,
                        )

                        # Add to collection
                        cleaned_resources.append(clean_resource)

            return cleaned_resources

        except Exception as err:
            LOGGER.info(f"Failed to get resources information with error: {err}")
            raise err

    @classmethod
    def _build_dashboard_widget_network(
        cls, resource: AutoScalingGroupResource
    ) -> Dict[str, Any]:
        """Build widget for network metrics"""

        widget_metric_properties = {
            "metrics": [
                [
                    {
                        "expression": "nIn+nOut",
                        "label": "All Network",
                        "id": "e1",
                        "region": REGION,
                        "color": "#d35400",
                    }
                ],
                [
                    "AWS/EC2",
                    "CPUUtilization",
                    "AutoScalingGroupName",
                    resource["cloudwatchDimensionId"],
                    {"yAxis": "right", "id": "m3", "color": "#95a5a6"},
                ],
                [".", "NetworkIn", ".", ".", {"id": "nIn", "color": "#f1c40f"}],
                [".", "NetworkOut", ".", ".", {"id": "nOut", "color": "#f39c12"}],
            ],
            "view": "timeSeries",
            "stacked": False,
            "region": REGION,
            "stat": "Average",
            "period": 300,
            "title": f"Autoscaling | {resource['name'] } | Network Vs CPU | AVG over 5 min",
            "yAxis": {
                "left": {"label": "Bytes", "min": 0, "showUnits": False},
                "right": {
                    "label": "CPU Utilization %",
                    "max": 100,
                    "showUnits": False,
                    "min": 0,
                },
            },
            "annotations": {
                "horizontal": [
                    {
                        "color": "#c0392b",
                        "label": "High CPU",
                        "value": 90,
                        "yAxis": "right",
                    },
                    {
                        "label": "10 gigabit/sec bandwidth",
                        "color": "#bdc3c7",
                        "value": 1250000000,
                    },
                    {
                        "label": "5 gigabit/sec bandwidth",
                        "color": "#bdc3c7",
                        "value": 625000000,
                    },
                ]
            },
        }

        widget_metric = {
            "type": "metric",
            "width": 24,
            "height": 6,
            "properties": widget_metric_properties,
        }

        return widget_metric

    @classmethod
    def _build_dashboard_widget_asg(
        cls, resource: AutoScalingGroupResource
    ) -> Dict[str, Any]:
        """Build widget for asg with metrics enabled"""

        widget_metric_properties = {
            "metrics": [
                [
                    "AWS/AutoScaling",
                    "GroupTotalInstances",
                    "AutoScalingGroupName",
                    resource["cloudwatchDimensionId"],
                    {"id": "m16", "yAxis": "left", "color": "#2980b9"},
                ],
                [
                    "AWS/EC2",
                    "CPUUtilization",
                    "AutoScalingGroupName",
                    resource["cloudwatchDimensionId"],
                    {"yAxis": "right", "id": "m3", "color": "#95a5a6"},
                ]
            ],
            "view": "timeSeries",
            "stacked": False,
            "region": REGION,
            "stat": "Average",
            "period": 300,
            "title": f"Autoscaling | {resource['name'] } | Instances vs CPU",
            "yAxis": {
                "left": {"label": "Total Count", "min": 0, "showUnits": False},
                "right": {
                    "label": "CPU Utilization %",
                    "max": 100,
                    "showUnits": False,
                    "min": 0,
                },
            },
            "annotations": {
                "horizontal": [
                    {
                        "color": "#c0392b",
                        "label": "High CPU",
                        "value": 90,
                        "yAxis": "right",
                    }
                ]
            },
        }

        widget_metric = {
            "type": "metric",
            "width": 24,
            "height": 6,
            "properties": widget_metric_properties,
        }

        return widget_metric
