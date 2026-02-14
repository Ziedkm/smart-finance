"""
Pydantic models for budgets
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from enum import Enum


class BudgetPeriod(str, Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class BudgetCreate(BaseModel):
    """Create budget request"""
    category_id: str = Field(..., description="Category UUID")
    amount: float = Field(..., gt=0, description="Budget amount")
    period: BudgetPeriod = BudgetPeriod.MONTHLY
    start_date: date = Field(default_factory=date.today)
    end_date: Optional[date] = None
    alert_threshold: float = Field(0.80, ge=0, le=1, description="Alert at X% utilization")
    
    class Config:
        json_schema_extra = {
            "example": {
                "category_id": "uuid-here",
                "amount": 500.00,
                "period": "monthly",
                "start_date": "2026-02-01",
                "end_date": None,
                "alert_threshold": 0.80
            }
        }


class BudgetUpdate(BaseModel):
    """Update budget request"""
    amount: Optional[float] = Field(None, gt=0)
    period: Optional[BudgetPeriod] = None
    end_date: Optional[date] = None
    alert_threshold: Optional[float] = Field(None, ge=0, le=1)
    is_active: Optional[bool] = None


class BudgetStatus(str, Enum):
    ON_TRACK = "on_track"
    WARNING = "warning"
    EXCEEDED = "exceeded"


class BudgetResponse(BaseModel):
    """Budget with variance calculation"""
    id: str
    user_id: str
    category_id: str
    category_name: str
    amount: float
    period: str
    start_date: date
    end_date: Optional[date]
    alert_threshold: float
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # Variance calculation (current period)
    actual_amount: float
    remaining_amount: float
    utilization_percent: float
    status: BudgetStatus
    days_remaining: int
