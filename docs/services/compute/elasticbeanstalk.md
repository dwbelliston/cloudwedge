---
label: ElasticBeanstalk
---

# ElasticBeanstalk

[!badge icon="tools" text="In Progress" variant="warning"]

## CloudWatch Configuration

When a resource is monitored it is going to be using these CloudWatch configurations to identify the metric.

| `namespace` | `dimension` | `metrics`                                                                                                                                       |
| ----------- | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| AWS/ElasticBeanstalk     | EnvironmentName  | [Available CloudWatch Metrics](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/health-enhanced-cloudwatch.html#health-enhanced-cloudwatch-metrics) |

## Service Defaults

When an alarm is created it will first review the service defaults to populate the CloudWatch alarm properties. After the service defaults, it will then apply the specific metric defaults if they are provided.

| Alarm Property         | Default Value                   |
| :--------------------- | :------------------------------ |
| **Statistic**          | `Average`                       |

## Default Alarm Metrics

Unless there is a tag override, each resource that is monitored will be bootstrapped with the default alarm metrics.

- `ApplicationRequests2xx`
- `ApplicationRequests3xx`
- `ApplicationRequests4xx`
- `ApplicationRequests5xx`

## Supported Metrics

### `ApplicationRequests2xx`

!!!light defaults
| Alarm Property | Default Value | Notes                                    |
| :------------- | :------------ | ---------------------------------------- |
| TBD  |           |  |
!!!

### `ApplicationRequests3xx`

!!!light defaults
| Alarm Property | Default Value | Notes                                    |
| :------------- | :------------ | ---------------------------------------- |
| TBD  |           |  |
!!!

### `ApplicationRequests4xx`

!!!light defaults
| Alarm Property | Default Value | Notes                                    |
| :------------- | :------------ | ---------------------------------------- |
| TBD  |           |  |
!!!

### `ApplicationRequests5xx`

!!!light defaults
| Alarm Property | Default Value | Notes                                    |
| :------------- | :------------ | ---------------------------------------- |
| TBD  |           |  |
!!!