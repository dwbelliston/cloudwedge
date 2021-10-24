---
label: SQS
---

# SQS

[!badge icon="check-circle" text="Stable" variant="success"]

## CloudWatch Configuration

When a resource is monitored it is going to be using these CloudWatch configurations to identify the metric.

| `namespace` | `dimension`          | `metrics`                                                                                                                            |
| ----------- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| AWS/SQS     | QueueName | [Available CloudWatch Metrics](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-available-cloudwatch-metrics.html) |

## Service Defaults

When an alarm is created it will first review the service defaults to populate the CloudWatch alarm properties. After the service defaults, it will then apply the specific metric defaults if they are provided.

| Alarm Property        | Default Value |
| :-------------------- | :------------ |
| **EvaluationPeriods** | `6`          |
| **Statistic**         | `Sum`     |
| **Period**            | `3600` [!badge text="1 Hour"]         |

## Dashboard Widgets

Each queue that is monitored will be added to a dashboard with the default widgets.

![](../../static/services/sqs/dashboard.png)

## Default Alarm Metrics

Unless there is a tag override, each queue that is monitored will be bootstrapped with the default alarm metrics.

- `ApproximateAgeOfOldestMessage`
- `NumberOfMessagesSent`

## Supported Metrics

### `NumberOfMessagesSent`

!!!light Defaults
| Alarm Property         | Default Value                   | Notes                                                              |
| :--------------------- | :------------------------------ | ------------------------------------------------------------------ |
| **Threshold**          | `0`                            | Threshold represents a sum of messages                         |
| **ComparisonOperator** | `LessThanOrEqualToThreshold` |                                                                    |
!!!

### `ApproximateAgeOfOldestMessage`

!!!light Defaults
| Alarm Property         | Default Value                   | Notes                                                              |
| :--------------------- | :------------------------------ | ------------------------------------------------------------------ |
| **Threshold**          | `3600 * 24` [!badge text="24 Hours"]                            | Threshold represents the age of a record                         |
| **ComparisonOperator** | `GreaterThanOrEqualToThreshold` |                                                                    |
!!!

### `ApproximateNumberOfMessagesVisible`

!!!light Defaults
No Metric Defaults
!!!

### `ApproximateNumberOfMessagesNotVisible`

!!!light Defaults
No Metric Defaults
!!!
