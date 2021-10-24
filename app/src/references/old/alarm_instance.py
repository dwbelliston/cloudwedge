from configuration.logger import LOGGER
from configuration import env as ENV

import lib.alarms as CfnAlarms
from lib.util import get_tag_value, parse_tag_value_list
from lib.exceptions import UnsupportedService, MetricMakerError


DEFAULT_LEVEL = 'medium'

class InstanceBase(object):
    def __init__(self, *, instance, service):
        LOGGER.info(f'Building {service} Instance')
        self.instance = instance
        self.tags = instance['Tags']
        self.service = service
        self.created_metrics = []
        self.template = f'#### {self.service} Instance Resource Group ####'
        self.default_metrics = []
        self.dashboard_instance_values = {}


    def get_yaml(self):
        return self.template


    def get_dashboard_instance_values(self):
        return self.dashboard_instance_values


    def make_instance_yaml(self):

        use_default_metrics = True

        for level in ENV.LEVELS:

            # Get the method that will return metrics for the level
            metric_list_for_level = getattr(self, f'_metrics_{level.lower()}')

            # Review each metric
            for metric in metric_list_for_level():
                # If we had at least one metric explicit marked, dont need defaults
                use_default_metrics = False
                # Build the metric with the level
                self._build_metric(metric, level)

        # Check the generic metric level
        for metric in self._metrics(use_default_metrics):
            level = get_tag_value(self.tags, ENV.TAG_LEVEL) or DEFAULT_LEVEL
            # Build the metric
            self._build_metric(metric, level)


    def _build_metric(self, metric, level):
        # Use the cloudformation constructor for the metric
        try:
            # Only create if not already created
            if metric not in self.created_metrics:
                # Add to created metric list to account for it
                self.created_metrics.append(metric)

                cfn_alarm_metric_class = getattr(CfnAlarms, metric)
                alarm = cfn_alarm_metric_class(instance=self.instance, level=level, service=self.service)

                metric_yaml = alarm.get_template()
                # Add dashboard values to
                self.add_dashboard_instance_values(alarm.get_dashboard_value_for_metric())

                # Add metric yaml to instance template
                self.template += metric_yaml

        # Catching errors, but not raising for silent death.
        # TODO: bubble these up to user
        except AttributeError as err:
            LOGGER.error(f"ERROR: Building metric failed with bad metric type: {err}")
        except UnsupportedService as err:
            LOGGER.error(f"ERROR: Building metric failed with unsupported service: {err}")
        except MetricMakerError as err:
            LOGGER.error(f"ERROR: Building metric failed with metric maker exception: {err}")
        except Exception as err:
            LOGGER.error(f"ERROR: Building metric failed: {err}")


    def _metrics_critical(self):
        return parse_tag_value_list(get_tag_value(self.tags, ENV.TAG_ALERT_METRICS_CRITICAL), self.service) or []


    def _metrics_high(self):
        return parse_tag_value_list(get_tag_value(self.tags, ENV.TAG_ALERT_METRICS_HIGH), self.service) or []


    def _metrics_medium(self):
        return parse_tag_value_list(get_tag_value(self.tags, ENV.TAG_ALERT_METRICS_MEDIUM), self.service) or []


    def _metrics_low(self):
        return parse_tag_value_list(get_tag_value(self.tags, ENV.TAG_ALERT_METRICS_LOW), self.service) or []


    def _metrics(self, use_default):
        '''Determine the metrics this instance will have alarms for'''

        explicit_metrics = get_tag_value(self.tags, ENV.TAG_ALERT_METRICS)

        tag_metrics = parse_tag_value_list(explicit_metrics, self.service)

        if not tag_metrics and use_default:
            return self.default_metrics
        else:
            return tag_metrics


    def add_dashboard_instance_values(self, metric_values):
        '''Set easy to access values to construct dashboard'''
        metric = metric_values['metric']
        values = metric_values['values']

        # Group the alarms by the metric, dashboard will display metric with all instances graphed
        self.dashboard_instance_values.setdefault(metric, values)


class Ec2Instance(InstanceBase):

    def __init__(self, *, instance):
        super().__init__(instance=instance, service='ec2')
        self.default_metrics = ['CPUUtilization', 'StatusCheckFailed_Instance', 'StatusCheckFailed_System']
        self.make_instance_yaml()


class RdsInstance(InstanceBase):

    def __init__(self, *, instance):
        super().__init__(instance=instance, service='rds')
        self.default_metrics = ['CPUUtilization']
        self.make_instance_yaml()
