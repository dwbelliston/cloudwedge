#!/bin/bash

# For local deploy, when you want to deploy straight to aws

ARTIFACT_BUCKET="cldwdg-west-dev-bucket-artifacts"
ARTIFACT_BUCKET_PREFIX="local"
STACK_NAME="cloudwedge"
CAPABILITIES="CAPABILITY_IAM"

pwd
ls

sam deploy -t "./publishing/publishing.yaml" --stack-name $STACK_NAME --no-confirm-changeset --s3-bucket $ARTIFACT_BUCKET --s3-prefix $ARTIFACT_BUCKET_PREFIX --capabilities $CAPABILITIES --force-upload
