"""
API routes for SPV Treasure Map
"""
from app.api.battles import router as battles_router
from app.api.places import router as places_router

__all__ = [
    "battles_router",
    "places_router",
]
