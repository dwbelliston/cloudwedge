# if gitlab is down, this can be run to deploy cloudwedge still


# What env to simulate?
ENV="prd" # prd | dev

# What regions
REGIONS=us-west-2

ARTIFACT_BUCKET=cloudwedge-public-artifacts
# Putting it in public folder, since the bucket policy has open access to public
ARTIFACT_BUCKET_PREFIX=public/cloudwedge
CAPABILITIES=CAPABILITY_IAM
ACL=public-read

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


./publishing/scripts/build.sh


# Publish
for REGION in "${REGION_LIST[@]}"; do
    echo "${CYAN}================ Publishing to $REGION ================${NOCOLOR}"
    echo "${BLUE}Removing old version files (if they exist)...${NOCOLOR}"
    aws s3 rm --recursive s3://${ARTIFACT_BUCKET}-${REGION}/$ARTIFACT_BUCKET_PREFIX/$VERSION/ --region $REGION
    echo "${BLUE}Publishing SAM package to S3 bucket ${ARTIFACT_BUCKET}-${REGION}...${NOCOLOR}"
    sam package --s3-bucket ${ARTIFACT_BUCKET}-${REGION} --s3-prefix $ARTIFACT_BUCKET_PREFIX/$VERSION --output-template-file cloudwedge-$VERSION.yaml --region $REGION
    echo "${BLUE}Setting ACLs on SAM packaged files...${NOCOLOR}"
    objects=($(aws s3api list-objects-v2 --bucket ${ARTIFACT_BUCKET}-${REGION} --prefix $ARTIFACT_BUCKET_PREFIX/$VERSION --query 'Contents[].Key' --output text))
    for obj in "${objects[@]}"; do echo "- Putting $ACL acl on $obj"; aws s3api put-object-acl --acl $ACL --bucket ${ARTIFACT_BUCKET}-${REGION} --key $obj --region $REGION; done
    echo "${BLUE}Uploading hub template file...${NOCOLOR}"
    aws s3 cp cloudwedge-$VERSION.yaml s3://${ARTIFACT_BUCKET}-${REGION}/$ARTIFACT_BUCKET_PREFIX/$VERSION/ --region $REGION --acl $ACL
    echo "${BLUE}Uploading spoke template file...${NOCOLOR}"
    aws s3 cp app/cloudwedge-spoke.yaml s3://${ARTIFACT_BUCKET}-${REGION}/$ARTIFACT_BUCKET_PREFIX/$VERSION/ --region $REGION --acl $ACL
    echo "${BLUE}Syncing media to public s3 bucket media folder...${NOCOLOR}"
    aws s3 sync ./publishing/media s3://${ARTIFACT_BUCKET}-${REGION}/$ARTIFACT_BUCKET_PREFIX/media/$ENV --acl public-read --delete
done
