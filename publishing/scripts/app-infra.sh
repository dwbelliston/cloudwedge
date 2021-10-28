#!/bin/bash

# Build the infra to host the bundled app


# What env to simulate?
ENV=$TARGET_ENV

# What regions
REGIONS=us-west-2,us-east-1
STACK_NAME=cloudwedge-app-infra
TEMPLATE_FILE=publishing/cw-artifact-bucket.yaml

RED='\033[01;31m'
GREEN='\033[01;32m'
YELLOW='\033[01;33m'
BLUE='\033[01;34m'
PURPLE='\033[01;35m'
CYAN='\033[01;36m'
NOCOLOR='\033[0m'


# Get the list of regions
temp="$(echo $REGIONS | tr -d '[:space:]')";
IFS=","; read -ra REGION_LIST <<< "$temp"; unset IFS

VERSION=$(cat package.json | python -c "import sys, json; print(json.load(sys.stdin)['version'])") && echo $VERSION


# Publish
for REGION in "${REGION_LIST[@]}"; do
    echo "${CYAN}================ Publishing to $REGION ================${NOCOLOR}"

    echo -e "${CYAN}Deploying publishing infra to ${REGION}${NOCOLOR}";
    aws cloudformation deploy \
        --stack-name $STACK_NAME \
        --region $REGION \
        --template-file "$TEMPLATE_FILE" \
        --parameter-overrides Env=$TARGET_ENV \
        --no-fail-on-empty-changeset;
done
