import asyncio
from typing import List, Dict, Optional
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException
from pydantic import EmailStr
from apscheduler.schedulers.background import BackgroundScheduler
from pymongo import MongoClient
from app.config import Settings
from app.models.schemas import EmailStatus
from app.database import Database
from datetime import timezone
import pytz
import logging
from pymongo.errors import ConfigurationError
from bson.objectid import ObjectId

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SESService:
    _scheduler = None
    
    def __init__(self, settings: Settings, db: Database):
        self.db = db
        self.session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.client = self.session.client('ses')
        self.sender_email = settings.SENDER_EMAIL
        
        # Extract connection info safely
        try:
            self.db_host = db.client.address[0]
            self.db_name = db.client.get_database().name
        except (ConfigurationError, AttributeError):
            self.db_host = settings.MONGODB_URL
            self.db_name = settings.MONGODB_DB_NAME
        
        logger.info(f"Initialized SESService with database: {self.db_name}")
        
        # Initialize scheduler only once
        if SESService._scheduler is None:
            SESService._scheduler = BackgroundScheduler(timezone=pytz.UTC)
            SESService._scheduler.start()
        self.scheduler = SESService._scheduler

    def _get_sync_database(self):
        """Helper method to create a new synchronous database connection"""
        client = MongoClient(self.db_host)
        return client[self.db_name]
    
    def get_utc_now(self) -> datetime:
        return datetime.now(timezone.utc)

    def ensure_timezone_aware(self, dt: datetime) -> datetime:
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    def _send_email_sync(self, email_record: Dict) -> Dict:
        """Synchronous method to send email via AWS SES"""
        try:
            message = {
                'Subject': {
                    'Data': email_record['subject'],
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Html': {
                        'Data': email_record['body_html'],
                        'Charset': 'UTF-8'
                    }
                }
            }

            if email_record.get('body_text'):
                message['Body']['Text'] = {
                    'Data': email_record['body_text'],
                    'Charset': 'UTF-8'
                }

            response = self.client.send_email(
                Source=self.sender_email,
                Destination={
                    'ToAddresses': email_record['recipient_emails'],
                },
                Message=message
            )
            
            return {
                'success': True,
                'message_id': response['MessageId']
            }
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _send_scheduled_email(self, email_id: str):
        """Synchronous method to handle scheduled email sending"""
        client = None
        try:
            # Create new synchronous database connection
            client = MongoClient(self.db_host)
            database = client[self.db_name]
            
            # Ensure email_id is ObjectId
            if isinstance(email_id, str):
                email_id = ObjectId(email_id)
            
            logger.info(f"Fetching email record for ID: {email_id}")
            
            # Get email record using synchronous operation
            email_record = database.emails.find_one({"_id": email_id})
            
            if not email_record:
                logger.error(f"Email record {email_id} not found")
                return
            
            logger.info(f"Sending scheduled email to {email_record.get('recipient_emails', [])}")
            
            # Send email
            result = self._send_email_sync(email_record)
            
            # Update status
            if result['success']:
                update_data = {
                    "status": EmailStatus.SENT,
                    "message_id": result['message_id'],
                    "sent_at": self.get_utc_now()
                }
                logger.info(f"Email {email_id} sent successfully")
            else:
                update_data = {
                    "status": EmailStatus.FAILED,
                    "error_message": result['error'],
                    "failed_at": self.get_utc_now()
                }
                logger.error(f"Failed to send email {email_id}: {result['error']}")
            
            # Update the database using synchronous operation
            database.emails.update_one(
                {"_id": email_id},
                {"$set": update_data}
            )
            
        except Exception as e:
            logger.error(f"Error in scheduled email job for {email_id}: {str(e)}")
            if client:
                try:
                    database = client[self.db_name]
                    database.emails.update_one(
                        {"_id": email_id},
                        {
                            "$set": {
                                "status": EmailStatus.FAILED,
                                "error_message": str(e),
                                "failed_at": self.get_utc_now()
                            }
                        }
                    )
                except Exception as update_error:
                    logger.error(f"Failed to update error status for {email_id}: {str(update_error)}")
        finally:
            if client:
                client.close()

    async def _schedule_email(
        self,
        to_addresses: List[EmailStr],
        subject: str,
        body_html: str,
        body_text: Optional[str],
        scheduled_time: datetime
    ) -> Dict:
        """Schedule email for later sending"""
        now = self.get_utc_now()
        scheduled_time = self.ensure_timezone_aware(scheduled_time)

        if scheduled_time <= now:
            raise ValueError("Scheduled time must be in the future")

        email_record = {
            "recipient_emails": to_addresses,
            "subject": subject,
            "body_html": body_html,
            "body_text": body_text,
            "scheduled_time": scheduled_time,
            "status": EmailStatus.SCHEDULED,
            "created_at": now
        }

        email_id = await self.db.emails.insert_one(email_record)
        str_email_id = str(email_id.inserted_id)

        logger.info(f"Scheduling email {str_email_id} for {scheduled_time}")
        
        self.scheduler.add_job(
            self._send_scheduled_email,
            trigger='date',
            run_date=scheduled_time,
            args=[str_email_id],
            id=str_email_id,
            misfire_grace_time=None
        )

        return {
            "message": "Email scheduled successfully",
            "email_id": str_email_id,
            "status": EmailStatus.SCHEDULED,
            "scheduled_time": scheduled_time
        }

    async def get_email_status(self, email_id: str) -> Dict:
        """Get the current status of an email"""
        email_record = await self.db.emails.find_one({"_id": email_id})
        if not email_record:
            raise HTTPException(status_code=404, detail="Email not found")
        return {
            "status": email_record["status"],
            "scheduled_time": email_record.get("scheduled_time"),
            "sent_at": email_record.get("sent_at"),
            "error_message": email_record.get("error_message")
        }
    
    async def send_email(
        self,
        to_addresses: List[EmailStr],
        subject: str,
        body_html: str,
        body_text: Optional[str] = None,
        scheduled_time: Optional[datetime] = None
    ) -> Dict:
        if scheduled_time:
            # Ensure scheduled_time is timezone-aware
            scheduled_time = self.ensure_timezone_aware(scheduled_time)
            return await self._schedule_email(
                to_addresses,
                subject,
                body_html,
                body_text,
                scheduled_time
            )

        # Create email record with UTC timestamp
        email_record = {
            "recipient_emails": to_addresses,
            "subject": subject,
            "body_html": body_html,
            "body_text": body_text,
            "status": EmailStatus.PENDING,
            "created_at": self.get_utc_now()
        }

        email_id = await self.db.emails.insert_one(email_record)

        try:
            message = {
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Html': {
                        'Data': body_html,
                        'Charset': 'UTF-8'
                    }
                }
            }

            if body_text:
                message['Body']['Text'] = {
                    'Data': body_text,
                    'Charset': 'UTF-8'
                }

            response = self.client.send_email(
                Source=self.sender_email,
                Destination={
                    'ToAddresses': to_addresses,
                },
                Message=message
            )

            # Update status to SENT
            await self.db.emails.update_one(
                {"_id": email_id.inserted_id},
                {
                    "$set": {
                        "status": EmailStatus.SENT,
                        "message_id": response['MessageId'],
                        "sent_at": self.get_utc_now()
                    }
                }
            )

            return {
                'message_id': response['MessageId'],
                'status': EmailStatus.SENT,
                'email_id': str(email_id.inserted_id),
                'recipients': to_addresses
            }

        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']

            await self.db.emails.update_one(
                {"_id": email_id.inserted_id},
                {
                    "$set": {
                        "status": EmailStatus.FAILED,
                        "error_code": error_code,
                        "error_message": error_message,
                        "failed_at": self.get_utc_now()
                    }
                }
            )

            raise HTTPException(
                status_code=500,
                detail=f"Failed to send email: {error_code} - {error_message}"
            )

    async def update_email_status(self, email_id: str, status: EmailStatus, error_details: Optional[Dict] = None) -> None:
        """Update email status and related details"""
        update_data = {
            "status": status,
            f"{status.lower()}_at": datetime.now()
        }

        if error_details:
            update_data.update(error_details)

        await self.db.emails.update_one(
            {"_id": email_id},
            {"$set": update_data}
        )

    async def verify_email_identity(self, email: EmailStr) -> Dict:
        """Verify an email address with Amazon SES"""
        try:
            response = self.client.verify_email_identity(
                EmailAddress=email
            )
            return {
                'status': 'verification_sent',
                'email': email
            }
        except ClientError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initiate verification: {str(e)}"
            )

    async def get_send_statistics(self) -> Dict:
        """Get sending statistics from Amazon SES"""
        try:
            response = self.client.get_send_statistics()
            return response['SendDataPoints']
        except ClientError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get statistics: {str(e)}"
            )

    async def generate_and_send(
        self,
        to_addresses: List[EmailStr],
        situation: str,
        keywords: List[str],
        template_data: Dict[str, str],
        scheduled_time: Optional[datetime] = None
    ) -> Dict:
        """
        Generate personalized email using CSV data and send via Amazon SES
        
        Args:
            to_addresses: List of recipient email addresses
            situation: Email context/purpose
            keywords: Key points to include
            template_data: Dictionary of template variables from CSV row
            scheduled_time: Optional scheduled send time
        """
        from app.services.llm_service import generate_email_content
        
        # Generate email content with template data
        email_content = await generate_email_content(
            situation=situation,
            keywords=keywords,
            data=template_data
        )
        
        # Replace template variables in generated content
        for key, value in template_data.items():
            placeholder = f"{{{key}}}"
            email_content['subject'] = email_content['subject'].replace(placeholder, str(value))
            email_content['html_body'] = email_content['html_body'].replace(placeholder, str(value))
            email_content['text_body'] = email_content['text_body'].replace(placeholder, str(value))
        
        # Send the personalized email
        return await self.send_email(
            to_addresses=to_addresses,
            subject=email_content['subject'],
            body_html=email_content['html_body'],
            body_text=email_content['text_body'],
            scheduled_time=scheduled_time
    )

    async def send_bulk_templated_emails(
        self,
        csv_data: List[Dict],
        recipient_column: str,
        scheduled_time: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Send templated emails to multiple recipients based on CSV data.
        """
        results = []
        for row in csv_data:
            try:
                recipient_email = row[recipient_column]
                if not isinstance(recipient_email, str) or '@' not in recipient_email:
                    raise ValueError(f"Invalid email address: {recipient_email}")

                result = await self.send_email(
                    to_addresses=[recipient_email],
                    subject=row['email_subject'],
                    body_html=row['email_content'],
                    scheduled_time=scheduled_time
                )

                results.append({
                    'status': 'success',
                    'email': recipient_email,
                    'template_data': row['template_data'],
                    **result
                })
            except Exception as e:
                results.append({
                    'status': 'error',
                    'email': row.get(recipient_column, 'unknown'),
                    'template_data': row.get('template_data', {}),
                    'error': str(e)
                })

        return results
    
#     {
#     "recipient_column": "Email",
#     "template": "Dear {Name},\n\nWelcome to {Company}! We're excited to have you join us in {Location}.\n\nBest regards,\nThe Team",
#     "subject_template": "Welcome to {Company}, {Name}!",
#     "placeholder_columns": ["Name", "Company", "Location"],
#     "scheduled_time": null
# }