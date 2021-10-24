---
order: 90
icon: tag
label: Tags
tags: [guide]
---

# Tags

CloudWedge is built on the pattern of tagging resources. This is the master list of tags that are supported and can be used to fine tune your alarms.

### Core Tags

==- [!badge variant="primary" icon="tag" iconAlign="left" text="cloudwedge:active"]

#### Tag Name

```text
cloudwedge:active
```

#### Tag Details

|         |                 |
| :------------ | :--------------------------|
| **Required**    | :icon-verified: |
| **Description** | This tag controls if the resource should be included as candidate for alarms. Without this tag the cloudwedge will not identify this resource as in scope. |
| **Default**     | No default, its either on or off |
| **Values**      | Only the value "true" will mark the resource as in scope for alarms. Any other value will not considered. |
| **Example**     | `true` |

==- [!badge variant="primary" icon="tag" iconAlign="left" text="cloudwedge:owner"]

#### Tag Name

```text
cloudwedge:owner
```

#### Tag Details

|         |                 |
| :------------ | :--------------------------|
| **Required**    | :icon-x-16: |
| **Description** | Tag determines what owner the alerts will be marked with. You can use this owner to filter alerting methods to specifc owners. For example, you may want to receive a text just for systems you own. |
| **Default**     | `cloudwedge` |
| **Values**      | any string |
| **Example**     | `customers-microservice` |

==- [!badge variant="primary" icon="tag" iconAlign="left" text="cloudwedge:level"]

#### Tag Name

```text
cloudwedge:level
```

#### Tag Details

|         |                 |
| :------------ | :--------------------------|
| **Required**    | :icon-x-16: |
| **Description** | Tag determines what level the alerts will be marked as. You can use this level to filter alerting methods to specifc levels. For example, you may want to receive a text just for critical alerts. |
| **Default**     | `medium` |
| **Values**      | `critical` `high` `medium` `low` |
| **Example**     | `critical` |

===

### Setting Metrics

==- [!badge variant="primary" icon="tag" iconAlign="left" text="cloudwedge:metrics"]

#### Tag Name

```text
cloudwedge:metrics
```

#### Tag Details

|         |                 |
| :------------ | :--------------------------|
| **Required**    | :icon-x-16: |
| **Description** | Tag determines what metrics should be created for this resource. This overrides the default metrics for the service. |
| **Default**     | Defaults to service level default metrics |
| **Values**      | An array of supported service metrics separated with a `|` |
| **Example**     | `CPUUtilization | DiskReadOps` |

==- [!badge variant="primary" icon="tag" iconAlign="left" text="cloudwedge:metrics:[ critical | high | medium | low ]"]

#### Tag Names

```text
cloudwedge:metrics:critical
```

```text
cloudwedge:metrics:high
```

```text
cloudwedge:metrics:medium
```

```text
cloudwedge:metrics:low
```

#### Tag Details

|         |                 |
| :------------ | :--------------------------|
| **Required**    | :icon-x-16: |
| **Description** | You can use these tags to separate the criticality of different metrics. Lets say you want CPUUtilization to be a `critical` metric for a given resource, but the other metrics are just `high`. You can use these tags and list the metrics for each level. |
| **Default**     | None |
| **Values**      | An array of supported service metrics separated with a `|` |
| **Example**     | `CPUUtilization | DiskReadOps` |

===

### Alarm Overrides

==- [!badge variant="primary" icon="tag" iconAlign="left" text="cloudwedge:alarm:prop:`CloudFormationProperty`"]

#### Tag Prefix

```text
cloudwedge:alarm:prop:
```

#### Tag Examples

```text
cloudwedge:alarm:prop:Threshold
```

```text
cloudwedge:alarm:prop:Period
```

#### Tag Details

|                 |                                                                                                                                                                  |
| :-------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Required**    | :icon-x:                                                                                                                                                  |
| **Description** | Tag determines what the default property on the CloudFormation alarms will be. This is a quick way to change the property value for all metrics on the resource. |
| **Default**     | None                                                                                                                                                             |
| **Values**      | Refer to the [CloudFormation property documentation](../alarms/#alarm-anatomy) to see what values are valid for the property.                                  |
| **Example**     | `cloudwedge:alarm:prop:Threshold` = `80`                                                                                                                           |

==- [!badge variant="primary" icon="tag" iconAlign="left" text="cloudwedge:alarm:metric:`MetricName`:prop:`CloudFormationProperty`"]

#### Tag Pattern

```text
cloudwedge:alarm:metric:MetricName:prop:CloudFormationProperty
```

#### Tag Examples

```text
cloudwedge:alarm:metric:CPUUtilization:prop:Threshold
```

```text
cloudwedge:alarm:metric:ExecutionsFailed:prop:EvaluationPeriods
```

```text
cloudwedge:alarm:metric:ApplicationRequests3xx:prop:Period
```

#### Tag Details

|                 |                                                                                                                                 |
| :-------------- | :------------------------------------------------------------------------------------------------------------------------------ |
| **Required**    | :icon-x:                                                                                                                 |
| **Description** | Tag allows to target a specific metric's property and overide it with a new value.                                              |
| **Default**     | None                                                                                                                            |
| **Values**      | The metric must be listed as a supported metric for the service and the property must be a valid CloudFormation Alarm property. |
| **Example**     | `cloudwedge:alarm:metric:ExecutionsFailed:prop:EvaluationPeriods` = 5                                                           |

===

!!! secondary Param: `CloudFormationProperty`

`CloudFormationProperty` can be replaced with valid property names in the the [Alarms](./alarms.md/#alarm-anatomy) CloudFormation template. [CloudFormation property documentation](../alarms/#alarm-anatomy)

Examples:

- `Threshold`
- `EvaluationPeriods`
- `Period`
!!!

!!! secondary Param: `MetricName`

`MetricName` can be replaced with valid metric names. [Services list](../services/)

Examples:

- `CPUUtilization`
- `ExecutionsFailed`
- `ApplicationRequests3xx`

!!!