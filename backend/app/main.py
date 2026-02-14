"""
FastAPI main application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chatbot
from app.config import get_settings
from app.api import auth
from app.api import (
    transactions,
    budgets,
    goals,
    dashboard
)

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Smart Finance - AI-Powered Personal Finance Management API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(transactions.router, prefix=settings.API_V1_PREFIX)
app.include_router(budgets.router, prefix=settings.API_V1_PREFIX)
app.include_router(goals.router, prefix=settings.API_V1_PREFIX)
app.include_router(dashboard.router, prefix=settings.API_V1_PREFIX)
app.include_router(chatbot.router, prefix=settings.API_V1_PREFIX)
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)



@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Smart Finance API",
        "version": settings.VERSION,
        "docs": "/docs",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2026-02-14T03:21:00Z"
    }


# ============================================================
# TEST ENDPOINTS (No Authentication Required)
# ============================================================

@app.get("/test/info")
async def test_info():
    """Test endpoint - API information"""
    return {
        "api": "Smart Finance",
        "version": settings.VERSION,
        "status": "running",
        "features": {
            "ai_classification": True,
            "anomaly_detection": True,
            "forecasting": True,
            "budgets": True,
            "goals": True,
            "dashboard": True
        },
        "endpoints": {
            "test_classify": "/test/classify",
            "test_categories": "/test/categories",
            "swagger_docs": "/docs"
        }
    }


@app.get("/test/categories")
async def test_categories():
    """Test endpoint - returns mock categories"""
    return {
        "categories": [
            {"id": "1", "name": "Groceries", "icon": "🛒"},
            {"id": "2", "name": "Transport", "icon": "🚗"},
            {"id": "3", "name": "Dining", "icon": "🍽️"},
            {"id": "4", "name": "Bills & Utilities", "icon": "💡"},
            {"id": "5", "name": "Shopping", "icon": "🛍️"},
            {"id": "6", "name": "Entertainment", "icon": "🎬"},
            {"id": "7", "name": "Healthcare", "icon": "⚕️"},
            {"id": "8", "name": "Education", "icon": "📚"},
            {"id": "9", "name": "Income", "icon": "💰"},
            {"id": "10", "name": "Other", "icon": "📦"}
        ]
    }


@app.post("/test/classify")
async def test_classify(
    description: str,
    merchant: str,
    amount: float
):
    """
    Test AI classification without authentication
    
    Example:
    POST /test/classify?description=groceries&merchant=Carrefour&amount=50
    """
    from app.services.ai_service import get_ai_service
    
    ai = get_ai_service()
    
    mock_categories = [
        {"id": "1", "name": "Groceries"},
        {"id": "2", "name": "Transport"},
        {"id": "3", "name": "Dining"},
        {"id": "4", "name": "Bills & Utilities"},
        {"id": "5", "name": "Shopping"},
        {"id": "6", "name": "Entertainment"},
        {"id": "7", "name": "Healthcare"},
        {"id": "8", "name": "Education"},
        {"id": "9", "name": "Income"},
        {"id": "10", "name": "Other"}
    ]
    
    try:
        result = ai.classify_transaction(
            description=description,
            merchant=merchant,
            amount=amount,
            categories=mock_categories
        )
        
        return {
            "success": True,
            "input": {
                "description": description,
                "merchant": merchant,
                "amount": amount
            },
            "classification": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "input": {
                "description": description,
                "merchant": merchant,
                "amount": amount
            }
        }


@app.post("/test/detect-anomaly")
async def test_detect_anomaly(
    amount: float,
    category: str = "Groceries",
    description: str = "Transaction"
):
    """
    Test anomaly detection without authentication
    
    Example:
    POST /test/detect-anomaly?amount=5000&category=Groceries&description=Large+purchase
    """
    from app.services.ai_service import get_ai_service
    from datetime import date, timedelta
    import random
    
    ai = get_ai_service()
    
    # Mock current transaction
    current_transaction = {
        "id": "test-current",
        "amount": amount,
        "category": category,
        "description": description,
        "transaction_date": date.today().isoformat(),
        "transaction_type": "expense"
    }
    
    # Normal spending patterns by category
    category_patterns = {
        "Groceries": {"avg": 75, "std": 25},
        "Transport": {"avg": 45, "std": 15},
        "Dining": {"avg": 35, "std": 12},
        "Bills & Utilities": {"avg": 120, "std": 30},
        "Shopping": {"avg": 60, "std": 25},
        "Entertainment": {"avg": 40, "std": 15},
        "Healthcare": {"avg": 80, "std": 30},
        "Education": {"avg": 100, "std": 40},
        "Other": {"avg": 50, "std": 20}
    }
    
    pattern = category_patterns.get(category, {"avg": 50, "std": 20})
    
    # Generate EXACTLY 25 transactions (guaranteed > 20)
    mock_history = []
    for i in range(25):
        txn_date = date.today() - timedelta(days=i+1)
        
        # Normal amount with variation
        normal_amount = max(5, random.gauss(pattern["avg"], pattern["std"]))
        
        mock_history.append({
            "id": f"hist-{i}",
            "amount": round(normal_amount, 2),
            "category": category,
            "description": f"{category} purchase",
            "transaction_date": txn_date.isoformat(),
            "transaction_type": "expense"
        })
    
    try:
        # Detect anomaly with realistic history
        result = ai.detect_anomaly(current_transaction, mock_history)
        
        # Calculate stats for display
        avg_amount = sum(t["amount"] for t in mock_history) / len(mock_history)
        
        return {
            "success": True,
            "input": current_transaction,
            "history_stats": {
                "transaction_count": len(mock_history),
                "avg_amount": round(avg_amount, 2),
                "max_amount": round(max(t["amount"] for t in mock_history), 2),
                "min_amount": round(min(t["amount"] for t in mock_history), 2),
                "std_amount": round(
                    (sum((t["amount"] - avg_amount) ** 2 
                         for t in mock_history) / len(mock_history)) ** 0.5, 2
                )
            },
            "detection_result": result,  # This is what AI service returns
            "result": result if result else {
                "is_anomaly": False,
                "message": "Transaction appears normal",
                "anomaly_score": 0.0,
                "explanation": f"Amount {amount:.2f} is within normal range for {category}"
            }
        }
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "input": current_transaction,
            "history_count": len(mock_history)
        }



@app.get("/test/models-loaded")
async def test_models_loaded():
    """Check if AI models are loaded"""
    import os
    import traceback
    
    try:
        from app.services.ai_service import get_ai_service
        
        ai = get_ai_service()
        
        return {
            "success": True,
            "classifier": {
                "loaded": ai.classifier.is_trained,
                "model_path": settings.EXPENSE_CLASSIFIER_PATH,
                "file_exists": os.path.exists(settings.EXPENSE_CLASSIFIER_PATH)
            },
            "anomaly_detector": {
                "loaded": ai.anomaly_detector.is_trained if hasattr(ai.anomaly_detector, 'is_trained') else True,
                "model_path": settings.ANOMALY_DETECTOR_PATH,
                "file_exists": os.path.exists(settings.ANOMALY_DETECTOR_PATH)
            },
            "forecaster": {
                "loaded": ai.forecaster is not None,
                "available": ai.forecaster is not None
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc(),
            "classifier_path": settings.EXPENSE_CLASSIFIER_PATH,
            "classifier_exists": os.path.exists(settings.EXPENSE_CLASSIFIER_PATH),
            "anomaly_path": settings.ANOMALY_DETECTOR_PATH,
            "anomaly_exists": os.path.exists(settings.ANOMALY_DETECTOR_PATH)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
