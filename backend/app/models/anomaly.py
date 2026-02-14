"""
Pydantic models for anomaly detection
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AnomalyStatus(str, Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    DISMISSED = "dismissed"
    CONFIRMED = "confirmed"


class AnomalyResponse(BaseModel):
    """Anomaly detection result"""
    id: str
    user_id: str
    transaction_id: str
    detected_at: datetime
    anomaly_score: float = Field(..., ge=-1, le=1)
    explanation: str
    status: str
    reviewed_at: Optional[datetime]
    
    # Transaction details
    transaction: dict


class AnomalyReview(BaseModel):
    """Review anomaly request"""
    status: AnomalyStatus = Field(..., description="New status after review")
    notes: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "confirmed",
                "notes": "This was indeed an unusual expense"
            }
        }


class AnomalyListResponse(BaseModel):
    """List of anomalies"""
    anomalies: List[AnomalyResponse]
    total: int
    pending_count: int
