"""
Topics API - CRUD endpoints for SEO landing pages
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models.topic import Topic
from app.models.village import Village


router = APIRouter(prefix="/api/topics", tags=["topics"])


# ============================================================================
# Pydantic Schemas
# ============================================================================

class TopicCreate(BaseModel):
    slug: str
    title: str
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    hero_image_url: Optional[str] = None
    tags: Optional[List[str]] = None


class TopicUpdate(BaseModel):
    title: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    hero_image_url: Optional[str] = None
    tags: Optional[List[str]] = None


# ============================================================================
# Public Endpoints
# ============================================================================

@router.get("/", response_model=List[dict])
def list_topics(
    tag: Optional[str] = Query(None, description="Filter by tag"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List all topics with optional filters.

    - **tag**: Filter topics that contain this tag
    - **search**: Search in title and short_description
    """
    query = db.query(Topic)

    if tag:
        query = query.filter(Topic.tags.contains([tag]))

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Topic.title.ilike(search_term),
                Topic.short_description.ilike(search_term)
            )
        )

    total = query.count()
    topics = query.order_by(Topic.title).offset(offset).limit(limit).all()

    return {
        "results": [t.to_dict() for t in topics],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/{slug}", response_model=dict)
def get_topic(slug: str, db: Session = Depends(get_db)):
    """Get a single topic by slug."""
    topic = db.query(Topic).filter(Topic.slug == slug).first()

    if not topic:
        raise HTTPException(status_code=404, detail=f"Topic '{slug}' not found")

    return topic.to_dict()


@router.get("/{slug}/villages", response_model=dict)
def get_topic_villages(
    slug: str,
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get villages that match this topic's tags.

    Returns villages that have any overlapping themes with the topic's tags.
    """
    topic = db.query(Topic).filter(Topic.slug == slug).first()

    if not topic:
        raise HTTPException(status_code=404, detail=f"Topic '{slug}' not found")

    if not topic.tags:
        return {"results": [], "total": 0, "topic": topic.to_dict()}

    # Find villages with matching themes
    # Note: This requires the themes field to be added to villages table
    # For now, return empty until village themes are implemented
    query = db.query(Village)

    # When Village.themes is available:
    # query = query.filter(Village.themes.overlap(topic.tags))

    total = query.count()
    villages = query.offset(offset).limit(limit).all()

    return {
        "results": [v.to_dict() for v in villages],
        "total": total,
        "topic": topic.to_dict()
    }


# ============================================================================
# Admin Endpoints (Platform Admin Only)
# ============================================================================

@router.post("/", response_model=dict, status_code=201)
def create_topic(
    topic_data: TopicCreate,
    db: Session = Depends(get_db)
    # TODO: Add auth dependency: current_user = Depends(require_platform_admin)
):
    """
    Create a new topic.

    Requires platform_admin role.
    """
    # Check for duplicate slug
    existing = db.query(Topic).filter(Topic.slug == topic_data.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Topic with slug '{topic_data.slug}' already exists")

    topic = Topic(
        slug=topic_data.slug,
        title=topic_data.title,
        short_description=topic_data.short_description,
        long_description=topic_data.long_description,
        hero_image_url=topic_data.hero_image_url,
        tags=topic_data.tags
    )

    db.add(topic)
    db.commit()
    db.refresh(topic)

    return topic.to_dict()


@router.put("/{slug}", response_model=dict)
def update_topic(
    slug: str,
    topic_data: TopicUpdate,
    db: Session = Depends(get_db)
    # TODO: Add auth dependency: current_user = Depends(require_platform_admin)
):
    """
    Update a topic.

    Requires platform_admin role.
    """
    topic = db.query(Topic).filter(Topic.slug == slug).first()

    if not topic:
        raise HTTPException(status_code=404, detail=f"Topic '{slug}' not found")

    # Update fields if provided
    if topic_data.title is not None:
        topic.title = topic_data.title
    if topic_data.short_description is not None:
        topic.short_description = topic_data.short_description
    if topic_data.long_description is not None:
        topic.long_description = topic_data.long_description
    if topic_data.hero_image_url is not None:
        topic.hero_image_url = topic_data.hero_image_url
    if topic_data.tags is not None:
        topic.tags = topic_data.tags

    db.commit()
    db.refresh(topic)

    return topic.to_dict()


@router.delete("/{slug}", status_code=204)
def delete_topic(
    slug: str,
    db: Session = Depends(get_db)
    # TODO: Add auth dependency: current_user = Depends(require_platform_admin)
):
    """
    Delete a topic.

    Requires platform_admin role.
    """
    topic = db.query(Topic).filter(Topic.slug == slug).first()

    if not topic:
        raise HTTPException(status_code=404, detail=f"Topic '{slug}' not found")

    db.delete(topic)
    db.commit()

    return None
