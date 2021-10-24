---
label: AutoScaling
---

# AutoScaling

[!badge icon="tools" text="In Progress" variant="warning"]

## CloudWatch Configuration

When a resource is monitored it is going to be using these CloudWatch configurations to identify the metric.

| `namespace` | `dimension` | `metrics`                                                                                                                                       |
| ----------- | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| AWS/EC2     | AutoScalingGroupName  | [Available CloudWatch Metrics](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/viewing_metrics_with_cloudwatch.html#ec2-cloudwatch-metrics) |

## Service Defaults

When an alarm is created it will first review the service defaults to populate the CloudWatch alarm properties. After the service defaults, it will then apply the specific metric defaults if they are provided.

| Alarm Property         | Default Value                   |
| :--------------------- | :------------------------------ |
| **EvaluationPeriods**  | `5`                             |
| **Statistic**          | `Average`                       |
| **Period**             | `300`                           |
| **ComparisonOperator** | `GreaterThanOrEqualToThreshold` |

## Default Alarm Metrics

Unless there is a tag override, each group that is monitored will be bootstrapped with the default alarm metrics.

- `CPUUtilization`
- `NetworkIn`
- `NetworkOut`


## Supported Metrics

### `NumberOfMessagesSent`

!!!light Defaults
| Alarm Property         | Default Value                   | Notes                                                              |
| :--------------------- | :------------------------------ | ------------------------------------------------------------------ |
| **Threshold**          | `0`                            | Threshold represents a sum of messages                         |
| **ComparisonOperator** | `LessThanOrEqualToThreshold` |                                                                    |
!!!
