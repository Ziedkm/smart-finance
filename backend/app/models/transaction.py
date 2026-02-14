"""
Pydantic models for transactions
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


class TransactionCreate(BaseModel):
    """Create transaction request"""
    account_id: str = Field(..., description="Account UUID")
    amount: float = Field(..., gt=0, description="Transaction amount (positive)")
    transaction_type: TransactionType
    transaction_date: date = Field(default_factory=date.today)
    description: Optional[str] = Field(None, max_length=500)
    merchant: Optional[str] = Field(None, max_length=200)
    category_id: Optional[str] = Field(None, description="Category UUID (optional, AI will suggest)")
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    is_recurring: bool = False
    recurring_frequency: Optional[str] = Field(None, pattern="^(weekly|monthly|yearly)$")
    
    class Config:
        json_schema_extra = {
            "example": {
                "account_id": "uuid-here",
                "amount": 45.50,
                "transaction_type": "expense",
                "transaction_date": "2026-02-14",
                "description": "Grocery shopping",
                "merchant": "Carrefour",
                "category_id": None,  # AI will suggest
                "notes": "Weekly groceries",
                "tags": ["food", "weekly"],
                "is_recurring": False
            }
        }


class TransactionUpdate(BaseModel):
    """Update transaction request"""
    amount: Optional[float] = Field(None, gt=0)
    transaction_type: Optional[TransactionType] = None
    transaction_date: Optional[date] = None
    description: Optional[str] = Field(None, max_length=500)
    merchant: Optional[str] = Field(None, max_length=200)
    category_id: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    is_category_verified: Optional[bool] = None


class CategorySuggestion(BaseModel):
    """AI category suggestion"""
    category_id: str
    category_name: str
    confidence: float = Field(..., ge=0, le=1)
    explanation: str
    method: str  # 'rule', 'ml', 'default'
    top_3_predictions: List[dict]


class TransactionResponse(BaseModel):
    """Transaction response with AI suggestion"""
    id: str
    user_id: str
    account_id: str
    amount: float
    transaction_type: str
    transaction_date: date
    description: Optional[str]
    merchant: Optional[str]
    category_id: Optional[str]
    category_name: Optional[str]
    category_confidence: Optional[float]
    is_category_verified: bool
    notes: Optional[str]
    tags: Optional[List[str]]
    is_recurring: bool
    recurring_frequency: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    # AI suggestion (if category not verified)
    ai_suggestion: Optional[CategorySuggestion] = None


class TransactionListResponse(BaseModel):
    """Paginated transaction list"""
    transactions: List[TransactionResponse]
    total: int
    page: int
    page_size: int
    has_more: bool
