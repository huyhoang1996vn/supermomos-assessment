# email_service.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()
from fastapi import HTTPException

from settings import get_dynamodb_resource, ENVIRONMENT
from database.dynamodb import DynamoDB

dynamodb = get_dynamodb_resource()
table = dynamodb.Table(f"EmailStatus-{ENVIRONMENT}")
email_status_db = DynamoDB(table)

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.default_from_email = os.getenv("DEFAULT_FROM_EMAIL", "noreply@gmail.com")
        self.default_from_name = os.getenv("DEFAULT_FROM_NAME", "SuperMomos")
        
        if not self.smtp_username or not self.smtp_password:
            raise ValueError("SMTP_USERNAME and SMTP_PASSWORD environment variables are required")
    
    def send_emails(
        self,
        recipients: List[Dict],
        subject: str,
        body: str,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ) -> Dict:
        """
        Send emails to multiple recipients
        
        Args:
            recipients: List of user dictionaries with email addresses
            subject: Email subject
            body: Email body content
            from_email: Optional from email address
            from_name: Optional from name
            
        Returns:
            Dict with email sending results
        """
        if not recipients:
            return {
                "message": "No recipients provided",
                "recipients_count": 0,
            }
        
        # Use default values if not provided
        from_email = from_email or self.default_from_email
        from_name = from_name or self.default_from_name
        
        try:
            # Create SMTP connection
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            
            for recipient in recipients:
                try:
                    # Create message
                    msg = MIMEMultipart()
                    msg['From'] = f"{from_name} <{from_email}>"
                    msg['To'] = recipient['email']
                    msg['Subject'] = subject
                    
                    # Add body
                    msg.attach(MIMEText(body, 'html'))
                    
                    # Send email
                    result = server.send_message(msg)
                    email_status_db.create_object(
                        {
                            'email': recipient['email'],
                            'userId': recipient['userId'],
                            'status': 'sent',
                            'createdAt': datetime.now().isoformat()
                        }
                    )
                    
                except Exception as e:
                    email_status_db.create_object(
                        {
                            'email': recipient['email'],
                            'userId': recipient['userId'],
                            'status': 'failed',
                            'createdAt': datetime.now().isoformat()
                        }
                    )
                    print(f"Failed to send email to {recipient['email']}: {str(e)}")
            
            server.quit()
            
            return {
                "message": f"Email campaign completed. {len(recipients)} emails sent successfully.",
                "recipients_count": len(recipients),
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send emails: {str(e)}"
            )
    