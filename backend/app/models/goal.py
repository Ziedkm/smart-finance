"""
Pydantic models for financial goals
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from enum import Enum


class GoalStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class GoalCreate(BaseModel):
    """Create goal request"""
    name: str = Field(..., max_length=200)
    target_amount: float = Field(..., gt=0)
    current_amount: float = Field(0, ge=0)
    target_date: date
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Emergency Fund",
                "target_amount": 10000.00,
                "current_amount": 2500.00,
                "target_date": "2026-12-31",
                "category": "Savings",
                "description": "Build 6-month emergency fund"
            }
        }


class GoalUpdate(BaseModel):
    """Update goal request"""
    name: Optional[str] = Field(None, max_length=200)
    target_amount: Optional[float] = Field(None, gt=0)
    current_amount: Optional[float] = Field(None, ge=0)
    target_date: Optional[date] = None
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    status: Optional[GoalStatus] = None


class GoalResponse(BaseModel):
    """Goal with progress calculation"""
    id: str
    user_id: str
    name: str
    target_amount: float
    current_amount: float
    target_date: date
    category: Optional[str]
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    
    # Progress calculation
    progress_percent: float
    remaining_amount: float
    days_remaining: int
    required_monthly_contribution: float
    on_track: bool
