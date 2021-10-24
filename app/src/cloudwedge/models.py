import math
from abc import abstractmethod
from os import environ
from typing import Any, Dict, List, Optional, Tuple, TypedDict

import boto3
from cloudwedge.utils.logger import get_logger

REGION = environ.get('REGION')

LOGGER = get_logger("cloudwedge.models")

class AWSTag(TypedDict):
    Key: str
    Value: str


class AWSResource(TypedDict):
    service: str
    name: str
    uniqueId: str
    cloudwatchDimensionId: str
    owner: str
    tags: List[AWSTag]

# class AWSResource(object):
#     service: str
#     name: str
#     uniqueId: str
#     owner: str
#     tags: List[AWSTag]

#     def __init__(self, service, name, uniqueId, owner, tags):
#         self.service = service
#         self.name = name
#         self.uniqueId = uniqueId
#         self.owner = owner
#         self.tags = tags


class AWSService():
    # Properties that the extending service needs to implement
    name: str
    cloudwatch_namespace: str
    cloudwatch_dimension: str
    cloudwatch_dashboard_section_title: str
    default_metrics: Dict[str, Dict[str, str]]
    default_dashboard_metrics: Dict[str, Dict[str, str]]
    default_alarm_props: Dict[str, str]
    supported_metrics: Dict[str, Dict[str, str]]
    override_dashboard_metrics_options: Dict[str, Any] = {}
    override_dashboard_metric_properties: Dict[str, Any]
    override_dashboard_widget_properties: Dict[str, Any] = {}

    # CloudWedge root tags
    TAG_ACTIVE: Optional[str] = "cloudwedge:active"
    TAG_OWNER: Optional[str] = "cloudwedge:owner"
    TAG_LEVEL: Optional[str] = "cloudwedge:level"
    # CloudWedge metrics tags
    TAG_METRICS: str = "cloudwedge:metrics"
    TAG_METRICS_CRITICAL: str = "cloudwedge:metrics:critical"
    TAG_METRICS_HIGH: str = "cloudwedge:metrics:high"
    TAG_METRICS_MEDIUM: str = "cloudwedge:metrics:medium"
    TAG_METRICS_LOW: str = "cloudwedge:metrics:low"
    # CloudWedge alarm tags
    TAG_ALARM_PROP_PREFIX: str = "cloudwedge:alarm:prop:"
    TAG_ALARM_METRIC_PREFIX: str = "cloudwedge:alarm:metric:"
    # CloudWedge stack tags
    TAG_STACK_ID_KEY: str = "cloudwedge:stack"
    TAG_STACK_ID_VALUE: str = "true"
    TAG_STACK_TYPE_KEY: str = "cloudwedge:type"

    # Defaults
    DEFAULT_OWNER: str = "cloudwedge"
    DEFAULT_LEVEL: str = "medium"
    SUPPORTED_ALERT_LEVELS: List[str] = ["critical", "high", "medium", "low"]
    SUPPORTED_ALARM_PROPS: List[str] = [
        "Statistic", "Period", "TreatMissingData", "EvaluationPeriods", "Threshold", "ComparisonOperator"]
    ALARM_TARGET_SNS: str = environ.get("ALARM_ACTION_TARGET_TOPIC_ARN")
    USER_TARGET_SNS: str = environ.get("USER_TARGET_TOPIC_ARN")

    # Alarm Description keys
    # these are used to create the alarm description e.g. Resource=1s-dustin-stress Metric=CPUUtilization Level=medium Type=AWS/EC2 Owner=cloudwedge
    ALARM_DESCRIPTION_KEY_RESOURCE: str = "Resource"
    ALARM_DESCRIPTION_KEY_METRIC: str = "Metric"
    ALARM_DESCRIPTION_KEY_LEVEL: str = "Level"
    ALARM_DESCRIPTION_KEY_OWNER: str = "Owner"
    ALARM_DESCRIPTION_KEY_TYPE: str = "Type"


    @abstractmethod
    def get_resources(session: boto3.session.Session) -> List[AWSResource]:
        raise NotImplementedError

    @abstractmethod
    def get_default_resource_alarm_props(resource: AWSResource) -> Dict[str, str]:
        # The services can override this function if need to add in defaults
        return {}

    # @abstractmethod
    # def build_dashboard_widgets(resources: List[AWSResource]):
    #     raise NotImplementedError

    @staticmethod
    def _roundup(value: int, multiple: int = 60):
        return int(math.ceil(value / multiple)) * multiple

    def validate_prop_period(value: str, resource: Optional[AWSResource]) -> str:
        """Validate the Period property"""

        validated_prop = None

        # Check it is 10, 30 or multiple of 60
        # https://docs.aws.amazon.com/AmazonCloudWatch/latest/APIReference/API_PutMetricAlarm.html


        # Convert to int
        try:
            value_as_int = int(value)

            # Only a period greater than 60s is supported for metrics in the "AWS/" namespaces
            # # If less than 10, round up to 10
            # if value_as_int <= 10:
            #     validated_prop = "10"
            # # If less than 30, round up to 30
            # if value_as_int <= 30:
            #     validated_prop = "30"
            # Check its a multiple of 60
            if not value_as_int%60 == 0:
                # Round up to next 60
                validated_prop = AWSService._roundup(value=value_as_int, multiple=60)
            else:
                # Value is fine
                validated_prop = value

        except Exception as err:
            LOGGER.info(
                "Period property is invalid, falling back to service default")
            raise err

        return str(validated_prop)

    def build_dashboard_widgets_byresource_extra(resource: AWSResource) -> Tuple[List[Any], List[Any]]:
        # Implement extra at service level
        return [], []

    @classmethod
    def build_dashboard_widgets(cls, service, resources: List[AWSResource], widgets: Optional[Dict[str, str]] = None, is_group_resources = True) -> List[Any]:

        dashboard_widgets = []

        # Name of the service
        widget_name = {
            'type': 'text',
            'width': 24,
            'height': 1,
            'properties': {
                    'markdown': f'### **{service.cloudwatch_dashboard_section_title} Resources**'
            }
        }

        dashboard_widgets.append(widget_name)

        # If widgets are provided, use them
        if widgets:
            dashboard_widgets.extend(widgets)

        if is_group_resources:
            widgets = cls._build_dashboard_widgets_bymetric(service, resources, widgets)
        else:
            widgets = cls._build_dashboard_widgets_byresource(service, resources, widgets)

        dashboard_widgets.extend(widgets)

        return dashboard_widgets


    @staticmethod
    def _build_dashboard_widgets_bymetric(service, resources: List[AWSResource], widgets: Optional[Dict[str, str]] = None) -> List[Any]:
        """
        Build dashboard widgets looping over metrics and combining into single charts
        """

        dashboard_widgets = []

        # Build
        for metric in service.default_metrics:

            # Get resources in a block
            block = []
            after_first = False

            for resource in resources:

                metrics_metric_options_dict = service.override_dashboard_metrics_options.get(metric, {})

                if after_first:
                    # [ "...", "ExecutionsFailed", "StateMachineArn", "arn:aws:states:us-west-2:ACCOUNTID:stateMachine:CloudWedgeBuilderStateMachine-Xm2QclLByXty" ]
                    block.append(['...', resource['cloudwatchDimensionId'], metrics_metric_options_dict])
                else:
                    # [ "AWS/States", "ExecutionsFailed", "StateMachineArn", "arn:aws:states:us-west-2:ACCOUNTID:stateMachine:CloudWedgeBuilderStateMachine-Xm2QclLByXty" ]
                    block.append(
                        [
                            service.cloudwatch_namespace,
                            metric,
                            service.cloudwatch_dimension,
                            resource['cloudwatchDimensionId'],
                            metrics_metric_options_dict
                        ]
                    )


                after_first = True

            metric_properties = {
                'metrics': block,
                'view': 'timeSeries',
                'stacked': False,
                'region': REGION,
                'title': metric,
                'legend': {
                        'position': 'bottom'
                },
                'yAxis': {
                    'left': {
                        'label': ''
                    },
                    'right': {
                        'label': ''
                    }
                }
            }

            # Add any dashboard overrides for the specific metric
            metric_prop_override = service.override_dashboard_metric_properties.get(metric, {})
            widget_metric_properties = {
                **metric_properties,
                **metric_prop_override
            }

            widget_metric = {
                'type': 'metric',
                'width': 12,
                # 'height': 6,
                'properties': widget_metric_properties
            }

            # Add any dashboard overrides for the specific metric
            widget_prop_override = service.override_dashboard_widget_properties.get(metric, {})
            widget_metric = {
                **widget_metric,
                **widget_prop_override
            }

            dashboard_widgets.append(widget_metric)

        return dashboard_widgets

    @staticmethod
    def _build_dashboard_widgets_byresource(service, resources: List[AWSResource], widgets: Optional[Dict[str, str]] = None) -> List[Any]:
        """
        Build dashboard widgets looping over the resource first
        """

        dashboard_widgets = []

        # Build
        for resource in resources:

            resource_widgets = []

            # Name of the resource
            widget_name = {
                'type': 'text',
                'width': 24,
                'height': 1,
                'properties': {
                        'markdown': f'# 🔼 {service.cloudwatch_dashboard_section_title} :: **{resource["name"]}**'
                }
            }

            resource_widgets.append(widget_name)

            display_metrics = service.default_dashboard_metrics or service.default_metrics

            for metric in display_metrics:

                metrics_metric_options_dict = service.override_dashboard_metrics_options.get(metric, {})

                # [ "AWS/States", "ExecutionsFailed", "StateMachineArn", "arn:aws:states:us-west-2:ACCOUNTID:stateMachine:CloudWedgeBuilderStateMachine-Xm2QclLByXty" ]
                metric_property = [
                    service.cloudwatch_namespace,
                    metric,
                    service.cloudwatch_dimension,
                    resource['cloudwatchDimensionId'],
                    metrics_metric_options_dict
                ]


                metric_properties = {
                    'metrics': [metric_property], # has to be an array of array of strings
                    'view': 'timeSeries',
                    'stacked': False,
                    'region': REGION,
                    'title': metric,
                    'legend': {
                            'position': 'bottom'
                    },
                    'yAxis': {
                        'left': {
                            'label': ''
                        },
                        'right': {
                            'label': ''
                        }
                    }
                }

                # Add any dashboard overrides for the specific metric
                metric_prop_override = service.override_dashboard_metric_properties.get(metric, {})
                widget_metric_properties = {
                    **metric_properties,
                    **metric_prop_override
                }

                widget_metric = {
                    'type': 'metric',
                    'width': 12,
                    # 'height': 6,
                    'properties': widget_metric_properties
                }

                # Add any dashboard overrides for the specific metric
                widget_prop_override = service.override_dashboard_widget_properties.get(metric, {})
                widget_metric = {
                    **widget_metric,
                    **widget_prop_override
                }

                resource_widgets.append(widget_metric)

            front_widgets, back_widgets = service.build_dashboard_widgets_byresource_extra(resource)

            # Put front widgets after the first widget since first widget will have the name
            resource_widgets[1:1] = front_widgets
            resource_widgets.extend(back_widgets)

            widget_spacer = {
                "height": 1,
                "width": 24,
                "type": "text",
                "properties": {
                    "markdown": ""
                }
            }

            resource_widgets.append(widget_spacer)

            dashboard_widgets.extend(resource_widgets)

        return dashboard_widgets
