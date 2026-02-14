"""
Supabase database client and utilities
"""

from supabase import create_client, Client
from typing import Optional, Dict, Any, List
from functools import lru_cache
from app.config import get_settings


settings = get_settings()


@lru_cache()
def get_supabase_client() -> Client:
    """Get cached Supabase client (anon key)"""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


@lru_cache()
def get_supabase_admin_client() -> Client:
    """Get cached Supabase admin client (service role key)"""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)


class DatabaseService:
    """Helper service for database operations"""
    
    def __init__(self, client: Client):
        self.client = client
    
    async def execute_query(
        self,
        table: str,
        operation: str = "select",
        filters: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute a database query
        
        Args:
            table: Table name
            operation: 'select', 'insert', 'update', 'delete'
            filters: Filter conditions (e.g., {'user_id': 'uuid'})
            data: Data for insert/update
            order_by: Column to order by
            limit: Result limit
            
        Returns:
            Query result
        """
        try:
            query = self.client.table(table)
            
            if operation == "select":
                query = query.select("*")
                
                if filters:
                    for key, value in filters.items():
                        query = query.eq(key, value)
                
                if order_by:
                    query = query.order(order_by, desc=True)
                
                if limit:
                    query = query.limit(limit)
                
                response = query.execute()
                
            elif operation == "insert":
                if not data:
                    raise ValueError("Data required for insert")
                response = query.insert(data).execute()
                
            elif operation == "update":
                if not data or not filters:
                    raise ValueError("Data and filters required for update")
                
                query = query.update(data)
                for key, value in filters.items():
                    query = query.eq(key, value)
                response = query.execute()
                
            elif operation == "delete":
                if not filters:
                    raise ValueError("Filters required for delete")
                
                for key, value in filters.items():
                    query = query.eq(key, value)
                response = query.delete().execute()
                
            else:
                raise ValueError(f"Unknown operation: {operation}")
            
            return {
                "success": True,
                "data": response.data,
                "count": len(response.data) if response.data else 0
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    async def execute_rpc(
        self,
        function_name: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a PostgreSQL function via RPC
        
        Args:
            function_name: Name of the function
            params: Function parameters
            
        Returns:
            Function result
        """
        try:
            response = self.client.rpc(function_name, params or {}).execute()
            
            return {
                "success": True,
                "data": response.data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": None
            }


def get_db_service() -> DatabaseService:
    """Get database service instance"""
    return DatabaseService(get_supabase_client())


def get_admin_db_service() -> DatabaseService:
    """Get admin database service instance"""
    return DatabaseService(get_supabase_admin_client())
