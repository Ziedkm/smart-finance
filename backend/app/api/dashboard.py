"""
Dashboard API endpoint
Aggregated KPIs and insights
"""

from fastapi import APIRouter, Depends, HTTPException
from datetime import date, datetime, timedelta
from typing import List
from app.models.dashboard import (
    DashboardResponse, DashboardKPIs, CategorySpending, MonthlyTrend
)
from app.dependencies import get_current_user_id
from app.database import get_db_service, DatabaseService
from app.api.budgets import calculate_budget_variance

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/", response_model=DashboardResponse)
async def get_dashboard(
    user_id: str = Depends(get_current_user_id),
    db: DatabaseService = Depends(get_db_service)
):
    """
    Get dashboard overview with KPIs
    
    Returns:
    - Current month income/expenses/savings
    - Budget health summary
    - Goal progress summary
    - Spending breakdown by category
    - Monthly trends (last 6 months)
    - Top expenses
    - Recent transactions
    """
    today = date.today()
    
    # Current month dates
    month_start = today.replace(day=1)
    next_month = (month_start + timedelta(days=32)).replace(day=1)
    month_end = next_month - timedelta(days=1)
    
    # Get all user data
    transactions_result = await db.execute_query(
        table="transactions",
        filters={"user_id": user_id}
    )
    transactions = transactions_result['data'] if transactions_result['success'] else []
    
    budgets_result = await db.execute_query(
        table="budgets",
        filters={"user_id": user_id, "is_active": True}
    )
    budgets = budgets_result['data'] if budgets_result['success'] else []
    
    goals_result = await db.execute_query(
        table="goals",
        filters={"user_id": user_id, "status": "in_progress"}
    )
    goals = goals_result['data'] if goals_result['success'] else []
    
    anomalies_result = await db.execute_query(
        table="anomalies",
        filters={"user_id": user_id, "status": "pending"}
    )
    pending_anomalies = len(anomalies_result['data']) if anomalies_result['success'] else 0
    
    categories_result = await db.execute_query(
        table="categories",
        filters={"user_id": user_id}
    )
    categories = categories_result['data'] if categories_result['success'] else []
    category_map = {c['id']: c['name'] for c in categories}
    
    # === KPIs ===
    
    # Current month transactions
    current_month_txns = [
        t for t in transactions
        if month_start <= datetime.fromisoformat(t['transaction_date']).date() <= month_end
    ]
    
    total_income = sum(t['amount'] for t in current_month_txns if t['transaction_type'] == 'income')
    total_expenses = sum(t['amount'] for t in current_month_txns if t['transaction_type'] == 'expense')
    net_savings = total_income - total_expenses
    savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0
    
    # Budget health
    budgets_on_track = 0
    budgets_warning = 0
    budgets_exceeded = 0
    
    for budget in budgets:
        category_txns = [t for t in transactions if t['category_id'] == budget['category_id']]
        budget_with_variance = calculate_budget_variance(budget, category_txns)
        
        status = budget_with_variance['status']
        if status == 'on_track':
            budgets_on_track += 1
        elif status == 'warning':
            budgets_warning += 1
        elif status == 'exceeded':
            budgets_exceeded += 1
    
    # Goals (simple on-track calculation)
    from app.api.goals import calculate_goal_progress
    goals_on_track = 0
    for goal in goals:
        goal_progress = calculate_goal_progress(goal)
        if goal_progress['on_track']:
            goals_on_track += 1
    
    # Expense trend (compare to previous month)
    prev_month_start = (month_start - timedelta(days=1)).replace(day=1)
    prev_month_txns = [
        t for t in transactions
        if prev_month_start <= datetime.fromisoformat(t['transaction_date']).date() < month_start
        and t['transaction_type'] == 'expense'
    ]
    prev_month_expenses = sum(t['amount'] for t in prev_month_txns)
    
    if prev_month_expenses > 0:
        expense_change = ((total_expenses - prev_month_expenses) / prev_month_expenses) * 100
        if expense_change > 5:
            expense_trend = 'up'
        elif expense_change < -5:
            expense_trend = 'down'
        else:
            expense_trend = 'stable'
    else:
        expense_trend = 'stable'
        expense_change = 0
    
    kpis = DashboardKPIs(
        total_income=total_income,
        total_expenses=total_expenses,
        net_savings=net_savings,
        savings_rate=savings_rate,
        budgets_on_track=budgets_on_track,
        budgets_warning=budgets_warning,
        budgets_exceeded=budgets_exceeded,
        active_goals_count=len(goals),
        goals_on_track=goals_on_track,
        pending_anomalies=pending_anomalies,
        expense_trend=expense_trend,
        expense_change_percent=expense_change
    )
    
    # === Category Breakdown ===
    category_spending_map = {}
    for txn in current_month_txns:
        if txn['transaction_type'] == 'expense':
            cat_id = txn.get('category_id')
            if cat_id:
                cat_name = category_map.get(cat_id, 'Other')
                if cat_name not in category_spending_map:
                    category_spending_map[cat_name] = {'amount': 0, 'count': 0}
                category_spending_map[cat_name]['amount'] += txn['amount']
                category_spending_map[cat_name]['count'] += 1
    
    category_breakdown = []
    for cat_name, data in category_spending_map.items():
        category_breakdown.append(CategorySpending(
            category_name=cat_name,
            amount=data['amount'],
            percentage=(data['amount'] / total_expenses * 100) if total_expenses > 0 else 0,
            transaction_count=data['count']
        ))
    category_breakdown.sort(key=lambda x: x.amount, reverse=True)
    
    # === Monthly Trends (last 6 months) ===
    monthly_trends = []
    for i in range(5, -1, -1):
        trend_month_start = (today.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
        trend_month_end = (trend_month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        trend_txns = [
            t for t in transactions
            if trend_month_start <= datetime.fromisoformat(t['transaction_date']).date() <= trend_month_end
        ]
        
        trend_income = sum(t['amount'] for t in trend_txns if t['transaction_type'] == 'income')
        trend_expenses = sum(t['amount'] for t in trend_txns if t['transaction_type'] == 'expense')
        
        monthly_trends.append(MonthlyTrend(
            month=trend_month_start.strftime('%Y-%m'),
            income=trend_income,
            expenses=trend_expenses,
            net=trend_income - trend_expenses
        ))
    
    # === Top Expenses (current month) ===
    top_expenses = sorted(
        [t for t in current_month_txns if t['transaction_type'] == 'expense'],
        key=lambda x: x['amount'],
        reverse=True
    )[:5]
    
    top_expenses_formatted = [
        {
            'id': t['id'],
            'description': t.get('description') or t.get('merchant') or 'Transaction',
            'amount': t['amount'],
            'category': category_map.get(t.get('category_id'), 'Other'),
            'date': t['transaction_date']
        }
        for t in top_expenses
    ]
    
    # === Recent Transactions ===
    recent_transactions = sorted(
        transactions,
        key=lambda x: x['transaction_date'],
        reverse=True
    )[:10]
    
    recent_txns_formatted = [
        {
            'id': t['id'],
            'description': t.get('description') or t.get('merchant') or 'Transaction',
            'amount': t['amount'],
            'type': t['transaction_type'],
            'category': category_map.get(t.get('category_id'), 'Other'),
            'date': t['transaction_date']
        }
        for t in recent_transactions
    ]
    
    return DashboardResponse(
        kpis=kpis,
        category_breakdown=category_breakdown,
        monthly_trends=monthly_trends,
        top_expenses=top_expenses_formatted,
        recent_transactions=recent_txns_formatted
    )
