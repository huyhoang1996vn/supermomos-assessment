#!/usr/bin/env python3
"""
Data Initialization Script for SuperMomo API
Populates the database with sample users, events, and relationships
"""

import uuid
import json
from datetime import datetime, timedelta
from typing import List, Dict
import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AWS Configuration
ENVIRONMENT = os.getenv('ENVIRONMENT', 'dev')
AWS_REGION = os.getenv('AWS_REGION', 'ap-southeast-1')

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)

# Table names
USERS_TABLE = f"Users-{ENVIRONMENT}"
EVENTS_TABLE = f"Events-{ENVIRONMENT}"
USER_EVENT_TABLE = f"UserEventRelationship-{ENVIRONMENT}"
EMAIL_STATUS_TABLE = f"EmailStatus-{ENVIRONMENT}"

def get_table(table_name: str):
    """Get DynamoDB table"""
    try:
        return dynamodb.Table(table_name)
    except ClientError as e:
        print(f"❌ Error accessing table {table_name}: {e}")
        return None

def create_user(table, user_data: Dict) -> str:
    """Create a user and return the user ID"""
    try:
        user_id = str(uuid.uuid4())
        user_data['id'] = user_id
        user_data['createdAt'] = datetime.now().isoformat()
        
        # Initialize event counters
        user_data['number_of_events_hosted'] = 0
        user_data['number_of_events_attended'] = 0
        
        table.put_item(Item=user_data)
        print(f"✅ Created user: {user_data['firstName']} {user_data['lastName']} ({user_id})")
        return user_id
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return None

def create_event(table, event_data: Dict) -> str:
    """Create an event and return the event ID"""
    try:
        event_id = str(uuid.uuid4())
        event_data['id'] = event_id
        event_data['createdAt'] = datetime.now().isoformat()
        
        table.put_item(Item=event_data)
        print(f"✅ Created event: {event_data['title']} ({event_id})")
        return event_id
    except Exception as e:
        print(f"❌ Error creating event: {e}")
        return None

def create_user_event_relationship(table, user_id: str, event_id: str, relationship_type: str) -> bool:
    """Create a user-event relationship"""
    try:
        relationship_id = str(uuid.uuid4())
        relationship_data = {
            'id': relationship_id,
            'userId': user_id,
            'eventId': event_id,
            'relationshipType': relationship_type,
            'createdAt': datetime.now().isoformat()
        }
        
        table.put_item(Item=relationship_data)
        print(f"✅ Created relationship: User {user_id} -> Event {event_id} ({relationship_type})")
        return True
    except Exception as e:
        print(f"❌ Error creating relationship: {e}")
        return False

def create_email_status(table, user_id: str, email: str, status: str) -> bool:
    """Create an email status record"""
    try:
        email_status_data = {
            'userId': user_id,
            'email': email,
            'status': status,
            'createdAt': datetime.now().isoformat()
        }
        
        table.put_item(Item=email_status_data)
        print(f"✅ Created email status: {email} ({status})")
        return True
    except Exception as e:
        print(f"❌ Error creating email status: {e}")
        return False

