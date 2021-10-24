import json

from configuration.logger import LOGGER
from configuration import env as ENV


class DashboardMaker(object):
    ''' Make a dashboard scoped to an owner
    '''
    def __init__(self, owner, service, dashboard_values):
        '''
        Example Input:
        owner = 'ownerName'
        service = 'ec2'
        dashboard_values = {
            'StatusCheckFailed_System': [
                {'instance_id': 'i-333333333', 'period': '60', 'level': 'critical'},
                {'instance_id': 'i-4444444', 'period': '60', 'level': 'critical'}
            ],
            'StatusCheckFailed_Instance': [
                {'instance_id': 'i-333333333', 'period': '60', 'level': 'critical'},
                {'instance_id': 'i-4444444', 'period': '60', 'level': 'critical'}
            ],
            'CPUUtilization': [
                {'instance_id': 'i-333333333', 'period': '60', 'level': 'critical'},
                {'instance_id': 'i-4444444', 'period': '60', 'level': 'critical'}
            ],
            'NetworkIn': [
                {'instance_id': 'i-333333333', 'period': '60', 'level': 'critical'},
                {'instance_id': 'i-4444444', 'period': '60', 'level': 'critical'}
            ]
        }
        '''

        self.template = ''  # Init to empty
        self.owner = owner
        self.service = service
        self.dashboard_values = dashboard_values

        # Set Dashboard Values
        self.resource_unique_name = f'CloudWedge{self.owner}{self.service}Dashboard'
        self.dashboard_name = f'cloudwedge-{self.owner}-{self.service}'
        self.dashboard_body = json.dumps(self.build_dashboard_body()).replace('"', '\\"')

        # Set the final template
        self.set_template()


    def get_template(self):
        return self.template


    def set_template(self):
        '''Set the base yaml for the dashboard'''
        # Yaml is indented 1 unit, to match under the parents Resource block
        self.template = f'''
    {self.resource_unique_name}:
        Type: AWS::CloudWatch::Dashboard
        Properties:
            DashboardBody: "{self.dashboard_body}"
            DashboardName: {self.dashboard_name}'''


    def build_dashboard_body(self):

        # Text widget for naming dashboard
        widgets = [
            {
                'type': 'text',
                'x': 0,
                'y': 0,
                'width': 24,
                'height': 2,
                'properties': {
                    'markdown': f'# {self.owner}\\n###### CREATED BY CLOUDWEDGE'
                }
            }
        ]

        placements = {
            'CPUUtilization': {
                'width': 24,
                'x': 0,
                'y': 2
            },
            'StatusCheckFailed_System': {
                'width': 6
            },
            'StatusCheckFailed_Instance': {
                'width': 6
            }
        }

        for metric, instances in self.dashboard_values.items():
            widget_properties = self.build_metric_body(metric, instances)

            place_overrides = placements.get(metric, {})

            widget = {
                'type': 'metric',
                'width': 12,
                'height': 6,
                'properties': widget_properties,
                **place_overrides
            }

            widgets.append(widget)

        return {
            'widgets': widgets
        }


    def build_metric_body(self, metric, instances):

        build_metric_func = getattr(self, f'_build_metrics_block_{self.service}')
        metrics = build_metric_func(metric, instances)

        return {
            'metrics': metrics,
            'view': 'timeSeries',
            'stacked': False,
            'region': ENV.REGION,
            'title': metric,
            'legend': {
                'position': 'right'
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


    def _build_metrics_block_ec2(self, metric, instances):
        block = []
        after_first = False
        for instance in instances:

            if after_first:
                block.append(['...', instance['instance_id']])
            else:
                block.append(['AWS/EC2', metric, 'InstanceId', instance['instance_id']])

            after_first = True

        return block


    def _build_metrics_block_rds(self, metric, instances):
        block = []
        after_first = False
        for instance in instances:

            if after_first:
                block.append(['...', instance['instance_id']])
            else:
                block.append(['AWS/RDS', metric, 'DBInstanceIdentifier', instance['instance_id']])

            after_first = True

        return block
