# project API

A FastAPI-based REST API for managing users, events, and email campaigns with DynamoDB backend.

## 🚀 Features

- **User Management**: Create, read, update, and delete users with detailed profiles
- **Event Management**: Create and manage events with host/attendee relationships
- **Email Campaigns**: Send bulk emails to filtered user groups
- **Email Status Tracking**: Track email delivery status for each user
- **Advanced Filtering**: Filter users by company, job title, location, and event participation
- **DynamoDB Integration**: Scalable NoSQL database with optimized indexes
- **AWS SAM Deployment**: Infrastructure as Code for easy deployment

## 🏗️ Architecture

- **Backend**: FastAPI (Python 3.9)
- **Database**: Amazon DynamoDB
- **Infrastructure**: AWS SAM (Serverless Application Model)
- **Email Service**: SMTP integration with status tracking

## 📋 Prerequisites

- Python 3.9+
- AWS CLI configured
- AWS SAM CLI
- SMTP credentials for email functionality

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd project
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the root directory:

```env
# AWS Configuration
AWS_REGION=us-east-1
ENVIRONMENT=dev
AWS_DEFAULT_REGION=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

# SMTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=youremail
DEFAULT_FROM_NAME=SuperMomo
```

### 4. Deploy Infrastructure
#### Option 1: Using the Deployment Script (Recommended)

```bash
# Deploy to dev environment (default)
./deploy-db.sh

# Deploy to specific environment
./deploy-db.sh prod

# Deploy to staging
./deploy-db.sh staging
```

#### Option 2: Manual Deployment
```bash
# Deploy DynamoDB tables
sam build
sam deploy --guided
```

### 5. Run the Application

```bash
# Development
uvicorn main:app --reload

# Production
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Interactive API Docs
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔧 API Endpoints

### Users


#### Filter Users
```bash
curl -X GET "http://localhost:8000/users/list/?company=Tech%20Corp&city=San%20Francisco&min_hosted=1&page=1&pagesize=10"
```

**Endpoint**: `GET /users/list/`

**Query Parameters**:
- `company` (optional): Filter by company name
- `jobTitle` (optional): Filter by job title
- `city` (optional): Filter by city
- `state` (optional): Filter by state
- `min_hosted` (optional): Minimum number of events hosted
- `max_hosted` (optional): Maximum number of events hosted
- `min_attended` (optional): Minimum number of events attended
- `max_attended` (optional): Maximum number of events attended
- `sort_by` (optional): Field to sort by (default: "createdAt")
- `sort_order` (optional): Sort order - "asc" or "desc" (default: "desc")
- `page` (optional): Page number, 1-based (default: 1)
- `pagesize` (optional): Items per page, 1-100 (default: 20)

**Response Format**:
```json
{
  "items": [
    {
      "id": "user_id",
      "firstName": "John",
      "lastName": "Doe",
      "email": "john.doe@example.com",
      "phoneNumber": "+1234567890",
      "jobTitle": "Software Engineer",
      "company": "Tech Corp",
      "city": "San Francisco",
      "state": "CA",
      "number_of_events_hosted": 2,
      "number_of_events_attended": 5
    }
  ],
  "total_count": 50,
  "page": 1,
  "pagesize": 20,
  "total_pages": 3,
  "has_next": true,
  "has_previous": false
}
```

**Filtering Examples**:

```bash
# Filter by company
curl -X GET "http://localhost:8000/users/list/?company=Google"

# Filter by job title
curl -X GET "http://localhost:8000/users/list/?jobTitle=Software%20Engineer"

# Filter by location
curl -X GET "http://localhost:8000/users/list/?city=San%20Francisco&state=CA"

# Filter by event participation
curl -X GET "http://localhost:8000/users/list/?min_hosted=1&min_attended=3"

# Combined filters
curl -X GET "http://localhost:8000/users/list/?company=Tech%20Corp&jobTitle=Engineer&city=San%20Francisco&min_hosted=1&max_attended=10"

# With pagination and sorting
curl -X GET "http://localhost:8000/users/list/?company=Tech%20Corp&sort_by=number_of_events_hosted&sort_order=desc&page=2&pagesize=10"
```


#### Create User
```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "John",
    "lastName": "Doe",
    "phoneNumber": "+1234567890",
    "email": "john.doe@example.com",
    "jobTitle": "Software Engineer",
    "company": "Tech Corp",
    "city": "San Francisco",
    "state": "CA"
  }'
