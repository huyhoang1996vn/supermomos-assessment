# routes/email_status.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from routes.base_models import EmailStatusResponse, EmailStatusListResponse
from database.dynamodb import DynamoDB
from typing import Optional, List
from settings import get_dynamodb_resource, ENVIRONMENT

# Configure AWS region - you can change this to your preferred region
dynamodb = get_dynamodb_resource()
email_status_table = dynamodb.Table(f"EmailStatus-{ENVIRONMENT}")
email_status_db = DynamoDB(email_status_table)

email_status_router = APIRouter(prefix="/email-status", tags=["email-status"])


@email_status_router.get("/{user_id}", response_model=EmailStatusResponse)
async def get_email_status(user_id: str):
    """
    Get email status for a specific email address
    """
    try:
        # Query the table using the email as the primary key
        email_status = email_status_db.get_object(user_id, key_name='userId')
        
        if not email_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Email status not found for {user_id}"
            )
        
        return email_status
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving email status: {str(e)}"
        )


@email_status_router.get("/", response_model=EmailStatusListResponse)
async def get_all_email_status():
    """
    Get all email status records with optional filtering
    """
    try:
        # Get all items from the table
        items = email_status_db.get_all_objects()
        
        # Sort by creation date (newest first)
        items.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
        
        return EmailStatusListResponse(
            items=items,
            total_count=len(items)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving email status records: {str(e)}"
        )
