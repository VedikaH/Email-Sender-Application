from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from typing import List, Optional, Dict
from pydantic import BaseModel
from datetime import datetime
from io import StringIO
import pandas as pd
import csv

from app.api.routes.email import get_ses_service

from ...services.csv_service import CSVService, TemplateData
from ...services.ses_service import SESService
from ...database import Database
from ...config import Settings

router = APIRouter()

class BulkEmailRequest(BaseModel):
    template: str
    subject_template: str
    placeholder_columns: str 
    recipient_column: str
    scheduled_time: Optional[datetime] = None

@router.post("/send-bulk-emails")
async def send_bulk_emails(
    file: UploadFile = File(...),
    bulk_request: BulkEmailRequest = Depends(),
    ses_service: SESService = Depends(get_ses_service)
):
    try:
        contents = await file.read()
        file_contents = contents.decode('utf-8')
        print(file_contents)

        # Use csv.DictReader to read the CSV file
        reader = csv.DictReader(StringIO(file_contents))
        csv_data = list(reader)
        print(csv_data)

        # Validate required columns
        required_columns = set(bulk_request.placeholder_columns) | {bulk_request.recipient_column}
        missing_columns = required_columns - set(csv_data[0].keys())

        print(required_columns)
        print(missing_columns)

        avail = ', '.join(csv_data[0].keys())
        print(avail) 
        # Process the CSV data using the CSVService
        template_data = TemplateData(
            template=bulk_request.template,
            subject_template=bulk_request.subject_template,
            placeholder_columns=bulk_request.placeholder_columns
        )
        csv_data = await CSVService.process_csv(file_contents, template_data)

        # Send bulk emails
        results = await ses_service.send_bulk_templated_emails(
            csv_data=csv_data,
            recipient_column=bulk_request.recipient_column,
            scheduled_time=bulk_request.scheduled_time
        )

        return {
            "status": "completed",
            "total_processed": len(results),
            "results": results
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error processing file: {str(e)}"
        )
    
    # template: str = "Dear {Name}, welcome to {Company}. We're excited to have you join us."
    # subject_template: str = "Welcome to {Company}, {Name}!"
    # placeholder_columns: List[str] = ["Name", "Company"] 
    # recipient_column: str = "Email"
    # scheduled_time: Optional[datetime] = None