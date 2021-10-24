---
order: 80
icon: megaphone
label: Alarms
tags: [guide]
---

# Alarms

CloudWatch is an umbrella for a few different features. The one CloudWedge is using heavily is the CloudWatch Alarms features.

CloudWatch Alarms are basically a way to set some configurations around a provided metric. CloudWatch will then monitor that metric and when certain thresholds are met based on your configuration it will send an alert out.

!!! info CloudWatch Concepts

Jump into the documentation to learn more about the main concepts with CloudWatch.

[CloudWatch Core Concepts :icon-link-external:](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/cloudwatch_concepts.html)


A few notable terms to learn:

- `namespace` [:icon-link-external:](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/cloudwatch_concepts.html#Namespace)

- `dimension` [:icon-link-external:](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/cloudwatch_concepts.html#Dimension)

- `metrics` [:icon-link-external:](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/cloudwatch_concepts.html#Metric)

!!!

## Alarm Anatomy

CloudWedge uses CloudFormation to create the alarms for any given resource. The CloudFormation documentation is helpful to get oriented around what information goes into building an alarm.

The highlighted properties are the one CloudWedge exposes and you can manipulate for any resource with tags.

```yaml # hl_lines="9 14 24 25 26 28"
CloudWedgeAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
        ActionsEnabled: Boolean
        AlarmActions:
            - String
        AlarmDescription: String
        AlarmName: String
        ComparisonOperator: String
        DatapointsToAlarm: Integer
        Dimensions:
            - Dimension
        EvaluateLowSampleCountPercentile: String
        EvaluationPeriods: Integer
        ExtendedStatistic: String
        InsufficientDataActions:
            - String
        MetricName: String
        Metrics:
            - MetricDataQuery
        Namespace: String
        OKActions:
            - String
        Period: Integer
        Statistic: String
        Threshold: Double
        ThresholdMetricId: String
        TreatMissingData: String
        Unit: String
```
