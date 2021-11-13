---
layout: central
---

# Contributing

Some information about how to contribute to the project.

## Updating the templates

- `/app/cloudwedge.yaml` is the main file that creates the step function and lambdas that are the brain of the wedge. It also creates (conditionally) a stackset which references the `cloudwedge-spoke.yaml`

- `/app/cloudwedge-spoke.yaml` is the spoke template that is deployed out to the accounts to monitor. This template creates an event rule that will capturest he relavent events and then forward events to the hub.


- Make changes to template
- Increment the version in `package.json` (as needed)
- Push code to `dev` branch
- Github actions will deploy template s3 in the wedge dev account
- You can now create the stack using the reference from the s3 account (swap region as needed)
`https://us-west-2.console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/create/template?stackName=cloudwedge&templateURL=https://cloudwedge-public-artifacts-dev-us-west-2.s3.amazonaws.com/public/cloudwedge/latest/cloudwedge.yaml`
- Remember, when creating the stack you need to change the `ENV` parameter to `dev`, so that it will look at the `dev` s3 bucket instead of the `prd` bucket
