"""
Pydantic models for dashboard
"""

from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import date


class CategorySpending(BaseModel):
    """Spending by category"""
    category_name: str
    amount: float
    percentage: float
    transaction_count: int


class MonthlyTrend(BaseModel):
    """Monthly spending trend"""
    month: str  # YYYY-MM
    income: float
    expenses: float
    net: float


class DashboardKPIs(BaseModel):
    """Key performance indicators"""
    # Current month
    total_income: float
    total_expenses: float
    net_savings: float
    savings_rate: float  # percentage
    
    # Budget health
    budgets_on_track: int
    budgets_warning: int
    budgets_exceeded: int
    
    # Goals
    active_goals_count: int
    goals_on_track: int
    
    # Anomalies
    pending_anomalies: int
    
    # Trends
    expense_trend: str  # 'up', 'down', 'stable'
    expense_change_percent: float


class DashboardResponse(BaseModel):
    """Complete dashboard data"""
    kpis: DashboardKPIs
    category_breakdown: List[CategorySpending]
    monthly_trends: List[MonthlyTrend]
    top_expenses: List[Dict[str, Any]]
    recent_transactions: List[Dict[str, Any]]
