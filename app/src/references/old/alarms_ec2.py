import hashlib

from configuration.logger import LOGGER
from configuration import env as ENV
from lib.util import get_tag_value


class EC2AlarmBase(object):
    def __init__(self, *, instance, level, metric):
        self.template = ''  # Init to empty
        self.instance = instance
        self.level = level
        self.metric = metric
        self.tags = instance['Tags']

        # Set Instance Values
        self.instance_id = instance['InstanceId']
        self.instance_detailed_monitoring = instance['DetailedMonitoring']
        self.resource_unique_name = f"{self.instance_id.split('-')[1]}CloudWedge{self.metric.replace('_', '')}"
        self.instance_name = instance['Name']
        self.instance_is_running = True if instance['State'] == 'running' else False

        # Set Alert Values
        self.alert_owner = (get_tag_value(self.tags, ENV.TAG_OWNER) or 'cloudwedge').lower()
        # Use the supplied level, else get it from tag, or fall back to default
        self.alert_level = (self.level if self.level else get_tag_value(self.tags, ENV.TAG_LEVEL) or 'medium').lower()
        self.alert_topic = ENV.HUB_INGEST_TOPIC

        # Set period
        self.period = '60' if self.instance_detailed_monitoring == 'enabled' else '300'


    def get_template(self):
        return self.template


    def get_dashboard(self):
        return {
            'metric': self.metric,
            'values': {
                'instance_id': self.instance_id,
                'period': self.period,
                'level': self.level
            }
        }


    def set_base_yaml(self):
        '''Set the base yaml for the alarm, specifics for alarms will be updated on their class'''
        # Yaml is indented 1 unit, to match under the parents Resource block
        self.template = f"""
    {self.resource_unique_name}:
        Type: AWS::CloudWatch::Alarm
        Properties:
            AlarmDescription: Instance={self.instance_name} Metric={self.metric} AlertLevel={self.alert_level} Type=EC2 AlertOwner={self.alert_owner}
            Namespace: AWS/EC2
            MetricName: {self.metric}
            Statistic: Average
            Period: {self.period}
            Dimensions:
                - Name: InstanceId
                  Value: {self.instance_id}"""

        self.set_alert_on_okay()


    def set_alert_on_okay(self):
        tag_value = get_tag_value(self.tags, ENV.TAG_ALERT_ON_OK)

        if tag_value and (tag_value == 'all' or self.metric in tag_value):
            self.template += f"""
            OKActions:
                - { self.alert_topic}"""


class EC2CPUUtilization(EC2AlarmBase):

    def __init__(self, *, instance, level):
        super().__init__(instance=instance, level=level, metric='CPUUtilization')

        # Set Alarm Values
        self.alarm_name = f'{ENV.ALARM_PREFIX}-ec2-{self.alert_owner}-{self.alert_level}-{self.instance_id}-cpu'

        # Set Alarm values from tags
        self.evaluation_periods = get_tag_value(
            self.tags, ENV.TAG_ALARM_EC2_EVALUATION_PERIODS) or '5'
        self.threshold = get_tag_value(
            self.tags, ENV.TAG_ALARM_EC2_CPU_THRESHOLD) or '90'

        self.set_yaml()


    def set_yaml(self):
        self.set_base_yaml()

        self.template += f"""
            AlarmName: {self.alarm_name}
            TreatMissingData: breaching
            EvaluationPeriods: {self.evaluation_periods}
            Threshold: {self.threshold}
            ComparisonOperator: GreaterThanOrEqualToThreshold
            AlarmActions:
                - {self.alert_topic}
"""


class EC2StatusCheckFailed_Instance(EC2AlarmBase):

    def __init__(self, *, instance, level):
        super().__init__(instance=instance, level=level, metric='StatusCheckFailed_Instance')

        # Set Alarm Values
        self.alarm_name = f'{ENV.ALARM_PREFIX}-ec2-{self.alert_owner}-{self.alert_level}-{self.instance_id}-instance-failed'

        self.set_yaml()

    def set_yaml(self):
        self.set_base_yaml()

        self.template += f"""
            AlarmName: {self.alarm_name}
            EvaluationPeriods: 3
            Threshold: 1
            ComparisonOperator: GreaterThanOrEqualToThreshold
            AlarmActions:
                - {self.alert_topic}
"""



