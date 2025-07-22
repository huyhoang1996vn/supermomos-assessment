
import boto3
import os
from dotenv import load_dotenv

load_dotenv()
ENVIRONMENT = os.getenv('ENVIRONMENT', 'dev')

def get_dynamodb_resource():
    """Get DynamoDB resource using environment variables"""
    return boto3.resource(
        'dynamodb',
        region_name=os.environ.get('AWS_DEFAULT_REGION', 'ap-southeast-1'),
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    )