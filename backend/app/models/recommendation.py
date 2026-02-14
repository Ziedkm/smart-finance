"""
Pydantic models for recommendations
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class RecommendationType(str, Enum):
    BUDGET_WARNING = "budget_warning"
    SPENDING_INSIGHT = "spending_insight"
    SAVINGS_TIP = "savings_tip"
    GOAL_SUGGESTION = "goal_suggestion"
    ANOMALY_ALERT = "anomaly_alert"


class RecommendationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class RecommendationResponse(BaseModel):
    """Recommendation item"""
    id: str
    user_id: str
    type: str
    priority: str
    title: str
    message: str
    action_url: Optional[str]
    created_at: datetime
    is_read: bool
    dismissed_at: Optional[datetime]


class RecommendationListResponse(BaseModel):
    """List of recommendations"""
    recommendations: List[RecommendationResponse]
    total: int
    unread_count: int