class EC2StatusCheckFailed_System(EC2AlarmBase):

    def __init__(self, *, instance, level):
        super().__init__(instance=instance, level=level, metric='StatusCheckFailed_System')

        # Set Alarm Values
        self.alarm_name = f'{ENV.ALARM_PREFIX}-ec2-{self.alert_owner}-{self.alert_level}-{self.instance_id}-system-failed'

        # Set Alarm values from tags
        self.auto_recover = False if get_tag_value(self.tags, ENV.TAG_ALARM_EC2_AUTO_RECOVER) == 'false' else True

        self.set_yaml()


    def set_yaml(self):
        self.set_base_yaml()

        self.template += f"""
            AlarmName: {self.alarm_name}
            EvaluationPeriods: 2
            Threshold: 1
            ComparisonOperator: GreaterThanOrEqualToThreshold
            AlarmActions:
                - {self.alert_topic}
                { '- !Sub "arn:aws:automate:${AWS::Region}:ec2:recover"' if self.auto_recover and self.instance_is_running else ''}
"""


class EC2DiskReadOps(EC2AlarmBase):

    def __init__(self, *, instance, level):
        super().__init__(instance=instance, level=level, metric='DiskReadOps')

        # Set Alarm Values
        self.alarm_name = f'{ENV.ALARM_PREFIX}-ec2-{self.alert_owner}-{self.alert_level}-{self.instance_id}-disk-read-ops'

        # Set Alarm values from tags
        self.evaluation_periods = get_tag_value(
            self.tags, ENV.TAG_ALARM_EC2_EVALUATION_PERIODS) or '5'
        self.threshold = get_tag_value(
            self.tags, ENV.TAG_ALARM_EC2_RIO_THRESHOLD) or '5000'

        self.set_yaml()

    def set_yaml(self):
        self.set_base_yaml()

        self.template += f"""
            AlarmName: {self.alarm_name}
            EvaluationPeriods: {self.evaluation_periods}
            Threshold: {self.threshold}
            ComparisonOperator: GreaterThanOrEqualToThreshold
            AlarmActions:
                - {self.alert_topic}
"""


class EC2DiskWriteOps(EC2AlarmBase):

    def __init__(self, *, instance, level):
        super().__init__(instance=instance, level=level, metric='DiskWriteOps')

        # Set Alarm Values
        self.alarm_name = f'{ENV.ALARM_PREFIX}-ec2-{self.alert_owner}-{self.alert_level}-{self.instance_id}-disk-write-ops'

        # Set Alarm values from tags
        self.evaluation_periods = get_tag_value(
            self.tags, ENV.TAG_ALARM_EC2_EVALUATION_PERIODS) or '5'
        self.threshold = get_tag_value(
            self.tags, ENV.TAG_ALARM_EC2_WIO_THRESHOLD) or '5000'

        self.set_yaml()

    def set_yaml(self):
        self.set_base_yaml()

        self.template += f"""
            AlarmName: {self.alarm_name}
            EvaluationPeriods: {self.evaluation_periods}
            Threshold: {self.threshold}
            ComparisonOperator: GreaterThanOrEqualToThreshold
            AlarmActions:
                - {self.alert_topic}
"""


class EC2NetworkIn(EC2AlarmBase):

    def __init__(self, *, instance, level):
        super().__init__(instance=instance, level=level, metric='NetworkIn')

        # Set Alarm Values
        self.alarm_name = f'{ENV.ALARM_PREFIX}-ec2-{self.alert_owner}-{self.alert_level}-{self.instance_id}-network-in'

        # Set Alarm values from tags
        self.evaluation_periods = get_tag_value(
            self.tags, ENV.TAG_ALARM_EC2_EVALUATION_PERIODS) or '5'
        self.threshold = get_tag_value(
            self.tags, ENV.TAG_ALARM_EC2_NETIN_THRESHOLD) or '1000000'

        self.set_yaml()

    def set_yaml(self):
        self.set_base_yaml()

        self.template += f"""
            AlarmName: {self.alarm_name}
            EvaluationPeriods: {self.evaluation_periods}
            Threshold: {self.threshold}
            ComparisonOperator: GreaterThanOrEqualToThreshold
            AlarmActions:
                - {self.alert_topic}
"""


class EC2NetworkOut(EC2AlarmBase):

    def __init__(self, *, instance, level):
        super().__init__(instance=instance, level=level, metric='NetworkOut')

        # Set Alarm Values
        self.alarm_name = f'{ENV.ALARM_PREFIX}-ec2-{self.alert_owner}-{self.alert_level}-{self.instance_id}-network-out'

        # Set Alarm values from tags
        self.evaluation_periods = get_tag_value(
            self.tags, ENV.TAG_ALARM_EC2_EVALUATION_PERIODS) or '5'
        self.threshold = get_tag_value(
            self.tags, ENV.TAG_ALARM_EC2_NETOUT_THRESHOLD) or '1000000'

        self.set_yaml()

    def set_yaml(self):
        self.set_base_yaml()

        self.template += f"""
            AlarmName: {self.alarm_name}
            EvaluationPeriods: {self.evaluation_periods}
            Threshold: {self.threshold}
            ComparisonOperator: GreaterThanOrEqualToThreshold
            AlarmActions:
                - {self.alert_topic}
"""
