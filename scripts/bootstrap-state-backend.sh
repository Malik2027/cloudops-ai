#!/usr/bin/env bash
# Run this ONCE before any terraform init to create the S3 bucket used for
# remote state. Locking uses S3 native lock files (use_lockfile = true),
# so no DynamoDB table is needed.
#
# Prerequisites: AWS CLI configured with sufficient permissions
# Usage: bash scripts/bootstrap-state-backend.sh

set -euo pipefail

REGION="ap-south-1"
BUCKET="cloudops-ai-terraform-state"

echo "Creating S3 bucket: $BUCKET in $REGION"
aws s3api create-bucket \
  --bucket "$BUCKET" \
  --region "$REGION" \
  --create-bucket-configuration LocationConstraint="$REGION"

echo "Enabling versioning"
aws s3api put-bucket-versioning \
  --bucket "$BUCKET" \
  --versioning-configuration Status=Enabled

echo "Enabling server-side encryption"
aws s3api put-bucket-encryption \
  --bucket "$BUCKET" \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"},
      "BucketKeyEnabled": true
    }]
  }'

echo "Blocking public access"
aws s3api put-public-access-block \
  --bucket "$BUCKET" \
  --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

echo ""
echo "Bootstrap complete."
echo "  S3 bucket : $BUCKET"
echo "  Region    : $REGION"
echo ""
echo "Next steps:"
echo "  cd terraform/environments/dev && terraform init"
