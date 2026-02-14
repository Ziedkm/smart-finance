"""
Run the FastAPI server
"""

import uvicorn
from app.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    
    print("=" * 60)
    print("🚀 Starting Smart Finance API Server")
    print("=" * 60)
    print(f"📡 Host: {settings.API_HOST}:{settings.API_PORT}")
    print(f"📚 Docs: http://localhost:{settings.API_PORT}/docs")
    print(f"🔧 Debug: {settings.DEBUG}")
    print("=" * 60)
    
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
