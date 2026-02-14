"""
Goal API endpoints
CRUD + progress tracking
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import date, datetime
from app.models.goal import GoalCreate, GoalUpdate, GoalResponse, GoalStatus
from app.dependencies import get_current_user_id
from app.database import get_db_service, DatabaseService

router = APIRouter(prefix="/goals", tags=["Goals"])


def calculate_goal_progress(goal: dict) -> dict:
    """
    Calculate goal progress metrics
    
    Args:
        goal: Goal dict
        
    Returns:
        Goal with progress calculations
    """
    target_amount = goal['target_amount']
    current_amount = goal['current_amount']
    target_date = datetime.fromisoformat(goal['target_date']).date() if isinstance(goal['target_date'], str) else goal['target_date']
    today = date.today()
    
    # Progress percentage
    progress_percent = (current_amount / target_amount * 100) if target_amount > 0 else 0
    
    # Remaining amount
    remaining_amount = max(0, target_amount - current_amount)
    
    # Days remaining
    days_remaining = (target_date - today).days
    
    # Required monthly contribution
    if days_remaining > 0 and remaining_amount > 0:
        months_remaining = days_remaining / 30.0
        required_monthly = remaining_amount / months_remaining if months_remaining > 0 else remaining_amount
    else:
        required_monthly = 0
    
    # On track calculation (simple heuristic)
    days_elapsed = (today - datetime.fromisoformat(goal['created_at']).date()).days
    total_days = (target_date - datetime.fromisoformat(goal['created_at']).date()).days
    expected_progress = (days_elapsed / total_days * 100) if total_days > 0 else 0
    on_track = progress_percent >= expected_progress * 0.9  # 90% of expected progress
    
    return {
        **goal,
        'progress_percent': round(progress_percent, 2),
        'remaining_amount': remaining_amount,
        'days_remaining': days_remaining,
        'required_monthly_contribution': round(required_monthly, 2),
        'on_track': on_track
    }


@router.post("/", response_model=GoalResponse, status_code=201)
async def create_goal(
    goal: GoalCreate,
    user_id: str = Depends(get_current_user_id),
    db: DatabaseService = Depends(get_db_service)
):
    """
    Create new financial goal
    
    - Set target amount and date
    - Track progress automatically
    - Get recommendations to stay on track
    """
    goal_data = {
        "user_id": user_id,
        "name": goal.name,
        "target_amount": goal.target_amount,
        "current_amount": goal.current_amount,
        "target_date": goal.target_date.isoformat(),
        "category": goal.category,
        "description": goal.description,
        "status": GoalStatus.IN_PROGRESS.value
    }
    
    result = await db.execute_query(
        table="goals",
        operation="insert",
        data=goal_data
    )
    
    if not result['success']:
        raise HTTPException(status_code=500, detail="Failed to create goal")
    
    created_goal = result['data'][0]
    goal_with_progress = calculate_goal_progress(created_goal)
    
    return GoalResponse(**goal_with_progress)


@router.get("/", response_model=List[GoalResponse])
async def list_goals(
    user_id: str = Depends(get_current_user_id),
    db: DatabaseService = Depends(get_db_service),
    status: str = None
):
    """
    List all goals with progress
    
    Query params:
    - status: Filter by status (in_progress, completed, cancelled)
    """
    filters = {"user_id": user_id}
    if status:
        filters["status"] = status
    
    result = await db.execute_query(
        table="goals",
        filters=filters,
        order_by="target_date"
    )
    
    if not result['success']:
        raise HTTPException(status_code=500, detail="Failed to fetch goals")
    
    goals = result['data']
    
    # Calculate progress for each goal
    response_goals = [
        GoalResponse(**calculate_goal_progress(goal))
        for goal in goals
    ]
    
    return response_goals


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: str,
    user_id: str = Depends(get_current_user_id),
    db: DatabaseService = Depends(get_db_service)
):
    """Get goal by ID with progress"""
    result = await db.execute_query(
        table="goals",
        filters={"id": goal_id, "user_id": user_id}
    )
    
    if not result['success'] or not result['data']:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    goal = result['data'][0]
    goal_with_progress = calculate_goal_progress(goal)
    
    return GoalResponse(**goal_with_progress)


@router.patch("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: str,
    updates: GoalUpdate,
    user_id: str = Depends(get_current_user_id),
    db: DatabaseService = Depends(get_db_service)
):
    """Update goal (including progress)"""
    existing = await db.execute_query(
        table="goals",
        filters={"id": goal_id, "user_id": user_id}
    )
    
    if not existing['success'] or not existing['data']:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    update_data = updates.model_dump(exclude_unset=True)
    
    if 'target_date' in update_data:
        update_data['target_date'] = update_data['target_date'].isoformat()
    if 'status' in update_data:
        update_data['status'] = update_data['status'].value
    
    result = await db.execute_query(
        table="goals",
        operation="update",
        filters={"id": goal_id},
        data=update_data
    )
    
    if not result['success']:
        raise HTTPException(status_code=500, detail="Failed to update goal")
    
    updated_goal = result['data'][0]
    goal_with_progress = calculate_goal_progress(updated_goal)
    
    return GoalResponse(**goal_with_progress)


@router.delete("/{goal_id}", status_code=204)
async def delete_goal(
    goal_id: str,
    user_id: str = Depends(get_current_user_id),
    db: DatabaseService = Depends(get_db_service)
):
    """Delete goal"""
    existing = await db.execute_query(
        table="goals",
        filters={"id": goal_id, "user_id": user_id}
    )
    
    if not existing['success'] or not existing['data']:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    result = await db.execute_query(
        table="goals",
        operation="delete",
        filters={"id": goal_id}
    )
    
    if not result['success']:
        raise HTTPException(status_code=500, detail="Failed to delete goal")
    
    return None
