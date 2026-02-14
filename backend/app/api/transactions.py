"""
Transaction API endpoints
CRUD + AI classification + anomaly detection
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import date, datetime, timedelta
from app.models.transaction import (
    TransactionCreate, TransactionUpdate, TransactionResponse,
    TransactionListResponse, CategorySuggestion
)
from app.dependencies import get_current_user_id
from app.database import get_db_service, DatabaseService
from app.services.ai_service import get_ai_service, AIService

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/", response_model=TransactionResponse, status_code=201)
async def create_transaction(
    transaction: TransactionCreate,
    user_id: str = Depends(get_current_user_id),
    db: DatabaseService = Depends(get_db_service),
    ai: AIService = Depends(get_ai_service)
):
    """
    Create new transaction with AI category suggestion
    
    - Automatically classifies transaction if category not provided
    - Detects anomalies in spending patterns
    - Returns transaction with AI suggestion
    """
    # Get user's categories
    categories_result = await db.execute_query(
        table="categories",
        filters={"user_id": user_id}
    )
    
    if not categories_result['success']:
        raise HTTPException(status_code=500, detail="Failed to fetch categories")
    
    categories = categories_result['data']
    
    # AI classification if category not provided
    ai_suggestion = None
    category_id = transaction.category_id
    category_confidence = None
    is_category_verified = transaction.category_id is not None
    
    if not category_id:
        # Get AI suggestion
        classification = ai.classify_transaction(
            description=transaction.description or '',
            merchant=transaction.merchant or '',
            amount=transaction.amount,
            categories=categories
        )
        
        category_id = classification['category_id']
        category_confidence = classification['confidence']
        
        ai_suggestion = CategorySuggestion(
            category_id=classification['category_id'],
            category_name=classification['category_name'],
            confidence=classification['confidence'],
            explanation=classification['explanation'],
            method=classification['method'],
            top_3_predictions=classification['top_3_predictions']
        )
    
    # Create transaction
    txn_data = {
        "user_id": user_id,
        "account_id": transaction.account_id,
        "amount": transaction.amount,
        "transaction_type": transaction.transaction_type.value,
        "transaction_date": transaction.transaction_date.isoformat(),
        "description": transaction.description,
        "merchant": transaction.merchant,
        "category_id": category_id,
        "category_confidence": category_confidence,
        "is_category_verified": is_category_verified,
        "notes": transaction.notes,
        "tags": transaction.tags,
        "is_recurring": transaction.is_recurring,
        "recurring_frequency": transaction.recurring_frequency
    }
    
    result = await db.execute_query(
        table="transactions",
        operation="insert",
        data=txn_data
    )
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=f"Failed to create transaction: {result['error']}")
    
    created_txn = result['data'][0]
    
    # Anomaly detection (async, don't block response)
    try:
        # Get user's recent transactions for context
        history_result = await db.execute_query(
            table="transactions",
            filters={"user_id": user_id},
            order_by="transaction_date",
            limit=100
        )
        
        if history_result['success']:
            anomaly_result = ai.detect_anomaly(
                transaction=created_txn,
                user_history=history_result['data']
            )
            
            if anomaly_result and anomaly_result['is_anomaly']:
                # Store anomaly
                await db.execute_query(
                    table="anomalies",
                    operation="insert",
                    data={
                        "user_id": user_id,
                        "transaction_id": created_txn['id'],
                        "anomaly_score": anomaly_result['anomaly_score'],
                        "explanation": anomaly_result['explanation'],
                        "status": "pending"
                    }
                )
    except Exception as e:
        # Log error but don't fail the request
        print(f"Anomaly detection failed: {e}")
    
    # Get category name
    category_name = None
    if category_id:
        cat = next((c for c in categories if c['id'] == category_id), None)
        if cat:
            category_name = cat['name']
    
    # Build response
    response_data = TransactionResponse(
        **created_txn,
        category_name=category_name,
        ai_suggestion=ai_suggestion if not is_category_verified else None
    )
    
    return response_data


@router.get("/", response_model=TransactionListResponse)
async def list_transactions(
    user_id: str = Depends(get_current_user_id),
    db: DatabaseService = Depends(get_db_service),
    account_id: Optional[str] = None,
    category_id: Optional[str] = None,
    transaction_type: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100)
):
    """
    List transactions with filters and pagination
    
    Query params:
    - account_id: Filter by account
    - category_id: Filter by category
    - transaction_type: 'income' or 'expense'
    - start_date, end_date: Date range
    - page, page_size: Pagination
    """
    # Build filters
    filters = {"user_id": user_id}
    if account_id:
        filters["account_id"] = account_id
    if category_id:
        filters["category_id"] = category_id
    if transaction_type:
        filters["transaction_type"] = transaction_type
    
    # TODO: Add date range filtering (requires custom query)
    # For now, fetch all and filter in Python
    
    result = await db.execute_query(
        table="transactions",
        filters=filters,
        order_by="transaction_date"
    )
    
    if not result['success']:
        raise HTTPException(status_code=500, detail="Failed to fetch transactions")
    
    transactions = result['data']
    
    # Date filtering
    if start_date or end_date:
        transactions = [
            t for t in transactions
            if (not start_date or datetime.fromisoformat(t['transaction_date']).date() >= start_date) and
               (not end_date or datetime.fromisoformat(t['transaction_date']).date() <= end_date)
        ]
    
    # Get categories for name mapping
    categories_result = await db.execute_query(
        table="categories",
        filters={"user_id": user_id}
    )
    category_map = {c['id']: c['name'] for c in categories_result['data']} if categories_result['success'] else {}
    
    # Pagination
    total = len(transactions)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_transactions = transactions[start_idx:end_idx]
    
    # Build response
    response_transactions = []
    for txn in page_transactions:
        response_transactions.append(
            TransactionResponse(
                **txn,
                category_name=category_map.get(txn.get('category_id')),
                ai_suggestion=None  # Don't include in list view
            )
        )
    
    return TransactionListResponse(
        transactions=response_transactions,
        total=total,
        page=page,
        page_size=page_size,
        has_more=end_idx < total
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    user_id: str = Depends(get_current_user_id),
    db: DatabaseService = Depends(get_db_service)
):
    """Get transaction by ID"""
    result = await db.execute_query(
        table="transactions",
        filters={"id": transaction_id, "user_id": user_id}
    )
    
    if not result['success'] or not result['data']:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    txn = result['data'][0]
    
    # Get category name
    if txn.get('category_id'):
        cat_result = await db.execute_query(
            table="categories",
            filters={"id": txn['category_id']}
        )
        category_name = cat_result['data'][0]['name'] if cat_result['success'] and cat_result['data'] else None
    else:
        category_name = None
    
    return TransactionResponse(**txn, category_name=category_name, ai_suggestion=None)


@router.patch("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: str,
    updates: TransactionUpdate,
    user_id: str = Depends(get_current_user_id),
    db: DatabaseService = Depends(get_db_service)
):
    """Update transaction"""
    # Verify ownership
    existing = await db.execute_query(
        table="transactions",
        filters={"id": transaction_id, "user_id": user_id}
    )
    
    if not existing['success'] or not existing['data']:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Build update data
    update_data = updates.model_dump(exclude_unset=True)
    
    # Convert enums to strings
    if 'transaction_type' in update_data:
        update_data['transaction_type'] = update_data['transaction_type'].value
    
    # Convert dates to ISO strings
    if 'transaction_date' in update_data:
        update_data['transaction_date'] = update_data['transaction_date'].isoformat()
    
    result = await db.execute_query(
        table="transactions",
        operation="update",
        filters={"id": transaction_id},
        data=update_data
    )
    
    if not result['success']:
        raise HTTPException(status_code=500, detail="Failed to update transaction")
    
    updated_txn = result['data'][0]
    
    # Get category name
    category_name = None
    if updated_txn.get('category_id'):
        cat_result = await db.execute_query(
            table="categories",
            filters={"id": updated_txn['category_id']}
        )
        category_name = cat_result['data'][0]['name'] if cat_result['success'] and cat_result['data'] else None
    
    return TransactionResponse(**updated_txn, category_name=category_name, ai_suggestion=None)


@router.delete("/{transaction_id}", status_code=204)
async def delete_transaction(
    transaction_id: str,
    user_id: str = Depends(get_current_user_id),
    db: DatabaseService = Depends(get_db_service)
):
    """Delete transaction"""
    # Verify ownership
    existing = await db.execute_query(
        table="transactions",
        filters={"id": transaction_id, "user_id": user_id}
    )
    
    if not existing['success'] or not existing['data']:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    result = await db.execute_query(
        table="transactions",
        operation="delete",
        filters={"id": transaction_id}
    )
    
    if not result['success']:
        raise HTTPException(status_code=500, detail="Failed to delete transaction")
    
    return None
