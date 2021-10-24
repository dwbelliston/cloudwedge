---
label: ECS
---

# ECS

[!badge icon="tools" text="In Progress" variant="warning"]

## CloudWatch Configuration

When a resource is monitored it is going to be using these CloudWatch configurations to identify the metric.

| `namespace` | `dimension` | `metrics`                                                                                                                                       |
| ----------- | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| AWS/ECS     | ClusterName | [Available CloudWatch Metrics](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/cloudwatch-metrics.html#available_cloudwatch_metrics) |

## Service Defaults

When an alarm is created it will first review the service defaults to populate the CloudWatch alarm properties. After the service defaults, it will then apply the specific metric defaults if they are provided.

| Alarm Property         | Default Value                   |
| :--------------------- | :------------------------------ |
| **EvaluationPeriods**  | `5`                             |
| **Statistic**          | `Average`                       |
| **Period**             | `300`                           |
| **ComparisonOperator** | `GreaterThanOrEqualToThreshold` |

## Default Alarm Metrics

Unless there is a tag override, each cluster that is monitored will be bootstrapped with the default alarm metrics.

- `CPUUtilization`
- `MemoryUtilization`

## Supported Metrics

### `CPUUtilization`

!!!light Defaults
| Alarm Property | Default Value | Notes                                    |
| :------------- | :------------ | ---------------------------------------- |
| **Threshold**  | `85`          | Threshold represents a percentage of CPU |
!!!

### `MemoryUtilization`

!!!light Defaults

| Alarm Property | Default Value | Notes                             |
| :------------- | :------------ | --------------------------------- |
| **Threshold**  | `70`          | Threshold represents a percentage |
!!!

### `CPUReservation`

!!!light Defaults

| Alarm Property | Default Value | Notes |
| :------------- | :------------ | ----- |
| **TBD**        |               |       |
!!!

### `MemoryReservation`

!!!light Defaults

| Alarm Property | Default Value | Notes |
| :------------- | :------------ | ----- |
| **TBD**        |               |       |
!!!

### `GPUReservation`

!!!light Defaults

| Alarm Property | Default Value | Notes |
| :------------- | :------------ | ----- |
| **TBD**        |               |       |
!!!