#!/bin/bash

# Package the lambda functions assets to s3 and then copy the
# packaged yaml, which references those s3 lambda functions, to
# the same s3 location, so the cloudformation can be deployed
# using the s3 file

CURRENT_VERSION=$(npm run version --silent)
ARTIFACT_BUCKET=1s-public-cloudformation
ARTIFACT_BUCKET_PREFIX=cloudwedge-versions/$CURRENT_VERSION
ARTIFACT_TEMPLATE_FILE=cloudwedge.yaml
TEMPLATE_OUTPUT_DIR=.out
TEMPLATE_OUTPUT_FILE=cloudwedge-packaged.$CURRENT_VERSION.yaml

echo "CloudWedge Publishing version $CURRENT_VERSION"

# Clear s3 target for this version
echo "🗑  - Prepare target for upload"
aws s3 rm s3://$ARTIFACT_BUCKET/$ARTIFACT_BUCKET_PREFIX/ --recursive

# Package the functions to s3
echo "📦 - Package artifacts"
# https://github.com/awslabs/aws-sam-cli/issues/978
mkdir -p $TEMPLATE_OUTPUT_DIR
sam package --s3-bucket $ARTIFACT_BUCKET --s3-prefix $ARTIFACT_BUCKET_PREFIX/src --output-template-file $TEMPLATE_OUTPUT_DIR/$TEMPLATE_OUTPUT_FILE --force-upload

# Copy the template to s3 next to the packages
echo "🚀 - Copy template to s3"
aws s3 cp $TEMPLATE_OUTPUT_DIR/$TEMPLATE_OUTPUT_FILE s3://$ARTIFACT_BUCKET/$ARTIFACT_BUCKET_PREFIX/$ARTIFACT_TEMPLATE_FILE

# # # Publish to AWS SAR
# # sam publish --template $TEMPLATE_OUTPUT_FILE --semantic-version 1.0.2 --region us-west-2

# # Sync media to s3
echo "🎞 - Upload the media files to s3"
aws s3 sync publishing/media s3://$ARTIFACT_BUCKET/$ARTIFACT_BUCKET_PREFIX/media --acl public-read --delete
