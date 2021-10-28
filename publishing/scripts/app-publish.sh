#!/bin/bash

# Build the infra to host the bundled app


# What env to simulate?
ENV=$TARGET_ENV

# What regions
REGIONS=us-west-2,us-east-1,us-east-2

ARTIFACT_BUCKET=cloudwedge-public-artifacts-$TARGET_ENV
# Putting it in public folder, since the bucket policy has open access to public
ARTIFACT_BUCKET_PREFIX=public/cloudwedge
ACL=public-read
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
    echo -e "${CYAN}================ Publishing to $REGION ================${NOCOLOR}"
    echo -e "${BLUE}Removing old version files (if they exist)...${NOCOLOR}"
    aws s3 rm --recursive s3://${ARTIFACT_BUCKET}-${REGION}/$ARTIFACT_BUCKET_PREFIX/$VERSION/ --region $REGION
    echo -e "${BLUE}Publishing SAM package to S3 bucket...${NOCOLOR}"
    sam package --s3-bucket ${ARTIFACT_BUCKET}-${REGION} --s3-prefix $ARTIFACT_BUCKET_PREFIX/$VERSION --output-template-file cloudwedge-$VERSION.yaml --region $REGION
    echo -e "${BLUE}Setting ACLs on SAM packaged files...${NOCOLOR}"
    objects=($(aws s3api list-objects-v2 --bucket ${ARTIFACT_BUCKET}-${REGION} --prefix $ARTIFACT_BUCKET_PREFIX/$VERSION --query 'Contents[].Key' --output text))
    for obj in "${objects[@]}"; do echo "- Putting $ACL acl on $obj"; aws s3api put-object-acl --acl $ACL --bucket ${ARTIFACT_BUCKET}-${REGION} --key $obj --region $REGION; done
    echo -e "${BLUE}Uploading template file...${NOCOLOR}"
    aws s3 cp cloudwedge-$VERSION.yaml s3://${ARTIFACT_BUCKET}-${REGION}/$ARTIFACT_BUCKET_PREFIX/$VERSION/ --region $REGION --acl $ACL
    echo -e "${BLUE}Syncing media to public s3 bucket media folder...${NOCOLOR}"
    aws s3 sync ./publishing/media s3://${ARTIFACT_BUCKET}-${REGION}/$ARTIFACT_BUCKET_PREFIX/media/$ENV --acl public-read --delete
    echo -e "${BLUE}Syncing media to public s3 bucket media folder...${NOCOLOR}"
    aws s3 cp s3://${ARTIFACT_BUCKET}-${REGION}/$ARTIFACT_BUCKET_PREFIX/$VERSION/cloudwedge-$VERSION.yaml s3://${ARTIFACT_BUCKET}-${REGION}/$ARTIFACT_BUCKET_PREFIX/latest/cloudwedge.yaml --region $REGION --acl $ACL
    aws s3 cp s3://${ARTIFACT_BUCKET}-${REGION}/$ARTIFACT_BUCKET_PREFIX/$VERSION/cloudwedge-spoke.yaml s3://${ARTIFACT_BUCKET}-${REGION}/$ARTIFACT_BUCKET_PREFIX/latest/cloudwedge-spoke.yaml --region $REGION --acl $ACL
done
