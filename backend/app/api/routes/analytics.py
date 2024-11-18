from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from typing import Dict, List
from ...database import Database
from ...services.ses_service import SESService
from ...api.routes.email import get_ses_service

router = APIRouter()

@router.get("/analytics")
async def get_email_analytics(
    ses_service: SESService = Depends(get_ses_service)
):
    """Combine MongoDB tracking data with SES statistics for comprehensive analytics"""
    db = await Database.get_db()
    
    # Get SES statistics
    ses_stats = await ses_service.get_send_statistics()
    
    # Get MongoDB statistics
    mongo_pipeline = [
        {
            "$group": {
                "_id": None,
                "total_emails": {"$sum": 1},
                "sent": {
                    "$sum": {"$cond": [{"$eq": ["$status", "SENT"]}, 1, 0]}
                },
                "pending": {
                    "$sum": {"$cond": [{"$eq": ["$status", "PENDING"]}, 1, 0]}
                },
                "scheduled": {
                    "$sum": {"$cond": [{"$eq": ["$status", "SCHEDULED"]}, 1, 0]}
                },
                "failed": {
                    "$sum": {"$cond": [{"$eq": ["$status", "FAILED"]}, 1, 0]}
                }
            }
        }
    ]
    
    db_stats = await db.emails.aggregate(mongo_pipeline).to_list(None)
    db_stats = db_stats[0] if db_stats else {
        "total_emails": 0, "sent": 0, "pending": 0, "scheduled": 0, "failed": 0
    }

    # Process SES data points
    ses_summary = {
        "total_delivery_attempts": 0,
        "total_bounces": 0,
        "total_complaints": 0,
        "total_rejects": 0,
        "delivery_attempts_24h": 0,
        "bounces_24h": 0,
        "complaints_24h": 0,
        "rejects_24h": 0,
        "time_series_data": [],
        "success_rate": 0,
        "bounce_rate": 0
    }
    
    for point in ses_stats:
        timestamp = point["Timestamp"]
        data_point = {
            "timestamp": timestamp,
            "delivery_attempts": point["DeliveryAttempts"],
            "bounces": point["Bounces"],
            "complaints": point["Complaints"],
            "rejects": point["Rejects"]
        }
        ses_summary["time_series_data"].append(data_point)
        
        # Update totals
        ses_summary["total_delivery_attempts"] += point["DeliveryAttempts"]
        ses_summary["total_bounces"] += point["Bounces"]
        ses_summary["total_complaints"] += point["Complaints"]
        ses_summary["total_rejects"] += point["Rejects"]
    
    # Calculate rates
    if ses_summary["total_delivery_attempts"] > 0:
        successful_deliveries = (ses_summary["total_delivery_attempts"] - 
                               ses_summary["total_bounces"] - 
                               ses_summary["total_rejects"])
        ses_summary["success_rate"] = (successful_deliveries / 
                                     ses_summary["total_delivery_attempts"]) * 100
        ses_summary["bounce_rate"] = (ses_summary["total_bounces"] / 
                                    ses_summary["total_delivery_attempts"]) * 100

    # Combine both data sources
    return {
        "database_metrics": {
            "total_emails": db_stats["total_emails"],
            "status_breakdown": {
                "sent": db_stats["sent"],
                "pending": db_stats["pending"],
                "scheduled": db_stats["scheduled"],
                "failed": db_stats["failed"]
            }
        },
        "ses_metrics": {
            "overall_stats": {
                "total_delivery_attempts": ses_summary["total_delivery_attempts"],
                "total_bounces": ses_summary["total_bounces"],
                "total_complaints": ses_summary["total_complaints"],
                "total_rejects": ses_summary["total_rejects"],
                "success_rate": round(ses_summary["success_rate"], 2),
                "bounce_rate": round(ses_summary["bounce_rate"], 2)
            }
        }
    }
