#!/bin/bash

# Sync docs site to s3

CYAN='\033[01;36m'
NOCOLOR='\033[0m'

WEBROOT_BUCKET=cw-east-$TARGET_ENV-bucket-web-root
WEBROOT_LOCALFOLDER="docsbuilt"


echo -e "${CYAN}Syncing docs to ${WEBROOT_BUCKET}${NOCOLOR}";

ls
pwd
ls node_modules

echo "---"

which retype
echo "---"

npx retype build

echo "---"
aws s3 sync docs s3://$WEBROOT_BUCKET --delete --sse aws:kms
# aws s3 sync $WEBROOT_LOCALFOLDER s3://$WEBROOT_BUCKET --delete --sse aws:kms
