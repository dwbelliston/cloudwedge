---
label: API Gateway
---

# API Gateway

[!badge icon="tools" text="In Progress" variant="warning"]

## CloudWatch Configuration

When a resource is monitored it is going to be using these CloudWatch configurations to identify the metric.

| `namespace`    | `dimension`     | `metrics`                                                                                                                            |
| -------------- | --------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| AWS/ApiGateway | EnvironmentName | [Available CloudWatch Metrics](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-metrics-and-dimensions.html) |

## Service Defaults

When an alarm is created it will first review the service defaults to populate the CloudWatch alarm properties. After the service defaults, it will then apply the specific metric defaults if they are provided.

| Alarm Property | Default Value |
| :------------- | :------------ |
| **Statistic**  | `Sum` |

## Default Alarm Metrics

Unless there is a tag override, each gateway that is monitored will be bootstrapped with the default alarm metrics.

- `Latency`
- `IntegrationLatency`
- `5XXError`
- `4XXError`

## Supported Metrics

### `Latency`

!!!light Defaults
| Alarm Property | Default Value | Notes |
| :------------- | :------------ | ----- |
| TBD            |               |       |
!!!

### `IntegrationLatency`

!!!light Defaults
| Alarm Property | Default Value | Notes |
| :------------- | :------------ | ----- |
| TBD            |               |       |
!!!

### `5XXError`

!!!light Defaults
| Alarm Property | Default Value | Notes |
| :------------- | :------------ | ----- |
| TBD            |               |       |
!!!

### `4XXError`

!!!light Defaults
| Alarm Property | Default Value | Notes |
| :------------- | :------------ | ----- |
| TBD            |               |       |
!!!
