"""tags.py"""
import re
import os
from typing import Tuple, Dict, List

from cloudwedge.models import AWSService, AWSTag
from cloudwedge.utils.logger import get_logger

# Setup logger
LOGGER = get_logger('util.tags')


class TagsApi():

    @staticmethod
    def convert_dict_to_tags(input_dict: Dict[str, str]) -> List[AWSTag]:
        """Convert dictionary to tags format"""

        standard_tags = []

        for key, value in input_dict.items():
            standard_tags.append({
                'Key': key,
                'Value': value,
            })

        return standard_tags

    @staticmethod
    def convert_lowercase_tags_keys(input_dict: List[Dict[str, str]]) -> List[AWSTag]:
        """Convert lowercase keys to standard tags format"""

        standard_tags = []

        for tag in input_dict:
            standard_tags.append({
                'Key': tag['key'],
                'Value': tag['value']
            })

        return standard_tags

    @staticmethod
    def get_owner_from_tags(tags: List[AWSTag]) -> str:
        """Find owner tag and return its value"""

        owner_tag = TagsApi.get_tag_by_key(tags, AWSService.TAG_OWNER)

        return owner_tag['Value'] if owner_tag else AWSService.DEFAULT_OWNER


    @staticmethod
    def get_name_from_tags(tags: List[AWSTag]) -> str:
        """Find name tag and return its value"""

        name_tag = TagsApi.get_tag_by_key(tags, 'Name')

        return name_tag['Value'] if name_tag else None


    @staticmethod
    def get_alert_level_from_tags(tags: List[AWSTag]) -> str:
        """Find alert level tag and return its value"""

        found_tag = TagsApi.get_tag_by_key(tags, AWSService.TAG_LEVEL)

        found_level = found_tag['Value'] if found_tag else None

        # Return level if its a supported value, else return default
        return found_level if found_level in AWSService.SUPPORTED_ALERT_LEVELS else AWSService.DEFAULT_LEVEL


    @staticmethod
    def get_metrics_from_tags(tags: List[AWSTag], tag_key) -> str:
        """Find metrics for a given and return its value"""

        metrics = []

        found_tag = TagsApi.get_tag_by_key(tags, tag_key)

        if found_tag:
            # Tag value will be string like: 'CPUUtilization | StatusCheckFailed_Instance | StatusCheckFailed_System'
            metrics_list_string = found_tag['Value']
            # Remove white space and then split, to get nice list
            metrics = metrics_list_string.replace(' ', '').split('|')
        else:
            metrics = []

        return metrics


    @staticmethod
    def get_metrics_by_level_from_tags(tags: List[AWSTag]) -> Tuple[bool, Dict[str, List[str]]]:
        """Find metrics from tag and return value for each level"""

        # Get metrics from the tags for specific levels, each level can have its own
        # set of metrics. If there is overlap, the high level takes precedence
        level_metrics_sets = {
            'critical': set(TagsApi.get_metrics_from_tags(tags, AWSService.TAG_METRICS_CRITICAL)),
            'high': set(TagsApi.get_metrics_from_tags(tags, AWSService.TAG_METRICS_HIGH)),
            'medium': set(TagsApi.get_metrics_from_tags(tags, AWSService.TAG_METRICS_MEDIUM)),
            'low': set(TagsApi.get_metrics_from_tags(tags, AWSService.TAG_METRICS_LOW))
        }

        # In addition to a tag for specific level, there is a tag that can list metrics
        # and the metrics from that list inherit the level defined either by a tag that
        # defines the level, or fallback to default level
        dynamic_alert_level = TagsApi.get_alert_level_from_tags(tags)
        dynamic_metrics_set = set(
            TagsApi.get_metrics_from_tags(tags, AWSService.TAG_METRICS))
        # Add to the level set
        level_metrics_sets.get(dynamic_alert_level).update(dynamic_metrics_set)

        # Now, the individual levels do dont have duplicates, but now we check for duplicates
        # across levels, keeping the metric with highest level

        # Setup final return object
        metrics_by_level = {
            # We can just add critical, because its highest
            'critical': list(level_metrics_sets['critical']),
            'high': None,
            'medium': None,
            'low': None
        }

        # Keep running track of metrics that have been created
        all_metrics_set = set()
        # Add critical metrics to tracking
        all_metrics_set.update(level_metrics_sets['critical'])

        # Check each metric level, starting with high, then medium, then low
        for level in ['high', 'medium', 'low']:
            # Get metrics for the level, minus what has already been tracked
            scrubbed_metrics = level_metrics_sets[level] - all_metrics_set
            # Add these metrics to tracking
            all_metrics_set.update(scrubbed_metrics)
            # Add them in list form to output obj
            metrics_by_level[level] = list(scrubbed_metrics)

        # Check if any metrics were found, can be used to toggle to default metrics
        has_metrics = bool(all_metrics_set)

        return has_metrics, metrics_by_level


    @staticmethod
    def get_tag_by_key(tags=[], tag_key=None):
        """Find tag by key value and return full tag"""

        target_tag = None

        if type(tags) is list:

            target_tag = next((tag for tag in tags if tag['Key'] ==
                            tag_key), None)

        return target_tag

    @staticmethod
    def get_tags_alarm_props(tags: List[AWSTag]):
        """Get alarm props override from the tags"""
        alarm_props = {}

        for tag in tags:

            # Does the tag have the alarms props prefix
            if not tag['Key'].find(AWSService.TAG_ALARM_PROP_PREFIX) == -1:
                # This tag is attempting to override an alarm prop

                # Replace prefix with empty to leave the remain bit of the tag
                # which is the target prop value
                target_prop = tag['Key'].replace(AWSService.TAG_ALARM_PROP_PREFIX, '')

                # Is the target prop valid?
                for supported_prop in AWSService.SUPPORTED_ALARM_PROPS:
                    if target_prop.lower() == supported_prop.lower():
                        # This target prop is supported, set it has a default with its value
                        alarm_props[supported_prop] = tag['Value']

        return alarm_props

    @staticmethod
    def get_tags_metric_props(tags: List[AWSTag], metric: str, supported_metrics: List[str]):
        """Get metric props override from the tags"""
        metric_props = {}

        for tag in tags:
            # Does the tag have the metrics props prefix
            if not tag['Key'].find(AWSService.TAG_ALARM_METRIC_PREFIX) == -1:
                # This tag is attempting to override a metric prop

                # Get the target metric e.g. Tag['Key']= cloudwedge:alarm:metric:CPUUtilization:prop:Threshold
                try:
                    tag_override_metric = re.search(f'{AWSService.TAG_ALARM_METRIC_PREFIX}(.+?):prop:', tag['Key']).group(1)
                except AttributeError:
                    tag_override_metric = None

                if tag_override_metric and TagsApi.clean_value(metric) == TagsApi.clean_value(tag_override_metric):
                    # Is the target metric valid
                    for supported_metric in supported_metrics:
                        if TagsApi.clean_value(tag_override_metric) == TagsApi.clean_value(supported_metric):
                            # Target metric is supported

                            # Now check if the prop its trying to edit is valid
                            target_prop = tag['Key'].replace(f'{AWSService.TAG_ALARM_METRIC_PREFIX}{tag_override_metric}:prop:', '')

                            # Is the target prop valid?
                            for supported_prop in AWSService.SUPPORTED_ALARM_PROPS:
                                if target_prop.lower() == supported_prop.lower():
                                    # This target prop is supported, set it has a default with its value
                                    metric_props[supported_prop] = tag['Value']

        return metric_props

    @staticmethod
    def clean_value(value: str):
        """Clean the value, lower it and strip _"""
        if value:
            return value.lower().replace("_", "") if value else ''
