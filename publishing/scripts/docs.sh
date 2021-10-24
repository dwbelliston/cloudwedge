#!/bin/bash

ARTIFACT_BUCKET="cloudwedge.1strategy.com"
# ARTIFACT_BUCKET="cloudwedge.1strategy-sandbox.com"
DOCS_SITE_FOLDER="site"

echo "✨ - Syncing site to s3 $ARTIFACT_BUCKET"
aws s3 sync $DOCS_SITE_FOLDER s3://$ARTIFACT_BUCKET/ --acl public-read --delete