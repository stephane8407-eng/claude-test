"""
SPV Treasure Map - FastAPI Backend
Main application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import check_postgis
import os

# Create FastAPI app
app = FastAPI(
    title="SPV Treasure Map API",
    description="Historical treasure hunting intelligence platform for France, UK, and Belgium",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    print("🚀 Starting SPV Treasure Map API...")

    # Check PostGIS
    try:
        check_postgis()
    except Exception as e:
        print(f"⚠️  Warning: Could not verify PostGIS: {e}")

    print("✅ API started successfully!")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    print("👋 Shutting down SPV Treasure Map API...")


@app.get("/")
async def root():
    """Root endpoint - API status."""
    return {
        "name": "SPV Treasure Map API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected"  # TODO: Add actual DB check
    }


# Import and include routers
# TODO: Uncomment when routes are created
# from app.api import battles, places, users
# app.include_router(battles.router, prefix="/api", tags=["battles"])
# app.include_router(places.router, prefix="/api", tags=["places"])
# app.include_router(users.router, prefix="/api", tags=["users"])


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "True").lower() == "true"

    print(f"🌍 Starting server at http://{host}:{port}")
    print(f"📚 API docs at http://{host}:{port}/api/docs")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload
    )
