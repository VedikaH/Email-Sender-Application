from io import StringIO
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File
from typing import List, Optional
import pandas as pd
from pydantic import BaseModel, EmailStr
from datetime import datetime

from app.services.ses_service import SESService
from app.services.csv_service import CSVService, TemplateData
from app.config import Settings
from app.database import Database


router = APIRouter()

class EmailRequest(BaseModel):
    to_addresses: List[EmailStr]
    subject: str
    body_html: str
    body_text: Optional[str] = None
    scheduled_time: Optional[datetime] = None

class EmailGenerationRequest(BaseModel):
    to_addresses: List[EmailStr]
    situation: str
    keywords: List[str]
    email_type: str
    template_data: dict
    scheduled_time: Optional[datetime] = None

class VerifyEmailRequest(BaseModel):
    email: EmailStr

class BulkEmailRequest(BaseModel):
    recipient_column: str
    template: str
    subject_template: str
    placeholder_columns: List[str]
    scheduled_time: Optional[datetime] = None

def get_ses_service(settings: Settings = Depends(), db: Database = Depends(Database.get_db)):
    return SESService(settings, db)

@router.post("/send")
async def send_email(
    email_request: EmailRequest,
    ses_service: SESService = Depends(get_ses_service)
):
    return await ses_service.send_email(
        to_addresses=email_request.to_addresses,
        subject=email_request.subject,
        body_html=email_request.body_html,
        body_text=email_request.body_text,
        scheduled_time=email_request.scheduled_time
    )

@router.post("/generate-and-send")
async def generate_and_send_email(
    email_request: EmailGenerationRequest,
    ses_service: SESService = Depends(get_ses_service)
):
    return await ses_service.generate_and_send(
        to_addresses=email_request.to_addresses,
        situation=email_request.situation,
        keywords=email_request.keywords,
        template_data=email_request.template_data,
        scheduled_time=email_request.scheduled_time
    )

@router.post("/verify-email")
async def verify_email(
    verify_request: VerifyEmailRequest,
    ses_service: SESService = Depends(get_ses_service)
):
    return await ses_service.verify_email_identity(verify_request.email)


@router.post("/generate-and-send-bulk")
async def generate_and_send_bulk_emails(
    file: UploadFile = File(...),
    situation: str = Form(...),
    keywords: List[str] = Form(...),
    recipient_column: str = Form(...),
    scheduled_time: Optional[datetime] = Form(None),
    ses_service: SESService = Depends(get_ses_service)
):
    # Read CSV file
    contents = await file.read()
    df = pd.read_csv(StringIO(contents.decode()))
    
    results = []
    for _, row in df.iterrows():
        try:
            # Get recipient email from the specified column
            recipient_email = row[recipient_column]
            
            # Create template data from row
            template_data = row.to_dict()
            
            # Generate and send personalized email
            result = await ses_service.generate_and_send(
                to_addresses=[recipient_email],
                situation=situation,
                keywords=keywords,
                template_data=template_data,
                scheduled_time=scheduled_time
            )
            
            results.append({
                'status': 'success',
                'email': recipient_email,
                'result': result
            })
            
        except Exception as e:
            results.append({
                'status': 'error',
                'email': row.get(recipient_column, 'unknown'),
                'error': str(e)
            })
    
    return {
        'status': 'completed',
        'total_processed': len(results),
        'results': results
    }


