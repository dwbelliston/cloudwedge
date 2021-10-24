"""
Services

Register supported services classes for consumption
"""

from typing import List

from cloudwedge.models import AWSService

from .apigateway import ApiGatewayService
from .autoscalinggroup import AutoScalingGroupService
from .ec2 import EC2Service
from .ecs import ECSService
from .elasticbeanstalk import ElasticBeanstalkService
from .rds import RDSService
from .sqs import SQSService
from .statemachine import StateMachineService


class ServiceRegistry():
    # This list will be used to iterate through each supported service
    supported: List[AWSService] = [
        EC2Service,
        RDSService,
        ElasticBeanstalkService,
        ApiGatewayService,
        StateMachineService,
        SQSService,
        ECSService,
        AutoScalingGroupService
    ]

    @staticmethod
    def get_service(service_name: str) -> AWSService:

        # Add service to the lookup based on its 'service.name'
        # TODO: maybe we can loop through supported services and find the match
        # basically just want to provide a quick way to lookup service dynamically
        registry = {
            'ec2': EC2Service,
            'sqs': SQSService,
            'autoscalinggroup': AutoScalingGroupService,
            'rds': RDSService,
            'elasticbeanstalk': ElasticBeanstalkService,
            'apigateway': ApiGatewayService,
            'statemachine': StateMachineService,
            'ecs': ECSService
        }

        return registry[service_name]
