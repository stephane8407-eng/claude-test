"""
SPV Treasure Map - FastAPI Backend
Main application entry point.
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pathlib import Path
from app.database import check_postgis, get_db
import os

# Create FastAPI app
app = FastAPI(
    title="SPV Treasure Map API",
    description="Historical treasure hunting intelligence platform for France, UK, and Belgium",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS - explicitly list allowed origins for credentials support
# Note: allow_origins=["*"] with allow_credentials=True is blocked by browsers
CORS_ORIGINS = [
    "http://localhost:5173",      # Vite dev server
    "http://localhost:3000",      # Alternative dev port
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
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


@app.get("/api/cache/stats")
async def get_cache_statistics():
    """
    Get cache performance statistics.

    Returns cache hit/miss rates for monitoring performance.
    """
    from app.utils import get_cache_stats
    return get_cache_stats()


# Import and include routers
from app.api.battles import router as battles_router
from app.api.places import router as places_router
from app.api.conflicts import router as conflicts_router
from app.api.villages import router as villages_router
from app.api.pois import router as pois_router
from app.api import identity
from app.api.auth import router as auth_router
from app.api.qr_codes import router as qr_codes_router

# V1 Product Spec - New routers
from app.api.topics import router as topics_router
from app.api.sponsors import router as sponsors_router
from app.api.projects import router as projects_router
from app.api.upload import router as upload_router

# Phase D: RAG Foundation
from app.api.case_studies import router as case_studies_router
from app.api.funding_programs import router as funding_programs_router
from app.api.identity_generation import router as identity_generation_router
from app.api.village_identity import router as village_identity_router

# Phase E: Project Management Dashboard
from app.api.project_kanban import router as project_kanban_router

# Phase E Week 2: Grant Application Generator
from app.api.grants import router as grants_router

app.include_router(battles_router)
app.include_router(places_router)
app.include_router(conflicts_router)
app.include_router(villages_router)
app.include_router(pois_router)
app.include_router(identity.router)
app.include_router(auth_router)
app.include_router(qr_codes_router, prefix="/api", tags=["qr_codes"])

# V1 Product Spec - New routers
app.include_router(topics_router)
app.include_router(sponsors_router)
app.include_router(projects_router)
app.include_router(upload_router)

# Phase D: RAG Foundation
app.include_router(case_studies_router)
app.include_router(funding_programs_router)
app.include_router(identity_generation_router)
app.include_router(village_identity_router)

# Phase E: Project Management Dashboard
app.include_router(project_kanban_router)

# Phase E Week 2: Grant Application Generator
app.include_router(grants_router)


# ============================================================================
# Sponsor Click Tracking (Root-level endpoint per spec)
# ============================================================================

@app.get("/api/sponsor-click/{slot_id}")
def sponsor_click_redirect(slot_id: int, db: Session = Depends(get_db)):
    """
    Track a sponsor click and redirect to sponsor website.

    Per spec section 5: /api/sponsor-click/[slotId]
    1. Increment click_count on SponsorSlot
    2. Look up Sponsor.website_url
    3. Redirect (302) to sponsor website
    """
    from app.models.sponsor_slot import SponsorSlot

    slot = db.query(SponsorSlot).filter(SponsorSlot.id == slot_id).first()

    if not slot:
        raise HTTPException(status_code=404, detail=f"Sponsor slot {slot_id} not found")

    sponsor = slot.sponsor
    if not sponsor or not sponsor.website_url:
        raise HTTPException(status_code=404, detail="Sponsor website not configured")

    # Increment click count
    slot.increment_clicks()
    db.commit()

    # Redirect to sponsor website
    return RedirectResponse(url=sponsor.website_url, status_code=302)


# ============================================================================
# Static File Serving (for uploads - use nginx in production)
# ============================================================================

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
for subdir in ["heroes", "logos", "gpx", "general"]:
    (UPLOAD_DIR / subdir).mkdir(exist_ok=True)

# Mount static files for uploads
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


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
