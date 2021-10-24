import hashlib

import lib.alarms_ec2 as EC2Alarms
import lib.alarms_rds as RDSAlarms
from configuration.logger import LOGGER
from configuration import env as ENV
from lib.util import get_tag_value
from lib.exceptions import UnsupportedService, UnsupportedServiceMetric, MetricMakerError


class MetricMaker(object):
    def __init__(self, *, instance, level, service, metric):
        self.resource = None

        if service == 'ec2':
            alarm_class = EC2Alarms
        elif service == 'rds':
            alarm_class = RDSAlarms
        else:
            # Raise error that service is not supported
            raise UnsupportedService(f'CloudWedge does not support service [{service}]')

        try:
            cfn_metric_maker = getattr(alarm_class, f'{service.upper()}{metric}')
            self.resource = cfn_metric_maker(instance=instance, level=level)
        except AttributeError as err:
            raise UnsupportedServiceMetric(f'Service {service} does not support metric {metric}')
        except Exception as err:
            LOGGER.error(f"ERROR: Building metric failed: {err}")
            raise MetricMakerError(f'Metric Maker failed with err: {err}')

    def get_template(self):
        return self.resource.get_template()


    def get_dashboard_value_for_metric(self):
        return self.resource.get_dashboard()


class CPUUtilization(MetricMaker):

    def __init__(self, *, instance, level, service):
        super().__init__(instance=instance, level=level, service=service, metric='CPUUtilization')


class StatusCheckFailed_Instance(MetricMaker):

    def __init__(self, *, instance, level, service):
        super().__init__(instance=instance, level=level, service=service, metric='StatusCheckFailed_Instance')


class StatusCheckFailed_System(MetricMaker):

    def __init__(self, *, instance, level, service):
        super().__init__(instance=instance, level=level, service=service, metric='StatusCheckFailed_System')


class DiskReadOps(MetricMaker):

    def __init__(self, *, instance, level, service):
        super().__init__(instance=instance, level=level, service=service, metric='DiskReadOps')


class DiskWriteOps(MetricMaker):

    def __init__(self, *, instance, level, service):
        super().__init__(instance=instance, level=level, service=service, metric='DiskWriteOps')


class NetworkIn(MetricMaker):

    def __init__(self, *, instance, level, service):
        super().__init__(instance=instance, level=level, service=service, metric='NetworkIn')


class NetworkOut(MetricMaker):

    def __init__(self, *, instance, level, service):
        super().__init__(instance=instance, level=level, service=service, metric='NetworkOut')


class FreeableMemory(MetricMaker):

    def __init__(self, *, instance, level, service):
        super().__init__(instance=instance, level=level, service=service, metric='FreeableMemory')


class FreeStorageSpace(MetricMaker):

    def __init__(self, *, instance, level, service):
        super().__init__(instance=instance, level=level, service=service, metric='FreeStorageSpace')
