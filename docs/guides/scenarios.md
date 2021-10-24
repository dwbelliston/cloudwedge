---
order: 70
icon: milestone
tags: [guide, examples]
description: This is a custom description for this page
label: Scenarios
---

# Scenarios

A showcase on ways to use tags to get your desired configuration.

## Monitoring resource with owner


+++ Opt-In

[!badge variant="primary" icon="tag" iconAlign="left" text="cloudwedge:active"]

Tag Key
```
cloudwedge:active
```

Tag Value
```
true
```

+++ Assign Owner

[!badge variant="primary" icon="tag" iconAlign="left" text="cloudwedge:owner"]

Tag Key
```
cloudwedge:owner
```

Tag Value
```
:string
```
+++

## Monitoring resource with owner and critical level


+++ Opt-In

[!badge variant="primary" icon="tag" iconAlign="left" text="cloudwedge:active"]

Tag Key
```
cloudwedge:active
```

Tag Value
```
true
```

+++ Assign Owner

[!badge variant="primary" icon="tag" iconAlign="left" text="cloudwedge:owner"]

Tag Key
```
cloudwedge:owner
```

Tag Value
```
:string
```

+++ Assign Level

[!badge variant="primary" icon="tag" iconAlign="left" text="cloudwedge:level"]

Tag Key
```
cloudwedge:level
```

Tag Value
```
critical
```
+++

## Monitor EC2 instance with certain metrics


+++ Opt-In

[!badge variant="primary" icon="tag" iconAlign="left" text="cloudwedge:active"]

Tag Key
```
cloudwedge:active
```

Tag Value
```
true
```

+++ Assign Owner

[!badge variant="primary" icon="tag" iconAlign="left" text="cloudwedge:owner"]

Tag Key
```
cloudwedge:owner
```

Tag Value
```
:string
```

+++ Assign Metrics

[!badge variant="primary" icon="tag" iconAlign="left" text="cloudwedge:metrics"]

Tag Key
```
cloudwedge:metrics
```

Tag Value
```
CPUUtilization | NetworkIn | NetworkOut
```
+++

## Monitor EC2 instance with property overrides


+++ Opt-In

[!badge variant="primary" icon="tag" iconAlign="left" text="cloudwedge:active"]

Tag Key
```
cloudwedge:active
```

Tag Value
```
true
```

+++ Assign Owner

[!badge variant="primary" icon="tag" iconAlign="left" text="cloudwedge:owner"]

Tag Key
```
cloudwedge:owner
```

Tag Value
```
:string
```

+++ Assign Prop Override

[!badge variant="primary" icon="tag" iconAlign="left" text="cloudwedge:alarm:prop:Period"]

Tag Key
```
cloudwedge:alarm:prop:Period
```

Tag Value
```
10
```

+++ Assign Metric Override

[!badge variant="primary" icon="tag" iconAlign="left" text="cloudwedge:alarm:metric:CPUUtilization:prop:Threshold"]

Tag Key
```
cloudwedge:alarm:metric:CPUUtilization:prop:Threshold
```

Tag Value
```
78
```
+++
