# models/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Literal
from enum import Enum
from datetime import datetime

class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"
    prefer_not_to_say = "prefer_not_to_say"

class UserBase(BaseModel):
    firstName: str = Field(..., min_length=1, max_length=50)
    lastName: str = Field(..., min_length=1, max_length=50)
    phoneNumber: Optional[str] = Field(..., min_length=1, max_length=50)
    email: EmailStr
    avatar: Optional[str] = None
    gender: Optional[Gender] = None
    jobTitle: Optional[str] = None
    company: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    number_of_events_hosted: Optional[int] = 0
    number_of_events_attended: Optional[int] = 0

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    firstName: Optional[str] = Field(None, min_length=1, max_length=50)
    lastName: Optional[str] = Field(None, min_length=1, max_length=50)
    phoneNumber: Optional[str] = Field(..., min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    avatar: Optional[str] = None
    gender: Optional[Gender] = None
    jobTitle: Optional[str] = None
    company: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None

class UserInDB(UserBase):
    id: str

class UserResponse(UserInDB):
    pass

# Event Models
class EventBase(BaseModel):
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    startAt: datetime
    endAt: datetime
    venue: Optional[str] = None
    maxCapacity: Optional[int] = Field(None, ge=1)
    owner: str = Field(..., min_length=1)

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    startAt: Optional[datetime] = None
    endAt: Optional[datetime] = None
    venue: Optional[str] = None
    maxCapacity: Optional[int] = Field(None, ge=1)
    owner: Optional[str] = Field(None, min_length=1)

class EventInDB(EventBase):
    id: str

class EventResponse(EventInDB):
    pass

class UserEventRelationship(BaseModel):
    userId: str
    eventId: str
    relationshipType: Literal["host", "attendee"]
    createdAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    
    
class PaginatedUserResponse(BaseModel):
    items: List[UserResponse]
    total_count: int
    page: int
    pagesize: int
    total_pages: int
    has_next: bool
    has_previous: bool


class EmailRequest(BaseModel):
    subject: str = Field(..., min_length=1, max_length=200, description="Email subject")
    body: str = Field(..., min_length=1, description="Email body content")
    # from_email: Optional[str] = Field(None, description="From email address (optional)")
    # from_name: Optional[str] = Field(None, description="From name (optional)")

class EmailResponse(BaseModel):
    message: str
    recipients: List[dict]

# Email Status Models
class EmailStatusBase(BaseModel):
    email: EmailStr
    userId: str
    status: Literal["sent", "failed"]
    createdAt: str


class EmailStatusInDB(EmailStatusBase):
    pass

class EmailStatusResponse(EmailStatusInDB):
    pass

class EmailStatusListResponse(BaseModel):
    items: List[EmailStatusResponse]
    total_count: int