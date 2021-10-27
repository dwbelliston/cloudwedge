#!/bin/bash

# Deploy resources for hosting the docs


ARTIFACT_BUCKET="cldwdg-west-dev-bucket-artifacts"
ARTIFACT_BUCKET_PREFIX="local"
STACK_NAME="cloudwedge-docs"
CAPABILITIES="CAPABILITY_IAM"

pwd
ls

echo $TARGET_ENV

# sam deploy -t "./publishing/docs-infra.yaml" --stack-name $STACK_NAME --no-confirm-changeset --s3-bucket $ARTIFACT_BUCKET --s3-prefix $ARTIFACT_BUCKET_PREFIX --capabilities $CAPABILITIES --force-upload --no-fail-on-empty-changeset