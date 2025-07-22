#!/bin/bash

# SAM Deployment Script

set -e

# Configuration
STACK_NAME="dynamodb"
TEMPLATE_FILE="sam_templates/template.yaml"
REGION="ap-southeast-1"
ENVIRONMENT=${1:-dev}

echo "🚀 Deploying DynamoDB tables to AWS..."
echo "Environment: $ENVIRONMENT"
echo "Region: $REGION"
echo "Stack Name: $STACK_NAME"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if SAM CLI is installed
if ! command -v sam &> /dev/null; then
    echo "❌ AWS SAM CLI is not installed. Please install it first."
    echo "Install with: pip install aws-sam-cli"
    exit 1
fi

# Validate template
echo "📋 Validating SAM template..."
sam validate --template-file $TEMPLATE_FILE

# Build the application
echo "🔨 Building SAM application..."
sam build --template-file $TEMPLATE_FILE

# Deploy the stack
echo "☁️ Deploying to AWS..."
sam deploy \
    --template-file $TEMPLATE_FILE \
    --stack-name $STACK_NAME \
    --parameter-overrides EnvironmentType=$ENVIRONMENT \
    --capabilities CAPABILITY_IAM \
    --region $REGION \
    --no-fail-on-empty-changeset

echo "✅ Deployment completed successfully!"
echo ""
echo "📊 Stack outputs:"
aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs' \
    --output table

echo ""
echo "🔗 DynamoDB Tables:"
echo "Users Table: $(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query 'Stacks[0].Outputs[?OutputKey==`UsersTableName`].OutputValue' --output text)"
echo "Events Table: $(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query 'Stacks[0].Outputs[?OutputKey==`EventsTableName`].OutputValue' --output text)" 