"""
SQS for CloudWedge

Provides implementation details for sqs service. It follows contract
outlined in cloudwedge.models.AWSService
"""

from os import environ
from typing import Any, Dict, List, Optional, Tuple

import boto3
from cloudwedge.models import AWSResource, AWSService
from cloudwedge.utils.arnparse import arnparse
from cloudwedge.utils.logger import get_logger
from cloudwedge.utils.tags import TagsApi

REGION = environ.get('REGION')

LOGGER = get_logger('cloudwedge.sqs')


# Model for Service, extending AWSResource
class SQSResource(AWSResource):
    pass

# Class for Service
class SQSService(AWSService):
    # Name of the service, must be unique
    name = "sqs"
    # Cloudwatch alarm service specific values
    cloudwatch_namespace = "AWS/SQS"
    cloudwatch_dashboard_section_title = "SQS"
    cloudwatch_dimension = "QueueName"
    # Default metric to be used when metrics are not explicit in tags
    default_metrics = ["ApproximateAgeOfOldestMessage", "NumberOfMessagesSent"]
    default_dashboard_metrics = [
                       "ApproximateNumberOfMessagesVisible", "ApproximateNumberOfMessagesNotVisible", "ApproximateAgeOfOldestMessage"]
    # Alarm defaults for the service, applied if metric default doesnt exist
    default_alarm_props = {
        'EvaluationPeriods': "6",
        'Statistic': "Sum",
        'Period': "3600",
        # "ComparisonOperator": "GreaterThanOrEqualToThreshold"
        # "TreatMissingData": None
    }

    # List of supported metrics and default configurations
    supported_metrics = {
        'ApproximateNumberOfMessagesVisible': {
        },
        'ApproximateNumberOfMessagesNotVisible': {
        },
        'ApproximateAgeOfOldestMessage': {
            'Threshold': 3600 * 24,
            'ComparisonOperator': "GreaterThanOrEqualToThreshold"
        },
        'NumberOfMessagesSent': {
            'Threshold': 0,
            'ComparisonOperator': "LessThanOrEqualToThreshold"
        },
    }

    # There are dashboard additions that can be added at the metric level
    override_dashboard_metrics_options = {
        'NumberOfMessagesSent': { "stat": "Sum" },
        'ApproximateNumberOfMessagesVisible': { "label": "Last 1 Min", "stat": "Sum" },
        'ApproximateNumberOfMessagesNotVisible': { "label": "Last 1 Min", "stat": "Sum" },
        'ApproximateAgeOfOldestMessage': { "label": "Last 1 Min", "stat": "Sum" },
    }

    override_dashboard_metric_properties = {
        'ApproximateNumberOfMessagesVisible': {
            "view": "singleValue",
            "period": 60,
            "title":  "In Queue"
        },
        'ApproximateNumberOfMessagesNotVisible': {
            "view": "singleValue",
            "period": 60,
            "title":  "In flight"
        },
        'ApproximateAgeOfOldestMessage': {
            "view": "singleValue",
            "period": 60,
            "title":  "Oldest message age"
        },
    }

    # There are dashboard additions that can be added at the metric level
    override_dashboard_widget_properties = {
        'NumberOfMessagesSent': {
            'width': 24,
            'height': 6,
        },
        'ApproximateNumberOfMessagesVisible': {
            'width': 8,
            'height': 3,
        },
        'ApproximateNumberOfMessagesNotVisible': {
            'width': 8,
            'height': 3,
        },
        'ApproximateAgeOfOldestMessage': {
            'width': 8,
            'height': 3,
        },
    }

    @staticmethod
    def get_default_resource_alarm_props(resource: SQSResource) -> Dict[str, str]:
        """
        Get default alarm props based on the resource values
        """

        default_alarm_props = {}

        return default_alarm_props

    @staticmethod
    def validate_prop_period(value: str, resource: Optional[SQSResource]) -> str:
        """
        Validate alarm property 'Period'
        """

        # Validate prop with base method (like calling super)
        validated_base_prop = AWSService.validate_prop_period(value, resource)

        return validated_base_prop

    @staticmethod
    def build_dashboard_widgets(resources: List[SQSResource]) -> List[Any]:
        """
        Build dashboard widgets for the resources
        """

        # Get widgets with base method (like calling super)
        return AWSService.build_dashboard_widgets(SQSService, resources, is_group_resources=False)

    @staticmethod
    def build_dashboard_widgets_byresource_extra(resource: SQSResource) -> Tuple[List[Any], List[Any]]:
        """
        Build extra dashboard widgets for the resource
        """

        front_widgets = []
        back_widgets = []

        back_widgets.append({
            "height": 6,
            "width": 24,
            "type": "metric",
            "properties": {
                "metrics": [
                    [ "AWS/SQS", "NumberOfMessagesSent", "QueueName", resource['cloudwatchDimensionId'], { "stat": "Sum", "label": "Records Added (Interval @ 5 Min Sum)" } ],
                    [ "...", resource['cloudwatchDimensionId'], { "stat": "Maximum", "label": "In Queue (Interval @ 5 Min Max)", } ]
                ],
                "period": 360,
                "view": "timeSeries",
                "title": "Records Added vs In Queue Rolling",
                "region": REGION,
            }
        })

        return front_widgets, back_widgets


    @ staticmethod
    def get_resources(session: boto3.session.Session) -> List[SQSResource]:
        """
        Return all AWS SQS instances within scope, based on the tags
        """

        SQS_RESOURCE = session.resource('sqs')
        SQS_CLIENT = session.client('sqs')

        try:
            instances: List[SQSResource] = []

            # Get paginator for service
            paginator = SQS_CLIENT.get_paginator('list_queues').paginate()

            # Filters=[
            #     # Filter for only resources that have cloudwedge tag
            #     {'Name': f"tag:{AWSService.TAG_ACTIVE}",
            #         'Values': ["true"]},
            # ]

            # Collect all instances
            for page_instances in paginator:
                for queue_url in page_instances['QueueUrls']:


                    # For each db, get the tags on the instance
                    sqs_instance_tags = SQS_CLIENT.list_queue_tags(
                        QueueUrl=queue_url
                    )

                    # e.g. [{'Key': 'notifications', 'Value': 'true'}]
                    sqs_tags = sqs_instance_tags['Tags']

                    # If the active monitoring tag is on the instance, include in resource collection
                    # Stripping key so no whitespace mismatch
                    if any((tag_key.strip() == AWSService.TAG_ACTIVE and tag_val == 'true') for tag_key, tag_val in sqs_tags.items()):
                        # Add this queue to resource list
                        queue_res = SQS_RESOURCE.Queue(queue_url)

                        instances.append({"QueueUrl": queue_url, "Tags": sqs_tags, **queue_res.attributes})

            # Get things in a neat sqs resource object
            cleaned_resources: List[SQSResource] = []


            # >>> Example Instance
            # 'QueueUrl': 'url'
            # 'Tags': {tagKey: tagValue}
            # 'QueueArn':'arn:aws:sqs:us-west-2:ACCOUNTID:cc-west-dev-sqs-billing-invocation-dlq'
            # 'ApproximateNumberOfMessages':'0'
            # 'ApproximateNumberOfMessagesNotVisible':'0'
            # 'ApproximateNumberOfMessagesDelayed':'0'
            # 'CreatedTimestamp':'1625761037'
            # 'LastModifiedTimestamp':'1625761037'
            # 'VisibilityTimeout':'900'
            # 'MaximumMessageSize':'262144'
            # 'MessageRetentionPeriod':'1209600'
            # 'DelaySeconds':'0'
            # 'ReceiveMessageWaitTimeSeconds':'20'
            # 'KmsMasterKeyId':'alias/aws/sqs'
            # 'KmsDataKeyReusePeriodSeconds':'300'

            for instance in instances:

                # Get values from instance details
                tags = [{"Key": tag_key, "Value": tag_val} for tag_key, tag_val in instance.get('Tags').items()]

                arn = arnparse(instance['QueueArn'])

                # Setup SQSResource values
                service = SQSService.name
                resource_name = arn.resource_id
                resource_id = resource_name
                resource_owner = TagsApi.get_owner_from_tags(tags)
                tags = tags

                # Create SQSResource
                clean_resource = SQSResource(
                    service=service,
                    name=resource_name,
                    uniqueId=resource_name,
                    cloudwatchDimensionId=resource_id,
                    owner=resource_owner,
                    tags=tags,
                )

                # Add to collection
                cleaned_resources.append(clean_resource)

            return cleaned_resources

        except Exception as err:
            LOGGER.info(
                f"Failed to get instances information with error: {err}")
            raise err
