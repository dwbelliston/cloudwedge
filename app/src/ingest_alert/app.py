"""
IngestAlert

Ingest alert from an cloudwedge cloudwatch alarm, standardize the event
and send to alerting step function
"""
import os
import json
import re
import time

import boto3
from botocore.exceptions import ClientError

from cloudwedge.models import AWSService
from cloudwedge.utils.logger import get_logger

LOGGER = get_logger('IngestAlert')


# Setup boto3 session
SESSION = boto3.session.Session()
STEP_CLIENT = SESSION.client('stepfunctions')

# ARN of step function that will receive notification
STEPFUNCTION_ARN = os.environ.get('STEPFUNCTION_ARN')


class IngestAlert():
    def __init__(self, event=None):
        # Set up event
        self.event = event

    def run(self):
        """Run"""

        # Pull message from Sns event
        raw_sns_message = self.event['Records'][0]['Sns']['Message']
        alarm_details = json.loads(raw_sns_message)

        # Alarm description will have info we can use to identify more about the alert
        alarm_description = alarm_details['AlarmDescription']
        alarm_metric_name = alarm_details['Trigger']['MetricName']
        alarm_metric_threshold = alarm_details['Trigger']['Threshold']
        alert_state = alarm_details['NewStateValue']

        # Get values from alarm description
        re_alert_level = re.search(
            f'(?<={AWSService.ALARM_DESCRIPTION_KEY_LEVEL}=)(\w+)', alarm_description)
        re_alert_owner = re.search(
            f'(?<={AWSService.ALARM_DESCRIPTION_KEY_OWNER}=)(\w+)', alarm_description)
        re_alert_type = re.search(
            f'(?<={AWSService.ALARM_DESCRIPTION_KEY_TYPE}=)([\w,\-,\/]+)', alarm_description)
        re_alert_metric = re.search(
            f'(?<={AWSService.ALARM_DESCRIPTION_KEY_METRIC}=)([\w,\-]+)', alarm_description)
        re_resource_name = re.search(
            f'(?<={AWSService.ALARM_DESCRIPTION_KEY_RESOURCE}=)([\w,\-]+)', alarm_description)

        alert_level = re_alert_level.groups()[0]
        alert_owner = re_alert_owner.groups()[0]
        alert_type = re_alert_type.groups()[0]
        alert_metric = re_alert_metric.groups()[0]
        resource_name = re_resource_name.groups()[0]

        # Get sns subject ready
        sns_subject = self.make_sns_subject(state=alert_state, level=alert_level,
                                            namespace=alert_type, resource=resource_name,
                                            metric=alert_metric, threshold=alarm_metric_threshold)

        # Build object to send to step function
        step_input = {
            "level": alert_level.lower(),
            "type": alert_type.lower(),
            "owner": alert_owner.lower(),
            "metric": alert_metric,
            "state": alert_state,
            "resourceName": resource_name,
            "snsSubject": sns_subject,
            "snsMessage": self.make_sns_message(raw_sns_message, sns_subject),
            "event": self.event
        }

        LOGGER.info(
            f"Starting step function {STEPFUNCTION_ARN} : {step_input['snsSubject']}")

        try:
            response = STEP_CLIENT.start_execution(
                stateMachineArn=STEPFUNCTION_ARN,
                input=json.dumps(step_input)
            )
        except Exception as err:
            LOGGER.error(f"Failed to start step function with error: {err}")

            LOGGER.info("Waiting 10 seconds and will try again")
            time.sleep(10)

            try:
                response = STEP_CLIENT.start_execution(
                    stateMachineArn=STEPFUNCTION_ARN,
                    input=json.dumps(step_input)
                )
            except Exception as err:
                LOGGER.error(
                    f"We are in trouble... Again Failed to start step function with error: {err}")
                raise err

    def make_sns_subject(self, state=None, level=None, namespace=None, resource=None, metric=None, threshold=None):
        '''SNS subject can only be 100 chars'''
        # subject = (f'{alert_state.upper()[:6]} {alarm_description[:91]}..') if len(
        #     alarm_description) > 93 else f'{alert_state.upper()[:6]} {alarm_description}'

        # 'AWS/ElasticBeanstalk' > 'ElasticBeanstalk'
        service = namespace.split('/')[-1]

        # e.g. Critical ALARM on ElasticBeanstalk
        subject_prefix = f'{level.capitalize()} {state} on {service}'

        # "Critical ALARM on ElasticBeanstalk for Resourcename - CPUUtilization threshold 90"
        subject = f'{subject_prefix} for {resource} {metric} threshold {threshold}'

        # Check its length without any truncating
        if len(subject) > 98:
            # Still too long, just truncate end and add ellipses
            subject = f'{subject[:96]}..'

        return subject

    def make_sns_message(self, raw_sns_message, sns_subject):
        '''SNS message for different protocols'''

        sns_message = {"default": sns_subject,
                    "sms": sns_subject, "email": raw_sns_message}

        return sns_message
