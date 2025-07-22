# 🚀 Project DynamoDB Deployment Guide

This guide will help you deploy your DynamoDB tables to AWS using AWS SAM (Serverless Application Model).

## 📋 Prerequisites

### 1. Install AWS CLI
```bash
# macOS (using Homebrew)
brew install awscli

# Or download from AWS website
# https://aws.amazon.com/cli/
```

### 2. Install AWS SAM CLI
```bash
# Using pip
pip install aws-sam-cli

# Or using Homebrew
brew install aws-sam-cli
```

### 3. Configure AWS Credentials
```bash
# Configure your AWS credentials
aws configure

# You'll be prompted for:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region (use: ap-southeast-1)
# - Default output format (use: json)
```

## 🔧 Environment Setup

### 1. Set Environment Variables
```bash
# Set your AWS region
export AWS_DEFAULT_REGION=ap-southeast-1

# Set your project name and environment
export PROJECT_NAME=project
export ENVIRONMENT=dev

# Set your AWS credentials (if not using aws configure)
export AWS_ACCESS_KEY_ID=your_access_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_key_here
```

### 2. Verify AWS Configuration
```bash
# Test your AWS configuration
aws sts get-caller-identity

# Should return your AWS account info
```

## 🚀 Deployment Steps

### Option 1: Using the Deployment Script (Recommended)

```bash
# Deploy to dev environment (default)
./deploy-db.sh

# Deploy to specific environment
./deploy-db.sh prod

# Deploy to staging
./deploy-db.sh staging
```

### Option 2: Manual Deployment

```bash
# 1. Validate the template
sam validate --template-file sam_templates/template.yaml

# 2. Build the application
sam build --template-file sam_templates/template.yaml

# 3. Deploy the stack
sam deploy \
    --template-file sam_templates/template.yaml \
    --stack-name dynamodb \
    --parameter-overrides EnvironmentType=dev \
    --capabilities CAPABILITY_IAM \
    --region ap-southeast-1 \
    --no-fail-on-empty-changeset
```

## 📊 What Gets Deployed

### DynamoDB Tables Created:
1. **Users Table** (`Users-dev`)
   - Primary Key: `id`
   - Indexes: EmailIndex, CompanyIndex, JobTitleIndex, CityStateIndex

2. **Events Table** (`Events-dev`)
   - Primary Key: `id`
   - Indexes: SlugIndex, OwnerIndex, StartAtIndex, VenueIndex

### Features:
- ✅ **Pay-per-request billing** (no upfront costs)
- ✅ **Server-side encryption** enabled
- ✅ **Streams enabled** for real-time updates
- ✅ **Global Secondary Indexes** for efficient queries
- ✅ **Environment-based naming** (dev/staging/prod)

## 🔍 Verification

### 1. Check CloudFormation Stack
```bash
aws cloudformation describe-stacks \
    --stack-name dynamodb \
    --region ap-southeast-1
```

### 2. List DynamoDB Tables
```bash
aws dynamodb list-tables --region ap-southeast-1
```

### 3. Check Table Details
```bash
# Check Users table
aws dynamodb describe-table \
    --table-name Users-dev \
    --region ap-southeast-1

# Check Events table
aws dynamodb describe-table \
    --table-name Events-dev \
    --region ap-southeast-1
```

## 🧹 Cleanup

### Delete the Stack
```bash
sam delete --stack-name dynamodb --region ap-southeast-1
```

### Or using AWS CLI
```bash
aws cloudformation delete-stack \
    --stack-name dynamodb \
    --region ap-southeast-1
```

## 🔧 Troubleshooting

### Common Issues:

1. **"Unable to locate credentials"**
   ```bash
   # Run aws configure
   aws configure
   ```

2. **"NoRegionError"**
   ```bash
   # Set region environment variable
   export AWS_DEFAULT_REGION=ap-southeast-1
   ```

3. **"Access Denied"**
   - Ensure your AWS user has DynamoDB permissions
   - Required permissions: `dynamodb:*`, `cloudformation:*`

4. **"Stack already exists"**
   ```bash
   # Delete existing stack first
   sam delete --stack-name dynamodb
   ```

## 📝 Environment Variables for Your App

After deployment, set these environment variables in your application:

```bash
export AWS_DEFAULT_REGION=ap-southeast-1
export PROJECT_NAME=project
export ENVIRONMENT=dev
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
```

## 🎯 Next Steps

1. **Test the API** with the deployed tables
2. **Monitor costs** in AWS Console
3. **Set up CloudWatch** for monitoring
4. **Configure backups** if needed
5. **Set up CI/CD** for automated deployments

## 📞 Support

If you encounter issues:
1. Check AWS CloudFormation console for stack events
2. Review CloudWatch logs
3. Verify AWS credentials and permissions
4. Check the troubleshooting section above 