```

#### Get User by ID
```bash
curl -X GET "http://localhost:8000/users/{user_id}"
```

#### Get All Users
```bash
curl -X GET "http://localhost:8000/users/"
```

#### Update User
```bash
curl -X PUT "http://localhost:8000/users/{user_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "Jane",
    "lastName": "Smith",
    "jobTitle": "Senior Engineer"
  }'
```

#### Delete User
```bash
curl -X DELETE "http://localhost:8000/users/{user_id}"
```


#### Join Event
```bash
# Join as host
curl -X PATCH "http://localhost:8000/users/{user_id}/join/{event_id}?relationship_type=host"

# Join as attendee
curl -X PATCH "http://localhost:8000/users/{user_id}/join/{event_id}?relationship_type=attendee"
```

### Events

#### Create Event
```bash
curl -X POST "http://localhost:8000/events/" \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "tech-meetup-2024",
    "title": "Tech Meetup 2024",
    "description": "Join us for an exciting tech meetup",
    "startAt": "2024-03-15T18:00:00Z",
    "endAt": "2024-03-15T21:00:00Z",
    "venue": "Tech Hub",
    "maxCapacity": 100,
    "owner": "user_id_here",
    "hosts": ["user_id_1", "user_id_2"]
  }'
```

#### Get Event by ID
```bash
curl -X GET "http://localhost:8000/events/{event_id}"
```

#### Get All Events
```bash
curl -X GET "http://localhost:8000/events/"
```

#### Update Event
```bash
curl -X PUT "http://localhost:8000/events/{event_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Tech Meetup 2024",
    "description": "Updated description"
  }'
```

#### Delete Event
```bash
curl -X DELETE "http://localhost:8000/events/{event_id}"
```

### Email Campaigns

#### Send Email to Filtered Users
```bash
curl -X POST "http://localhost:8000/users/send-email/" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Welcome to SuperMomos!",
    "body": "<h1>Welcome!</h1><p>Thank you for joining our platform.</p>"
  }' \
  -G \
  -d "company=Tech Corp" \
  -d "city=San Francisco" \
  -d "min_hosted=1"
```

**Endpoint**: `POST /users/send-email/`

**Request Body** (JSON):
```json
{
  "subject": "Email Subject",
  "body": "<h1>HTML Content</h1><p>Email body content</p>"
}
```

**Query Parameters**:
- `company` (optional): Filter by company name
- `jobTitle` (optional): Filter by job title
- `city` (optional): Filter by city
- `state` (optional): Filter by state
- `min_hosted` (optional): Minimum number of events hosted
- `max_hosted` (optional): Maximum number of events hosted
- `min_attended` (optional): Minimum number of events attended
- `max_attended` (optional): Maximum number of events attended

**Response Format**:
```json
{
  "message": "Email campaign completed. 25 emails sent successfully.",
  "recipients": [
    {
      "userId": "userId",
      "email": "john.doe@example.com",
    }
  ],
  "recipients_count": 25
}
```

### Email Status

#### Get Email Status by User ID
```bash
curl -X GET "http://localhost:8000/email-status/{user_id}"
```

#### Get Email Status by Email Address
```bash
curl -X GET "http://localhost:8000/email-status/email/john.doe@example.com"
```

#### Get All Email Status Records
```bash
curl -X GET "http://localhost:8000/email-status/"
```

## 🗄️ Database Schema

### Users Table
- **Primary Key**: `id` (String)
- **GSI**: EmailIndex, CompanyIndex, JobTitleIndex, CityIndex, StateIndex
- **Attributes**: firstName, lastName, email, phoneNumber, jobTitle, company, city, state, etc.

### Events Table
- **Primary Key**: `id` (String)
- **GSI**: SlugIndex, OwnerIndex
- **Attributes**: slug, title, description, startAt, endAt, venue, maxCapacity, owner, hosts

### UserEventRelationship Table
- **Primary Key**: `id` (String)
- **GSI**: UserIdIndex, EventIdIndex, RelationshipTypeIndex
- **Attributes**: userId, eventId, relationshipType, createdAt

### EmailStatus Table
- **Primary Key**: `userId` (String)
- **GSI**: EmailIndex
- **Attributes**: email, status, createdAt

## 🚀 Deployment

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run with hot reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### AWS Deployment
```bash
# Build and deploy
sam build
sam deploy --guided

# Deploy to specific environment
sam deploy --parameter-overrides EnvironmentType=prod
```

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the deployment guide in `DEPLOYMENT.md` 