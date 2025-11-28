"""
Sponsors API - CRUD endpoints for partners and advertisers
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from pydantic import BaseModel
from datetime import date

from app.database import get_db
from app.models.sponsor import Sponsor
from app.models.sponsor_slot import SponsorSlot


router = APIRouter(prefix="/api/sponsors", tags=["sponsors"])


# ============================================================================
# Pydantic Schemas
# ============================================================================

class SponsorCreate(BaseModel):
    name: str
    slug: str
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    short_description: Optional[str] = None
    type: str  # 'local_business', 'regional_partner', 'founding_partner'
    sector: Optional[str] = None
    regions: Optional[List[str]] = None


class SponsorUpdate(BaseModel):
    name: Optional[str] = None
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    short_description: Optional[str] = None
    type: Optional[str] = None
    sector: Optional[str] = None
    regions: Optional[List[str]] = None
    is_active: Optional[bool] = None


class SponsorSlotCreate(BaseModel):
    sponsor_id: int
    object_type: str  # 'settlement', 'route', 'topic'
    object_id: int
    position: Optional[str] = 'primary'
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class SponsorSlotUpdate(BaseModel):
    position: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None


# ============================================================================
# Sponsor Endpoints
# ============================================================================

@router.get("/", response_model=dict)
def list_sponsors(
    type: Optional[str] = Query(None, description="Filter by type"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    region: Optional[str] = Query(None, description="Filter by region"),
    active_only: bool = Query(True, description="Only return active sponsors"),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List all sponsors with optional filters.
    """
    query = db.query(Sponsor)

    if active_only:
        query = query.filter(Sponsor.is_active == True)

    if type:
        query = query.filter(Sponsor.type == type)

    if sector:
        query = query.filter(Sponsor.sector == sector)

    if region:
        query = query.filter(Sponsor.regions.contains([region]))

    total = query.count()
    sponsors = query.order_by(Sponsor.name).offset(offset).limit(limit).all()

    return {
        "results": [s.to_dict() for s in sponsors],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/{slug}", response_model=dict)
def get_sponsor(slug: str, include_slots: bool = False, db: Session = Depends(get_db)):
    """Get a single sponsor by slug."""
    sponsor = db.query(Sponsor).filter(Sponsor.slug == slug).first()

    if not sponsor:
        raise HTTPException(status_code=404, detail=f"Sponsor '{slug}' not found")

    return sponsor.to_dict(include_slots=include_slots)


@router.post("/", response_model=dict, status_code=201)
def create_sponsor(
    sponsor_data: SponsorCreate,
    db: Session = Depends(get_db)
    # TODO: Add auth dependency: current_user = Depends(require_platform_admin)
):
    """
    Create a new sponsor.

    Requires platform_admin role.
    """
    # Validate type
    valid_types = ['local_business', 'regional_partner', 'founding_partner']
    if sponsor_data.type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid type. Must be one of: {valid_types}")

    # Check for duplicate slug
    existing = db.query(Sponsor).filter(Sponsor.slug == sponsor_data.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Sponsor with slug '{sponsor_data.slug}' already exists")

    sponsor = Sponsor(
        name=sponsor_data.name,
        slug=sponsor_data.slug,
        logo_url=sponsor_data.logo_url,
        website_url=sponsor_data.website_url,
        short_description=sponsor_data.short_description,
        type=sponsor_data.type,
        sector=sponsor_data.sector,
        regions=sponsor_data.regions
    )

    db.add(sponsor)
    db.commit()
    db.refresh(sponsor)

    return sponsor.to_dict()


@router.put("/{slug}", response_model=dict)
def update_sponsor(
    slug: str,
    sponsor_data: SponsorUpdate,
    db: Session = Depends(get_db)
    # TODO: Add auth dependency: current_user = Depends(require_platform_admin)
):
    """
    Update a sponsor.

    Requires platform_admin role.
    """
    sponsor = db.query(Sponsor).filter(Sponsor.slug == slug).first()

    if not sponsor:
        raise HTTPException(status_code=404, detail=f"Sponsor '{slug}' not found")

    # Validate type if provided
    if sponsor_data.type is not None:
        valid_types = ['local_business', 'regional_partner', 'founding_partner']
        if sponsor_data.type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid type. Must be one of: {valid_types}")
        sponsor.type = sponsor_data.type

    # Update fields if provided
    if sponsor_data.name is not None:
        sponsor.name = sponsor_data.name
    if sponsor_data.logo_url is not None:
        sponsor.logo_url = sponsor_data.logo_url
    if sponsor_data.website_url is not None:
        sponsor.website_url = sponsor_data.website_url
    if sponsor_data.short_description is not None:
        sponsor.short_description = sponsor_data.short_description
    if sponsor_data.sector is not None:
        sponsor.sector = sponsor_data.sector
    if sponsor_data.regions is not None:
        sponsor.regions = sponsor_data.regions
    if sponsor_data.is_active is not None:
        sponsor.is_active = sponsor_data.is_active

    db.commit()
    db.refresh(sponsor)

    return sponsor.to_dict()


@router.delete("/{slug}", status_code=204)
def delete_sponsor(
    slug: str,
    db: Session = Depends(get_db)
    # TODO: Add auth dependency: current_user = Depends(require_platform_admin)
):
    """
    Delete a sponsor and all associated slots.

    Requires platform_admin role.
    """
    sponsor = db.query(Sponsor).filter(Sponsor.slug == slug).first()

    if not sponsor:
        raise HTTPException(status_code=404, detail=f"Sponsor '{slug}' not found")

    db.delete(sponsor)
    db.commit()

    return None


# ============================================================================
# Sponsor Slot Endpoints
# ============================================================================

@router.get("/slots/", response_model=dict)
def list_sponsor_slots(
    sponsor_id: Optional[int] = None,
    object_type: Optional[str] = None,
    object_id: Optional[int] = None,
    active_only: bool = Query(True),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List sponsor slots with optional filters.
    """
    query = db.query(SponsorSlot)

    if active_only:
        today = date.today()
        query = query.filter(
            SponsorSlot.is_active == True,
            or_(SponsorSlot.start_date == None, SponsorSlot.start_date <= today),
            or_(SponsorSlot.end_date == None, SponsorSlot.end_date >= today)
        )

    if sponsor_id:
        query = query.filter(SponsorSlot.sponsor_id == sponsor_id)

    if object_type:
        query = query.filter(SponsorSlot.object_type == object_type)

    if object_id:
        query = query.filter(SponsorSlot.object_id == object_id)

    total = query.count()
    slots = query.order_by(SponsorSlot.position, SponsorSlot.created_at).offset(offset).limit(limit).all()

    return {
        "results": [s.to_dict(include_sponsor=True) for s in slots],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/slots/{slot_id}", response_model=dict)
def get_sponsor_slot(slot_id: int, db: Session = Depends(get_db)):
    """Get a single sponsor slot by ID."""
    slot = db.query(SponsorSlot).filter(SponsorSlot.id == slot_id).first()

    if not slot:
        raise HTTPException(status_code=404, detail=f"Sponsor slot {slot_id} not found")

    return slot.to_dict(include_sponsor=True)


@router.post("/slots/", response_model=dict, status_code=201)
def create_sponsor_slot(
    slot_data: SponsorSlotCreate,
    db: Session = Depends(get_db)
    # TODO: Add auth dependency: current_user = Depends(require_platform_admin)
):
    """
    Create a new sponsor slot.

    Requires platform_admin role.
    """
    # Validate object_type
    valid_types = ['settlement', 'route', 'topic']
    if slot_data.object_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid object_type. Must be one of: {valid_types}")

    # Validate position
    valid_positions = ['primary', 'secondary']
    if slot_data.position and slot_data.position not in valid_positions:
        raise HTTPException(status_code=400, detail=f"Invalid position. Must be one of: {valid_positions}")

    # Check sponsor exists
    sponsor = db.query(Sponsor).filter(Sponsor.id == slot_data.sponsor_id).first()
    if not sponsor:
        raise HTTPException(status_code=404, detail=f"Sponsor {slot_data.sponsor_id} not found")

    slot = SponsorSlot(
        sponsor_id=slot_data.sponsor_id,
        object_type=slot_data.object_type,
        object_id=slot_data.object_id,
        position=slot_data.position or 'primary',
        start_date=slot_data.start_date,
        end_date=slot_data.end_date
    )

    db.add(slot)
    db.commit()
    db.refresh(slot)

    return slot.to_dict(include_sponsor=True)


@router.put("/slots/{slot_id}", response_model=dict)
def update_sponsor_slot(
    slot_id: int,
    slot_data: SponsorSlotUpdate,
    db: Session = Depends(get_db)
    # TODO: Add auth dependency: current_user = Depends(require_platform_admin)
):
    """
    Update a sponsor slot.

    Requires platform_admin role.
    """
    slot = db.query(SponsorSlot).filter(SponsorSlot.id == slot_id).first()

    if not slot:
        raise HTTPException(status_code=404, detail=f"Sponsor slot {slot_id} not found")

    # Validate position if provided
    if slot_data.position is not None:
        valid_positions = ['primary', 'secondary']
        if slot_data.position not in valid_positions:
            raise HTTPException(status_code=400, detail=f"Invalid position. Must be one of: {valid_positions}")
        slot.position = slot_data.position

    if slot_data.start_date is not None:
        slot.start_date = slot_data.start_date
    if slot_data.end_date is not None:
        slot.end_date = slot_data.end_date
    if slot_data.is_active is not None:
        slot.is_active = slot_data.is_active

    db.commit()
    db.refresh(slot)

    return slot.to_dict(include_sponsor=True)


@router.delete("/slots/{slot_id}", status_code=204)
def delete_sponsor_slot(
    slot_id: int,
    db: Session = Depends(get_db)
    # TODO: Add auth dependency: current_user = Depends(require_platform_admin)
):
    """
    Delete a sponsor slot.

    Requires platform_admin role.
    """
    slot = db.query(SponsorSlot).filter(SponsorSlot.id == slot_id).first()

    if not slot:
        raise HTTPException(status_code=404, detail=f"Sponsor slot {slot_id} not found")

    db.delete(slot)
    db.commit()

    return None


# ============================================================================
# Click Tracking Endpoint
# ============================================================================

@router.get("/click/{slot_id}")
def track_sponsor_click(slot_id: int, db: Session = Depends(get_db)):
    """
    Track a sponsor click and redirect to sponsor website.

    This endpoint:
    1. Increments the click_count on the sponsor slot
    2. Redirects (302) to the sponsor's website_url
    """
    slot = db.query(SponsorSlot).filter(SponsorSlot.id == slot_id).first()

    if not slot:
        raise HTTPException(status_code=404, detail=f"Sponsor slot {slot_id} not found")

    # Get the sponsor
    sponsor = slot.sponsor
    if not sponsor or not sponsor.website_url:
        raise HTTPException(status_code=404, detail="Sponsor website not configured")

    # Increment click count
    slot.increment_clicks()
    db.commit()

    # Redirect to sponsor website
    return RedirectResponse(url=sponsor.website_url, status_code=302)


@router.post("/slots/{slot_id}/impression")
def track_sponsor_impression(slot_id: int, db: Session = Depends(get_db)):
    """
    Track a sponsor impression.

    Called when a page with this sponsor slot is viewed.
    """
    slot = db.query(SponsorSlot).filter(SponsorSlot.id == slot_id).first()

    if not slot:
        raise HTTPException(status_code=404, detail=f"Sponsor slot {slot_id} not found")

    slot.increment_impressions()
    db.commit()

    return {"success": True, "impression_count": slot.impression_count}
