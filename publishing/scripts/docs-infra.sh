#!/bin/bash

# Deploy resources for hosting the docs


CYAN='\033[01;36m'
NOCOLOR='\033[0m'
ARTIFACT_BUCKET=cldwdg-west-$TARGET_ENV-bucket-artifacts
ARTIFACT_BUCKET_PREFIX="/docs-infra"
CAPABILITIES="CAPABILITY_IAM"
STACK_NAME="cloudwedge-docs-infra"
SOURCE_TEMPLATE="./publishing/docs-infra.yaml"
REGION="us-east-1"


echo -e "${CYAN}Deploying docs infra to ${TARGET_ENV}${NOCOLOR}";
echo -e "${CYAN}Deploying docs infra to ${ARTIFACT_BUCKET}${NOCOLOR}";


sam deploy -t $SOURCE_TEMPLATE --stack-name $STACK_NAME --no-confirm-changeset --s3-bucket $ARTIFACT_BUCKET --force-upload --no-fail-on-empty-changeset --parameter-overrides Env=$TARGET_ENV --region $REGION
# --s3-prefix $ARTIFACT_BUCKET_PREFIX