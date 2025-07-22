# routes/events.py
from fastapi import APIRouter, Depends, HTTPException, status
from routes.base_models import EventCreate, EventUpdate, EventResponse
import uuid
from datetime import datetime
from settings import get_dynamodb_resource, ENVIRONMENT
from database.dynamodb import DynamoDB


dynamodb = get_dynamodb_resource()
table = dynamodb.Table(f"Events-{ENVIRONMENT}")
event_db = DynamoDB(table)
user_event_table = dynamodb.Table(f"UserEventRelationship-{ENVIRONMENT}")
user_event_db = DynamoDB(user_event_table)
eventsrouter = APIRouter(prefix="/events", tags=["events"])


@eventsrouter.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(event: EventCreate):
    event_id = str(uuid.uuid4())
    event_data = event.dict()
    event_data['id'] = event_id
    
    # Convert datetime objects to ISO format strings for DynamoDB
    if event_data.get('startAt'):
        event_data['startAt'] = event_data['startAt'].isoformat()
    if event_data.get('endAt'):
        event_data['endAt'] = event_data['endAt'].isoformat()
    
    created_event = event_db.create_object(event_data)
    return created_event

@eventsrouter.get("/", response_model=list[EventResponse])
async def get_all_events():
    events = event_db.get_all_objects()
    return events

@eventsrouter.get("/{event_id}")
async def get_event(event_id: str):
    event = event_db.get_object(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    event_data = EventResponse(**event).model_dump()
    users = user_event_db.get_object_by_index('EventIdIndex', 'eventId', event_id)
    hosts = []
    attendees = []
    for user in users:
        if user['relationshipType'] == 'host':
            hosts.append(user['userId'])
        elif user['relationshipType'] == 'attendee':
            attendees.append(user['userId'])
    event_data['hosts'] = hosts
    event_data['attendees'] = attendees
    return event_data

@eventsrouter.get("/slug/{slug}")
async def get_event_by_slug(slug: str):
    event = event_db.get_object_by_slug(slug)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@eventsrouter.put("/{event_id}", response_model=EventResponse)
async def update_event(event_id: str, event: EventUpdate):
    update_data = event.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided for update")
    
    # Convert datetime objects to ISO format strings for DynamoDB
    if update_data.get('startAt'):
        update_data['startAt'] = update_data['startAt'].isoformat()
    if update_data.get('endAt'):
        update_data['endAt'] = update_data['endAt'].isoformat()
    
    updated_event = event_db.update_object(event_id, update_data)
    if not updated_event:
        raise HTTPException(status_code=404, detail="Event not found")
    return updated_event

@eventsrouter.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(event_id: str):
    event_db.delete_object(event_id)
    return None 