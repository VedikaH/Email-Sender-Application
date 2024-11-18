from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class EmailStatus(str, Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"
    SCHEDULED = "SCHEDULED"

class DeliveryStatus(str, Enum):
    PENDING = "pending"
    DELIVERED = "delivered"
    BOUNCED = "bounced"
    OPENED = "opened"

class EmailContent(BaseModel):
    subject: str
    html_body: str
    text_body: str

class EmailData(BaseModel):
    recipient_email: EmailStr
    subject: str
    body_html: str
    body_text: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    status: EmailStatus = EmailStatus.PENDING
    delivery_status: DeliveryStatus = DeliveryStatus.PENDING
    metadata: Dict = {}
    created_at: Optional[datetime] = None

class EmailScheduleRequest(BaseModel):
    prompt: str
    schedule_time: Optional[datetime] = None
    batch_size: int = 50
    batch_interval_minutes: int = 60

class EmailGenerationRequest(BaseModel):
    to_addresses: List[EmailStr]
    situation: str
    keywords: List[str]
    email_type: str
    template_data: Dict
    scheduled_time: Optional[datetime] = None