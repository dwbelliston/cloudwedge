---
label: RDS
---

# RDS

[!badge icon="check-circle" text="Stable" variant="success"]

## CloudWatch Configuration

When a resource is monitored it is going to be using these CloudWatch configurations to identify the metric.

| `namespace` | `dimension`          | `metrics`                                                                                                                            |
| ----------- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| AWS/RDS     | DBInstanceIdentifier | [Available CloudWatch Metrics](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/MonitoringOverview.html#monitoring-cloudwatch) |

## Service Defaults

When an alarm is created it will first review the service defaults to populate the CloudWatch alarm properties. After the service defaults, it will then apply the specific metric defaults if they are provided.

| Alarm Property        | Default Value |
| :-------------------- | :------------ |
| **EvaluationPeriods** | `15`          |
| **Statistic**         | `Average`     |
| **Period**            | `60`          |

## Default Alarm Metrics

Unless there is a tag override, each database that is monitored will be bootstrapped with the default alarm metrics.

- `CPUUtilization`
- `FreeableMemory`
- `FreeStorageSpace`

## Supported Metrics


### `CPUUtilization`

!!!light Defaults
| Alarm Property         | Default Value                   | Notes                                                              |
| :--------------------- | :------------------------------ | ------------------------------------------------------------------ |
| **Threshold**          | `90`                            | Threshold represents a percentage of CPU                           |
| **TreatMissingData**   | `breaching`                     | If we dont get data it could be a sign the the CPU is overwhelmed. |
| **ComparisonOperator** | `GreaterThanOrEqualToThreshold` |                                                                    |
!!!

### `FreeableMemory`

!!!light Defaults
| Alarm Property         | Default Value                | Notes |
| :--------------------- | :--------------------------- | ----- |
| **Threshold**          | `100000000`                  |       |
| **ComparisonOperator** | `LessThanOrEqualToThreshold` |       |

!!!

### `FreeStorageSpace`

!!!light Defaults
| Alarm Property         | Default Value                | Notes |
| :--------------------- | :--------------------------- | ----- |
| **Threshold**          | `500000000`                  |       |
| **ComparisonOperator** | `LessThanOrEqualToThreshold` |       |
!!!