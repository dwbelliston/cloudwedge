---
label: EC2
---

# EC2

[!badge icon="check-circle" text="Stable" variant="success"]

## CloudWatch Configuration

When a resource is monitored it is going to be using these CloudWatch configurations to identify the metric.

| `namespace` | `dimension` | `metrics`                                                                                                                                       |
| ----------- | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| AWS/EC2     | InstanceId  | [Available CloudWatch Metrics](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/viewing_metrics_with_cloudwatch.html#ec2-cloudwatch-metrics) |

## Service Defaults

When an alarm is created it will first review the service defaults to populate the CloudWatch alarm properties. After the service defaults, it will then apply the specific metric defaults if they are provided.

| Alarm Property         | Default Value                   |
| :--------------------- | :------------------------------ |
| **EvaluationPeriods**  | `5`                             |
| **Statistic**          | `Average`                       |
| **Period**             | `300`                           |
| **ComparisonOperator** | `GreaterThanOrEqualToThreshold` |

## Default Alarm Metrics

Unless there is a tag override, each instance that is monitored will be bootstrapped with the default alarm metrics.

- `CPUUtilization`
- `StatusCheckFailed_Instance`
- `StatusCheckFailed_System`
- `DiskWriteOps`

## Supported Metrics

### `CPUUtilization`

!!!light Defaults
| Alarm Property | Default Value | Notes                                    |
| :------------- | :------------ | ---------------------------------------- |
| **Threshold**  | `85`          | Threshold represents a percentage of CPU |
!!!

### `StatusCheckFailed_Instance`

!!!light Defaults
| Alarm Property        | Default Value | Notes                        |
| :-------------------- | :------------ | ---------------------------- |
| **Threshold**         | `1`           | This is a count of failures. |
| **EvaluationPeriods** | `3`           |                              |
!!!

### `StatusCheckFailed_System`

!!!light Defaults
| Alarm Property        | Default Value | Notes                        |
| :-------------------- | :------------ | ---------------------------- |
| **Threshold**         | `1`           | This is a count of failures. |
| **EvaluationPeriods** | `2`           |                              |
!!!

### `DiskReadOps`

!!!light Defaults
| Alarm Property | Default Value | Notes  |
| :------------- | :------------ | ------ |
| **Threshold**  | `5000`        | Count |
!!!

### `DiskWriteOps`

!!!light Defaults

| Alarm Property | Default Value | Notes  |
| :------------- | :------------ | ------ |
| **Threshold**  | `5000`        | Count |
!!!

### `NetworkIn`

!!!light Defaults
| Alarm Property | Default Value | Notes  |
| :------------- | :------------ | ------ |
| **Threshold**  | `1000000`        | Count |
!!!

### `NetworkOut`

!!!light Defaults
| Alarm Property | Default Value | Notes  |
| :------------- | :------------ | ------ |
| **Threshold**  | `1000000`        | Count |
!!!
