"""
FastAPI dependency injection
Authentication, user extraction, etc.
"""

from fastapi import Depends, HTTPException, status, Header
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from app.config import get_settings
from app.database import get_supabase_client, DatabaseService, get_db_service
from supabase import Client


settings = get_settings()


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: DatabaseService = Depends(get_db_service)
) -> Dict[str, Any]:
    """
    Extract and verify current user from JWT token
    
    Args:
        authorization: Bearer token from header
        db: Database service
        
    Returns:
        User dict with id, email, etc.
        
    Raises:
        HTTPException: If token invalid or user not found
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Extract token
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    # Verify token with Supabase
    try:
        supabase = get_supabase_client()
        user_response = supabase.auth.get_user(token)
        
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        user = user_response.user
        
        return {
            "id": user.id,
            "email": user.email,
            "user_metadata": user.user_metadata or {}
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}"
        )


async def get_current_user_id(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> str:
    """Extract just the user ID"""
    return current_user["id"]


# Optional: For endpoints that don't require auth
async def get_optional_user(
    authorization: Optional[str] = Header(None)
) -> Optional[Dict[str, Any]]:
    """Get user if token provided, otherwise None"""
    if not authorization:
        return None
    
    try:
        return await get_current_user(authorization)
    except HTTPException:
        return None
