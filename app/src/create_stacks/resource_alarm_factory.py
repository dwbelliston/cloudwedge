"""
ResourceAlarmFactory

ResourceAlarmFactory receives a resource and builds a cloudformation
stack templates for it based on its service configuration. Depending
on the tags on the resource, the resource may have an alarm created
for multiple metrics.
"""

import hashlib
from typing import Dict, List

from cloudwedge.models import AWSResource, AWSService
from cloudwedge.utils.logger import get_logger
from cloudwedge.utils.tags import TagsApi

LOGGER = get_logger("ResourceAlarmFactory")


class ResourceAlarmFactory():
    def __init__(self, resource: AWSResource, service: AWSService):

        LOGGER.info(
            f"🏗 > ResourceAlarmFactory for {service.cloudwatch_namespace}:{resource['uniqueId']}"
        )

        # Set up variables
        self.resource = resource
        self.service = service
        # Template will have a json object for each metric alarm
        self.all_resource_alarms_template = {}

    def get_template(self):
        return self.all_resource_alarms_template

    def build(self):
        """Build alarm json object for every metric"""

        # Get metrics by level for this resource
        resource_metrics_by_level = self._get_metrics_by_level()

        # For each alert level, build metrics for that level
        for alert_level, level_metrics in resource_metrics_by_level.items():
            # alert_level = 'critical'
            # level_metrics = ['CPUUtilization', 'NetworkIn']

            # For each metric in the level
            for metric in level_metrics:
                metric_supported = False
                # TODO: maybe think about this more, the trick is to do a caseinsensitve dict key
                # lookup
                # First question to check is if this metric is supported by the service
                for supported_metric_key in self.service.supported_metrics.keys():
                    # Get the key that matches, but cleaning value to allow some variation in matching
                    if self._clean_value(supported_metric_key) == self._clean_value(metric):
                        # We support this metric, build an alarm
                        metric_supported = True

                        # Build the metric template for this single metric
                        single_alarm_template = self._build_alarm(
                            level=alert_level, metric=metric, supported_metric_key=supported_metric_key)

                        # Add the metric to the coll
                        self.all_resource_alarms_template.update(
                            single_alarm_template)

                # if not metric_supported:
                #     LOGGER.info(f'Metric {metric} not supported for {self.service.name}')

        return self.all_resource_alarms_template

    @staticmethod
    def _hash_for_identifier(identifier):
        """Hash identifier to get unique id"""
        return hashlib.md5(identifier.encode('utf-8')).hexdigest()

    @staticmethod
    def _clean_value(value: str):
        """Clean the value, lower it and strip _"""
        return value.lower().replace("_", "").replace("-", "")

    def _get_metrics_by_level(self) -> Dict[str, List[str]]:
        """Get metrics for each alert level"""
        has_metrics, metrics_by_level = TagsApi.get_metrics_by_level_from_tags(
            self.resource['tags'])

        if has_metrics:
            return metrics_by_level
        else:
            # Metrics were not defined on the tags, fallback to default metrics for the service
            default_metrics = self.service.default_metrics
            # Grab the alert value from the tags
            alert_level = TagsApi.get_alert_level_from_tags(
                self.resource['tags'])

            # Return defaults, keyed by the alert level
            return {
                alert_level: default_metrics
            }

    def _get_resource_alarm_props(self, metric: str) -> Dict[str, str]:
        """Get any alarm prop overrides from the resource tags for the resource and for the given metric"""
        resource_alarm_props = {}

        clean_metric_name = self._clean_value(metric)

        # Get props based on resource details
        alarm_props_by_resource = self.service.get_default_resource_alarm_props(
            self.resource)

        # Get props based on tag prop overrides
        alarm_props_by_tag_root = TagsApi.get_tags_alarm_props(
            self.resource['tags'])

        # Get props based on tag metric prop overrides
        supported_metrics = self.service.supported_metrics.keys()
        alarm_props_by_tag_metric = TagsApi.get_tags_metric_props(
            self.resource['tags'], clean_metric_name, supported_metrics)

        return {
            **alarm_props_by_resource,
            **alarm_props_by_tag_root,
            **alarm_props_by_tag_metric
        }

    def _build_alarm(self, level: str, metric: str, supported_metric_key: str):
        """Build alarm template for metric"""
        LOGGER.info(f"🔧 >> Building {level}:{metric}")

        # Make Unique resource name for the template resource
        clean_metric_name = self._clean_value(metric)
        clean_resource_id = self._clean_value(self.resource['uniqueId'])
        unique_resource_name = f"{self._hash_for_identifier(self.resource['uniqueId'])}CloudWedge{clean_metric_name}"
        # Get alarm level
        alert_level = level
        # Make alarm name, using unique name
        alarm_name = f"cloudwedge-autogen-{self.service.name}-{self.resource['owner']}-{alert_level}-{clean_metric_name}-{clean_resource_id}"
        # Make alarm description, Key=Value format is parsed when notifications are sent
        # Space at end of each line is important
        alarm_description = (
            f"{AWSService.ALARM_DESCRIPTION_KEY_RESOURCE}={self.resource['name']} "
            f"{AWSService.ALARM_DESCRIPTION_KEY_METRIC}={metric} "
            f"{AWSService.ALARM_DESCRIPTION_KEY_LEVEL}={alert_level} "
            f"{AWSService.ALARM_DESCRIPTION_KEY_TYPE}={self.service.cloudwatch_namespace} "
            f"{AWSService.ALARM_DESCRIPTION_KEY_OWNER}={self.resource['owner']} "
        )

        # Set alarm notification destination
        alarm_actions = [AWSService.ALARM_TARGET_SNS]

        # Universal default alarm props (this gives all the props needed for a complete alarm)
        dynamic_alarm_props = {
            'AlarmActions': alarm_actions,
            'Statistic': "Average",
            'Period': 1,
            'TreatMissingData': "missing",
            'EvaluationPeriods': 10,
            'Threshold': 99,
            'ComparisonOperator': "GreaterThanOrEqualToThreshold"
        }

        # Service default alarm props (service defaults override universal defaults)
        dynamic_alarm_props = {
            **dynamic_alarm_props,
            **self.service.default_alarm_props
        }

        # Metric default alarm props (metric defaults override service defaults)
        dynamic_alarm_props = {
            **dynamic_alarm_props,
            **self.service.supported_metrics.get(supported_metric_key, {})
        }

        # Resource default alarm props (the final say are any resource level overrides)
        dynamic_alarm_props = {
            **dynamic_alarm_props,
            **self._get_resource_alarm_props(metric)
        }

        # Build json cloudformation for alarm
        alarm_props = {
            'AlarmName': alarm_name,
            'AlarmDescription': alarm_description,
            'Namespace': self.service.cloudwatch_namespace,
            'MetricName': metric,
            'Dimensions': [
                {
                    'Name': self.service.cloudwatch_dimension,
                    'Value': self.resource['cloudwatchDimensionId']
                }
            ],
            # Values below here can be manipulated with tags and defaults
            **dynamic_alarm_props
        }

        # Validate properties
        validated_alarm_props = {
            **alarm_props,
            'Period': self.service.validate_prop_period(alarm_props['Period'], self.resource)
        }

        metric_template = {
            unique_resource_name: {
                "Type": "AWS::CloudWatch::Alarm",
                "Properties": validated_alarm_props
            }
        }

        return metric_template
