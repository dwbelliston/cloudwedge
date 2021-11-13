---
layout: central
---

# Contributing

Some information about how to contribute to the project.

## Updating the templates

- `/app/cloudwedge.yaml` is the main file that creates the step function and lambdas that are the brain of the wedge. It also creates (conditionally) a stackset which references the `cloudwedge-spoke.yaml`

- `/app/cloudwedge-spoke.yaml` is the spoke template that is deployed out to the accounts to monitor. This template creates an event rule that will capturest he relavent events and then forward events to the hub.
