# routes/users.py
import uuid
from typing import Dict, List, Literal, Optional
from fastapi import (APIRouter, BackgroundTasks, Depends, HTTPException, Query,
                     status)

from database.dynamodb import DynamoDB
from routes.base_models import (EmailRequest, EmailResponse,
                                PaginatedUserResponse, UserCreate,
                                UserEventRelationship, UserResponse,
                                UserUpdate)
from services.email_service import EmailService
from settings import ENVIRONMENT, get_dynamodb_resource

# Configure AWS region - you can change this to your preferred region
dynamodb = get_dynamodb_resource()
table = dynamodb.Table(f"Users-{ENVIRONMENT}")
user_db = DynamoDB(table)
user_event_table = dynamodb.Table(f"UserEventRelationship-{ENVIRONMENT}")
user_event_db = DynamoDB(user_event_table)
usersrouter = APIRouter(prefix="/users", tags=["users"])

# Initialize email service
email_service = EmailService()


def send_emails_background(
    recipients: List[Dict],
    subject: str,
    body: str,
    from_email: Optional[str] = None,
    from_name: Optional[str] = None
):
    """
    Background task to send emails asynchronously
    """
    try:
        result = email_service.send_emails(
            recipients=recipients,
            subject=subject,
            body=body,
            from_email=from_email,
            from_name=from_name
        )
        print(f"Background email sending completed: {result}")
    except Exception as e:
        print(f"Background email sending failed: {str(e)}")


@usersrouter.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    user_id = str(uuid.uuid4())
    user_data = user.dict()
    user_data["id"] = user_id
    created_user = user_db.create_object(user_data)
    return created_user


@usersrouter.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    user = user_db.get_object(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@usersrouter.get("/", response_model=list[UserResponse])
async def get_all_users():
    users = user_db.get_all_objects()
    return users

@usersrouter.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user: UserUpdate):
    update_data = user.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided for update")

    updated_user = user_db.update_object(user_id, update_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@usersrouter.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str):
    user_db.delete_object(user_id)
    return None


@usersrouter.patch("/{user_id}/join/{event_id}", response_model=UserEventRelationship)
async def patch_user(user_id: str, event_id: str, relationship_type: Literal["host", "attendee"]):
    user_event_relationship = UserEventRelationship(userId=user_id, eventId=event_id, relationshipType=relationship_type)
    data = user_event_relationship.dict()
    data["id"] = str(uuid.uuid4())
    new_obj = user_event_db.create_object(data)
    if relationship_type == "host":
        user_db.update_object(user_id, {"number_of_events_hosted": user_db.get_object(user_id).get("number_of_events_hosted", 0) + 1})
    elif relationship_type == "attendee":
        user_db.update_object(user_id, {"number_of_events_attended": user_db.get_object(user_id).get("number_of_events_attended", 0) + 1})
    return new_obj


@usersrouter.get("/list/", response_model=PaginatedUserResponse)
async def filter_users2(
    company: Optional[str] = Query(None, description="Filter by company name"),
    job_title: Optional[str] = Query(None, description="Filter by job title", alias="jobTitle"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query(None, description="Filter by state"),
    min_hosted: Optional[int] = Query(None, description="Minimum events hosted"),
    max_hosted: Optional[int] = Query(None, description="Maximum events hosted"),
    min_attended: Optional[int] = Query(None, description="Minimum events attended"),
    max_attended: Optional[int] = Query(None, description="Maximum events attended"),
    sort_by: Optional[str] = Query("createdAt", description="Field to sort by"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    pagesize: int = Query(20, ge=1, le=100, description="Number of items per page"),
):
    try:
        # If no filters provided, get all users
        if not any([company, job_title, city, state, min_hosted, max_hosted, min_attended, max_attended]):
            all_users = user_db.get_all_objects()
        else:
            all_users = user_db.query_employees_by_index(
                company=company,
                job_title=job_title,
                city=city,
                state=state,
                min_hosted=min_hosted,
                max_hosted=max_hosted,
                min_attended=min_attended,
                max_attended=max_attended
            )
        
        # Sort the users
        reverse = sort_order == "desc"
        all_users.sort(key=lambda x: x.get(sort_by, ""), reverse=reverse)
        
        # Calculate pagination metadata
        total_count = len(all_users)
        total_pages = (total_count + pagesize - 1) // pagesize  # Ceiling division
        offset = (page - 1) * pagesize
        
        # Get the current page of users
        paginated_users = all_users[offset:offset + pagesize]
        
        # Calculate pagination flags
        has_next = page < total_pages
        has_previous = page > 1
        
        return PaginatedUserResponse(
            items=paginated_users,
            total_count=total_count,
            page=page,
            pagesize=pagesize,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@usersrouter.post("/send-email/", response_model=EmailResponse)
async def send_email_to_users(
    background_tasks: BackgroundTasks,
    email_request: EmailRequest,
    company: Optional[str] = Query(None, description="Filter by company name"),
    job_title: Optional[str] = Query(None, description="Filter by job title", alias="jobTitle"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query(None, description="Filter by state"),
    min_hosted: Optional[int] = Query(None, description="Minimum events hosted"),
    max_hosted: Optional[int] = Query(None, description="Maximum events hosted"),
    min_attended: Optional[int] = Query(None, description="Minimum events attended"),
    max_attended: Optional[int] = Query(None, description="Maximum events attended"),
):
    """
    Send emails to users based on filter criteria.
    
    This endpoint allows you to send emails to users that match specific filter criteria.
    If no filters are provided, emails will be sent to all users (up to the limit).
    """
    try:
        # Get users based on filter criteria
        if not any([company, job_title, city, state, min_hosted, max_hosted, min_attended, max_attended]):
            # If no filters, get all users
            users = user_db.get_all_objects()
        else:
            # Apply filters
            users = user_db.query_employees_by_index(
                company=company,
                job_title=job_title,
                city=city,
                state=state,
                min_hosted=min_hosted,
                max_hosted=max_hosted,
                min_attended=min_attended,
                max_attended=max_attended
            )
        
        if not users:
            return EmailResponse(
                message="No users found matching the filter criteria",
                recipients_count=0,
                sent_count=0,
                failed_count=0,
                failed_emails=[]
            )
        
        # Prepare recipients list
        recipients = [{"email": user["email"], "userId": user["id"]} for user in users if user.get("email")]
        
        if not recipients:
            return EmailResponse(
                message="No valid email addresses found among matching users",
                recipients_count=0,
                sent_count=0,
                failed_count=0,
                failed_emails=[]
            )
        
        # Add email sending to background tasks
        background_tasks.add_task(
            send_emails_background,
            recipients=recipients,
            subject=email_request.subject,
            body=email_request.body,
        )
        
        return EmailResponse(
            message=f"Email campaign started in background. {len(recipients)} recipients will be notified.",
            recipients=recipients
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
