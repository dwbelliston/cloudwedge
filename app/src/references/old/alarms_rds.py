import hashlib

from configuration.logger import LOGGER
from configuration import env as ENV
from lib.util import get_tag_value


class RDSAlarmBase(object):
    def __init__(self, *, instance, level, metric):
        self.template = ''  # Init to empty
        self.instance = instance
        self.level = level
        self.metric = metric
        self.tags = instance['Tags']

        # Set Instance Values
        self.period = 60
        self.db_identifier = instance['InstanceId']
        self.resource_unique_name = self.hash_for_identifier(self.db_identifier)
        self.instance_name = instance['Name']
        self.db_engine = instance.get('Engine', '')

        # Set Alert Values
        self.alert_owner = (get_tag_value(self.tags, ENV.TAG_OWNER) or 'cloudwedge').lower()
        # Use the supplied level, else get it from tag, or fall back to default
        self.alert_level = (self.level if self.level else get_tag_value(self.tags, ENV.TAG_LEVEL) or 'medium').lower()
        self.alert_topic = ENV.HUB_INGEST_TOPIC


    def get_template(self):
        return self.template


    def get_dashboard(self):
        return {
            'metric': self.metric,
            'values': {
                'instance_id': self.db_identifier,
                'period': self.period,
                'level': self.level
            }
        }

    @staticmethod
    def hash_for_identifier(identifier):
        return hashlib.md5(identifier.encode('utf-8')).hexdigest()


class RDSCPUUtilization(RDSAlarmBase):

    def __init__(self, *, instance, level):
        super().__init__(instance=instance, level=level, metric='CPUUtilization')

        # Set Alarm Values
        self.alarm_name = f'{ENV.ALARM_PREFIX}-rds-{self.alert_owner}-{self.alert_level}-{self.db_identifier}-cpu'

        # Set Alarm values from tags
        self.evaluation_periods = get_tag_value(
            self.tags, ENV.TAG_ALARM_RDS_EVALUATION_PERIODS) or '15'
        self.threshold = get_tag_value(
            self.tags, ENV.TAG_ALARM_RDS_CPU_THRESHOLD) or '90'

        self.set_yaml()


    def set_yaml(self):
        # Yaml is indented 1 unit, to match under the parents Resource block
        self.template = f"""
    {self.resource_unique_name}CloudWedgeRDSCPUUtilization:
        Type: AWS::CloudWatch::Alarm
        Properties:
            AlarmName: {self.alarm_name}
            AlarmDescription: Instance={self.instance_name} Metric={self.metric} AlertLevel={self.alert_level} Type=RDS AlertOwner={self.alert_owner}
            MetricName: {self.metric}
            Namespace: AWS/RDS
            Statistic: Average
            Period: 60
            TreatMissingData: breaching
            EvaluationPeriods: {self.evaluation_periods}
            Threshold: {self.threshold}
            ComparisonOperator: GreaterThanOrEqualToThreshold
            Dimensions:
                - Name: DBInstanceIdentifier
                  Value: {self.db_identifier}
            AlarmActions:
                - {self.alert_topic}
"""


class RDSFreeableMemory(RDSAlarmBase):

    def __init__(self, *, instance, level):
        super().__init__(instance=instance, level=level, metric='FreeableMemory')

        # Set Alarm Values
        self.alarm_name = f'{ENV.ALARM_PREFIX}-rds-{self.alert_owner}-{self.alert_level}-{self.db_identifier}-memory'

        # Set Alarm values from tags
        self.evaluation_periods = get_tag_value(
            self.tags, ENV.TAG_ALARM_RDS_EVALUATION_PERIODS) or '15'
        self.threshold = get_tag_value(
            self.tags, ENV.TAG_ALARM_RDS_STORAGE_THRESHOLD) or '100000000'

        self.set_yaml()


    def set_yaml(self):
        # Yaml is indented 1 unit, to match under the parents Resource block
        self.template = f"""
    {self.resource_unique_name}CloudWedgeRDSFreeableMemory:
        Type: AWS::CloudWatch::Alarm
        Properties:
            AlarmName: {self.alarm_name}
            AlarmDescription: Instance={self.instance_name} Metric={self.metric} AlertLevel={self.alert_level} Type=RDS AlertOwner={self.alert_owner}
            MetricName: {self.metric}
            Namespace: AWS/RDS
            Statistic: Average
            Period: 60
            EvaluationPeriods: {self.evaluation_periods}
            Threshold: {self.threshold}
            ComparisonOperator: LessThanOrEqualToThreshold
            Dimensions:
                - Name: DBInstanceIdentifier
                  Value: {self.db_identifier}
            AlarmActions:
                - {self.alert_topic}
"""


class RDSFreeStorageSpace(RDSAlarmBase):

    def __init__(self, *, instance, level):
        super().__init__(instance=instance, level=level, metric='FreeStorageSpace')

        # Set Alarm Values
        self.alarm_name = f'{ENV.ALARM_PREFIX}-rds-{self.alert_owner}-{self.alert_level}-{self.db_identifier}-storage'

        # Set Alarm values from tags
        self.evaluation_periods = get_tag_value(
            self.tags, ENV.TAG_ALARM_RDS_EVALUATION_PERIODS) or '15'
        self.threshold = get_tag_value(
            self.tags, ENV.TAG_ALARM_RDS_MEMORY_THRESHOLD) or '500000000'

        self.set_yaml()


    def set_yaml(self):
        # Yaml is indented 1 unit, to match under the parents Resource block
        self.template = f"""
    {self.resource_unique_name}CloudWedgeRDSFreeStorageSpace:
        Type: AWS::CloudWatch::Alarm
        Properties:
            AlarmName: {self.alarm_name}
            AlarmDescription: Instance={self.instance_name} Metric={self.metric} AlertLevel={self.alert_level} Type=RDS AlertOwner={self.alert_owner}
            MetricName: {self.metric}
            Namespace: AWS/RDS
            Statistic: Average
            Period: 60
            EvaluationPeriods: {self.evaluation_periods}
            Threshold: {self.threshold}
            ComparisonOperator: LessThanOrEqualToThreshold
            Dimensions:
                - Name: DBInstanceIdentifier
                  Value: {self.db_identifier}
            AlarmActions:
                - {self.alert_topic}
"""