def update_user_event_counts(users_table, user_id: str, hosted_increment: int = 0, attended_increment: int = 0):
    """Update user's event count"""
    try:
        update_expression = "SET "
        expression_values = {}
        
        if hosted_increment > 0:
            update_expression += "number_of_events_hosted = number_of_events_hosted + :hosted"
            expression_values[':hosted'] = hosted_increment
        
        if attended_increment > 0:
            if hosted_increment > 0:
                update_expression += ", "
            update_expression += "number_of_events_attended = number_of_events_attended + :attended"
            expression_values[':attended'] = attended_increment
        
        users_table.update_item(
            Key={'id': user_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values
        )
        print(f"✅ Updated event counts for user {user_id}")
    except Exception as e:
        print(f"❌ Error updating event counts: {e}")

def main():
    """Main initialization function"""
    print("🚀 Starting SuperMomo Data Initialization...")
    print(f"Environment: {ENVIRONMENT}")
    print(f"Region: {AWS_REGION}")
    print("=" * 50)
    
    # Get tables
    users_table = get_table(USERS_TABLE)
    events_table = get_table(EVENTS_TABLE)
    user_event_table = get_table(USER_EVENT_TABLE)
    email_status_table = get_table(EMAIL_STATUS_TABLE)
    
    if not all([users_table, events_table, user_event_table, email_status_table]):
        print("❌ Failed to access one or more tables")
        return
    
    # Sample users data
    users_data = [
        {
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john.doe@google.com',
            'phoneNumber': '+1234567890',
            'jobTitle': 'Senior Software Engineer',
            'company': 'Google',
            'city': 'San Francisco',
            'state': 'CA',
            'gender': 'male'
        },
        {
            'firstName': 'Jane',
            'lastName': 'Smith',
            'email': 'jane.smith@facebook.com',
            'phoneNumber': '+1234567891',
            'jobTitle': 'Product Manager',
            'company': 'Facebook',
            'city': 'San Francisco',
            'state': 'CA',
            'gender': 'female'
        },
        {
            'firstName': 'Mike',
            'lastName': 'Johnson',
            'email': 'mike.johnson@apple.com',
            'phoneNumber': '+1234567892',
            'jobTitle': 'iOS Developer',
            'company': 'Apple',
            'city': 'Cupertino',
            'state': 'CA',
            'gender': 'male'
        },
        {
            'firstName': 'Sarah',
            'lastName': 'Wilson',
            'email': 'sarah.wilson@microsoft.com',
            'phoneNumber': '+1234567893',
            'jobTitle': 'Data Scientist',
            'company': 'Microsoft',
            'city': 'Seattle',
            'state': 'WA',
            'gender': 'female'
        },
        {
            'firstName': 'David',
            'lastName': 'Brown',
            'email': 'david.brown@amazon.com',
            'phoneNumber': '+1234567894',
            'jobTitle': 'Backend Engineer',
            'company': 'Amazon',
            'city': 'Seattle',
            'state': 'WA',
            'gender': 'male'
        },
        {
            'firstName': 'Emily',
            'lastName': 'Davis',
            'email': 'emily.davis@netflix.com',
            'phoneNumber': '+1234567895',
            'jobTitle': 'Frontend Engineer',
            'company': 'Netflix',
            'city': 'Los Gatos',
            'state': 'CA',
            'gender': 'female'
        },
        {
            'firstName': 'Alex',
            'lastName': 'Taylor',
            'email': 'alex.taylor@uber.com',
            'phoneNumber': '+1234567896',
            'jobTitle': 'DevOps Engineer',
            'company': 'Uber',
            'city': 'San Francisco',
            'state': 'CA',
            'gender': 'male'
        },
        {
            'firstName': 'Lisa',
            'lastName': 'Anderson',
            'email': 'lisa.anderson@airbnb.com',
            'phoneNumber': '+1234567897',
            'jobTitle': 'UX Designer',
            'company': 'Airbnb',
            'city': 'San Francisco',
            'state': 'CA',
            'gender': 'female'
        }
    ]
    
    # Sample events data
    events_data = [
        {
            'slug': 'tech-meetup-2024',
            'title': 'Tech Meetup 2024',
            'description': 'Join us for an exciting tech meetup with industry leaders',
            'startAt': (datetime.now() + timedelta(days=7)).isoformat(),
            'endAt': (datetime.now() + timedelta(days=7, hours=3)).isoformat(),
            'venue': 'Tech Hub San Francisco',
            'maxCapacity': 100,
            'owner': '',  # Will be set after user creation
            'hosts': []
        },
        {
            'slug': 'ai-workshop',
            'title': 'AI Workshop',
            'description': 'Hands-on workshop on machine learning and AI',
            'startAt': (datetime.now() + timedelta(days=14)).isoformat(),
            'endAt': (datetime.now() + timedelta(days=14, hours=4)).isoformat(),
            'venue': 'Innovation Center',
            'maxCapacity': 50,
            'owner': '',
            'hosts': []
        },
        {
            'slug': 'startup-networking',
            'title': 'Startup Networking Event',
            'description': 'Connect with fellow entrepreneurs and investors',
            'startAt': (datetime.now() + timedelta(days=21)).isoformat(),
            'endAt': (datetime.now() + timedelta(days=21, hours=2)).isoformat(),
            'venue': 'Startup Incubator',
            'maxCapacity': 75,
            'owner': '',
            'hosts': []
        },
        {
            'slug': 'design-thinking',
            'title': 'Design Thinking Workshop',
            'description': 'Learn design thinking methodologies',
            'startAt': (datetime.now() + timedelta(days=28)).isoformat(),
            'endAt': (datetime.now() + timedelta(days=28, hours=3)).isoformat(),
            'venue': 'Design Studio',
            'maxCapacity': 30,
            'owner': '',
            'hosts': []
        }
    ]
    
    print("👥 Creating users...")
    user_ids = []
    for user_data in users_data:
        user_id = create_user(users_table, user_data)
        if user_id:
            user_ids.append(user_id)
    
    print(f"\n📅 Creating events...")
    event_ids = []
    for i, event_data in enumerate(events_data):
        # Assign owners to events
        event_data['owner'] = user_ids[i % len(user_ids)]
        event_data['hosts'] = [user_ids[i % len(user_ids)]]
        
        event_id = create_event(events_table, event_data)
        if event_id:
            event_ids.append(event_id)
    
    print(f"\n🔗 Creating user-event relationships...")
    
    # Define relationships: (user_index, event_index, relationship_type)
    relationships = [
        (0, 0, 'host'),      # John hosts Tech Meetup
        (1, 0, 'attendee'),  # Jane attends Tech Meetup
        (2, 0, 'attendee'),  # Mike attends Tech Meetup
        (3, 0, 'attendee'),  # Sarah attends Tech Meetup
        
        (1, 1, 'host'),      # Jane hosts AI Workshop
        (0, 1, 'attendee'),  # John attends AI Workshop
        (2, 1, 'attendee'),  # Mike attends AI Workshop
        (4, 1, 'attendee'),  # David attends AI Workshop
        
        (2, 2, 'host'),      # Mike hosts Startup Networking
        (0, 2, 'attendee'),  # John attends Startup Networking
        (1, 2, 'attendee'),  # Jane attends Startup Networking
        (5, 2, 'attendee'),  # Emily attends Startup Networking
        
        (3, 3, 'host'),      # Sarah hosts Design Thinking
        (1, 3, 'attendee'),  # Jane attends Design Thinking
        (6, 3, 'attendee'),  # Alex attends Design Thinking
        (7, 3, 'attendee'),  # Lisa attends Design Thinking
    ]
    
    # Track event counts for each user
    user_event_counts = {user_id: {'hosted': 0, 'attended': 0} for user_id in user_ids}
    
    for user_idx, event_idx, relationship_type in relationships:
        if user_idx < len(user_ids) and event_idx < len(event_ids):
            user_id = user_ids[user_idx]
            event_id = event_ids[event_idx]
            
            success = create_user_event_relationship(user_event_table, user_id, event_id, relationship_type)
            if success:
                if relationship_type == 'host':
                    user_event_counts[user_id]['hosted'] += 1
                else:
                    user_event_counts[user_id]['attended'] += 1
    
    print(f"\n📊 Updating user event counts...")
    for user_id, counts in user_event_counts.items():
        update_user_event_counts(
            users_table, 
            user_id, 
            hosted_increment=counts['hosted'],
            attended_increment=counts['attended']
        )
    
    print(f"\n📧 Creating sample email status records...")
    # Create some email status records
    email_statuses = [
        (user_ids[0], users_data[0]['email'], 'sent'),
        (user_ids[1], users_data[1]['email'], 'sent'),
        (user_ids[2], users_data[2]['email'], 'failed'),
        (user_ids[3], users_data[3]['email'], 'sent'),
        (user_ids[4], users_data[4]['email'], 'sent'),
    ]
    
    for user_id, email, status in email_statuses:
        create_email_status(email_status_table, user_id, email, status)
    
    print("\n" + "=" * 50)
    print("✅ Data initialization completed successfully!")
    print(f"📊 Summary:")
    print(f"   - Users created: {len(user_ids)}")
    print(f"   - Events created: {len(event_ids)}")
    print(f"   - Relationships created: {len(relationships)}")
    print(f"   - Email status records: {len(email_statuses)}")
    print("\n🔗 Test the API with:")
    print(f"   - Get all users: GET http://localhost:8000/users/")
    print(f"   - Get filtered users: GET http://localhost:8000/users/list/?company=Google")
    print(f"   - Get all events: GET http://localhost:8000/events/")
    print(f"   - Get email status: GET http://localhost:8000/email-status/{user_ids[0]}")

if __name__ == "__main__":
    main() 