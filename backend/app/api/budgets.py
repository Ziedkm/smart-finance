"""
Budget API endpoints
CRUD + variance calculation + alerts
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import date, datetime, timedelta
from app.models.budget import (
    BudgetCreate, BudgetUpdate, BudgetResponse, BudgetStatus
)
from app.dependencies import get_current_user_id
from app.database import get_db_service, DatabaseService

router = APIRouter(prefix="/budgets", tags=["Budgets"])


def calculate_budget_variance(
    budget: dict,
    transactions: List[dict]
) -> dict:
    """
    Calculate budget variance for current period
    
    Args:
        budget: Budget dict
        transactions: List of transactions in category
        
    Returns:
        Budget with variance calculations
    """
    # Determine current period dates
    today = date.today()
    period = budget['period']
    
    if period == 'weekly':
        # Current week
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
    elif period == 'monthly':
        # Current month
        start = today.replace(day=1)
        next_month = today.replace(day=28) + timedelta(days=4)
        end = next_month - timedelta(days=next_month.day)
    elif period == 'yearly':
        # Current year
        start = today.replace(month=1, day=1)
        end = today.replace(month=12, day=31)
    else:
        start = today
        end = today
    
    # Filter transactions to current period
    period_transactions = [
        t for t in transactions
        if start <= datetime.fromisoformat(t['transaction_date']).date() <= end
        and t['transaction_type'] == 'expense'
    ]
    
    # Calculate actual amount spent
    actual_amount = sum(t['amount'] for t in period_transactions)
    
    # Calculate metrics
    budget_amount = budget['amount']
    remaining_amount = budget_amount - actual_amount
    utilization_percent = (actual_amount / budget_amount * 100) if budget_amount > 0 else 0
    
    # Determine status
    alert_threshold = budget.get('alert_threshold', 0.80)
    if utilization_percent >= 100:
        status = BudgetStatus.EXCEEDED
    elif utilization_percent >= (alert_threshold * 100):
        status = BudgetStatus.WARNING
    else:
        status = BudgetStatus.ON_TRACK
    
    # Days remaining in period
    days_remaining = (end - today).days
    
    return {
        **budget,
        'actual_amount': actual_amount,
        'remaining_amount': remaining_amount,
        'utilization_percent': utilization_percent,
        'status': status.value,
        'days_remaining': days_remaining
    }


@router.post("/", response_model=BudgetResponse, status_code=201)
async def create_budget(
    budget: BudgetCreate,
    user_id: str = Depends(get_current_user_id),
    db: DatabaseService = Depends(get_db_service)
):
    """
    Create new budget
    
    - Sets budget limit for a category
    - Defines period (weekly/monthly/yearly)
    - Configures alert threshold
    """
    # Verify category exists and belongs to user
    cat_result = await db.execute_query(
        table="categories",
        filters={"id": budget.category_id, "user_id": user_id}
    )
    
    if not cat_result['success'] or not cat_result['data']:
        raise HTTPException(status_code=404, detail="Category not found")
    
    category = cat_result['data'][0]
    
    # Create budget
    budget_data = {
        "user_id": user_id,
        "category_id": budget.category_id,
        "amount": budget.amount,
        "period": budget.period.value,
        "start_date": budget.start_date.isoformat(),
        "end_date": budget.end_date.isoformat() if budget.end_date else None,
        "alert_threshold": budget.alert_threshold,
        "is_active": True
    }
    
    result = await db.execute_query(
        table="budgets",
        operation="insert",
        data=budget_data
    )
    
    if not result['success']:
        raise HTTPException(status_code=500, detail="Failed to create budget")
    
    created_budget = result['data'][0]
    
    # Get transactions for variance calculation
    txn_result = await db.execute_query(
        table="transactions",
        filters={"user_id": user_id, "category_id": budget.category_id}
    )
    
    transactions = txn_result['data'] if txn_result['success'] else []
    
    # Calculate variance
    budget_with_variance = calculate_budget_variance(created_budget, transactions)
    budget_with_variance['category_name'] = category['name']
    
    return BudgetResponse(**budget_with_variance)


@router.get("/", response_model=List[BudgetResponse])
async def list_budgets(
    user_id: str = Depends(get_current_user_id),
    db: DatabaseService = Depends(get_db_service),
    active_only: bool = True
):
    """
    List all budgets with variance calculations
    
    Query params:
    - active_only: Only show active budgets (default: true)
    """
    filters = {"user_id": user_id}
    if active_only:
        filters["is_active"] = True
    
    result = await db.execute_query(
        table="budgets",
        filters=filters
    )
    
    if not result['success']:
        raise HTTPException(status_code=500, detail="Failed to fetch budgets")
    
    budgets = result['data']
    
    # Get categories
    cat_result = await db.execute_query(
        table="categories",
        filters={"user_id": user_id}
    )
    category_map = {c['id']: c['name'] for c in cat_result['data']} if cat_result['success'] else {}
    
    # Get all transactions for variance calculation
    txn_result = await db.execute_query(
        table="transactions",
        filters={"user_id": user_id}
    )
    all_transactions = txn_result['data'] if txn_result['success'] else []
    
    # Calculate variance for each budget
    response_budgets = []
    for budget in budgets:
        category_transactions = [
            t for t in all_transactions
            if t['category_id'] == budget['category_id']
        ]
        
        budget_with_variance = calculate_budget_variance(budget, category_transactions)
        budget_with_variance['category_name'] = category_map.get(budget['category_id'], 'Unknown')
        
        response_budgets.append(BudgetResponse(**budget_with_variance))
    
    return response_budgets


@router.get("/{budget_id}", response_model=BudgetResponse)
async def get_budget(
    budget_id: str,
    user_id: str = Depends(get_current_user_id),
    db: DatabaseService = Depends(get_db_service)
):
    """Get budget by ID with variance"""
    result = await db.execute_query(
        table="budgets",
        filters={"id": budget_id, "user_id": user_id}
    )
    
    if not result['success'] or not result['data']:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    budget = result['data'][0]
    
    # Get category
    cat_result = await db.execute_query(
        table="categories",
        filters={"id": budget['category_id']}
    )
    category_name = cat_result['data'][0]['name'] if cat_result['success'] and cat_result['data'] else 'Unknown'
    
    # Get transactions
    txn_result = await db.execute_query(
        table="transactions",
        filters={"user_id": user_id, "category_id": budget['category_id']}
    )
    transactions = txn_result['data'] if txn_result['success'] else []
    
    # Calculate variance
    budget_with_variance = calculate_budget_variance(budget, transactions)
    budget_with_variance['category_name'] = category_name
    
    return BudgetResponse(**budget_with_variance)


@router.patch("/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: str,
    updates: BudgetUpdate,
    user_id: str = Depends(get_current_user_id),
    db: DatabaseService = Depends(get_db_service)
):
    """Update budget"""
    # Verify ownership
    existing = await db.execute_query(
        table="budgets",
        filters={"id": budget_id, "user_id": user_id}
    )
    
    if not existing['success'] or not existing['data']:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    # Build update data
    update_data = updates.model_dump(exclude_unset=True)
    
    if 'period' in update_data:
        update_data['period'] = update_data['period'].value
    if 'end_date' in update_data and update_data['end_date']:
        update_data['end_date'] = update_data['end_date'].isoformat()
    
    result = await db.execute_query(
        table="budgets",
        operation="update",
        filters={"id": budget_id},
        data=update_data
    )
    
    if not result['success']:
        raise HTTPException(status_code=500, detail="Failed to update budget")
    
    updated_budget = result['data'][0]
    
    # Get category and transactions for variance
    cat_result = await db.execute_query(
        table="categories",
        filters={"id": updated_budget['category_id']}
    )
    category_name = cat_result['data'][0]['name'] if cat_result['success'] and cat_result['data'] else 'Unknown'
    
    txn_result = await db.execute_query(
        table="transactions",
        filters={"user_id": user_id, "category_id": updated_budget['category_id']}
    )
    transactions = txn_result['data'] if txn_result['success'] else []
    
    budget_with_variance = calculate_budget_variance(updated_budget, transactions)
    budget_with_variance['category_name'] = category_name
    
    return BudgetResponse(**budget_with_variance)


@router.delete("/{budget_id}", status_code=204)
async def delete_budget(
    budget_id: str,
    user_id: str = Depends(get_current_user_id),
    db: DatabaseService = Depends(get_db_service)
):
    """Delete budget"""
    existing = await db.execute_query(
        table="budgets",
        filters={"id": budget_id, "user_id": user_id}
    )
    
    if not existing['success'] or not existing['data']:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    result = await db.execute_query(
        table="budgets",
        operation="delete",
        filters={"id": budget_id}
    )
    
    if not result['success']:
        raise HTTPException(status_code=500, detail="Failed to delete budget")
    
    return None
