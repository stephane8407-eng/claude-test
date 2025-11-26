"""
QR Code API endpoints for tourism tracking and monetization
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, timedelta
import hashlib
import secrets
from user_agents import parse

from app.database import get_db
from app.models.qr_code import QRCode
from app.models.qr_scan import QRScan
from app.models.qr_route import QRRoute
from app.models.village import Village
from app.models.poi import POI
from app.services.qr_generator import get_qr_generator, QRCodeSize
from app.services.auth import get_current_user
from app.models.user import User
from app.services.logger import get_logger
from pydantic import BaseModel, Field

logger = get_logger(__name__)
router = APIRouter()


# Pydantic schemas
class QRCodeCreate(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    target_url: str
    poi_id: Optional[int] = None
    battle_id: Optional[int] = None


class QRCodeResponse(BaseModel):
    id: int
    village_id: int
    code: str
    name: str
    description: Optional[str]
    target_url: str
    qr_image_url: Optional[str]
    scan_count: int
    last_scanned_at: Optional[datetime]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class QRCodeStats(BaseModel):
    total_scans: int
    unique_visitors: int
    scans_by_device: dict
    scans_by_hour: dict
    recent_scans: List[dict]


# Tier limits
TIER_QR_LIMITS = {
    'free': 0,
    'lite': 5,
    'partner': 999999  # Unlimited
}


def check_qr_limit(village: Village, db: Session):
    """Check if village can create more QR codes"""
    limit = TIER_QR_LIMITS.get(village.subscription_tier, 0)
    current_count = db.query(func.count(QRCode.id)).filter(
        QRCode.village_id == village.id
    ).scalar()

    if current_count >= limit:
        raise HTTPException(
            status_code=403,
            detail=f"QR code limit reached for {village.subscription_tier} tier ({limit} max). Upgrade to create more."
        )


@router.post("/villages/{village_slug}/qr-codes", response_model=QRCodeResponse)
def create_qr_code(
    village_slug: str,
    qr_data: QRCodeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new QR code for a village"""
    # Get village
    village = db.query(Village).filter(Village.slug == village_slug).first()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    # Check ownership/permission (simplified - should check roles)
    # For now, just check tier limit
    check_qr_limit(village, db)

    # Generate unique code
    code = f"spv-{village_slug}-{secrets.token_urlsafe(6)}"

    # Create QR code record
    qr_code = QRCode(
        village_id=village.id,
        poi_id=qr_data.poi_id,
        battle_id=qr_data.battle_id,
        code=code,
        name=qr_data.name,
        description=qr_data.description,
        target_url=qr_data.target_url,
        scan_count=0,
        is_active=True
    )

    db.add(qr_code)
    db.commit()
    db.refresh(qr_code)

    # Generate QR code images
    try:
        generator = get_qr_generator()
        # Full URL for scanning
        scan_url = f"https://spvtreasurehunt.com/api/qr/{code}"

        paths = generator.generate_and_save_qr_code(
            data=scan_url,
            qr_code=code,
            village_slug=village_slug,
            village_settings=village.settings
        )

        # Save medium size path to database
        qr_code.qr_image_url = paths.get(QRCodeSize.MEDIUM)
        db.commit()
        db.refresh(qr_code)

        logger.info(f"Created QR code {code} for village {village_slug}")

    except Exception as e:
        logger.error(f"Failed to generate QR images: {e}")
        # Don't fail the request, image can be regenerated

    return qr_code


@router.get("/villages/{village_slug}/qr-codes", response_model=List[QRCodeResponse])
def list_qr_codes(
    village_slug: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all QR codes for a village"""
    village = db.query(Village).filter(Village.slug == village_slug).first()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    qr_codes = db.query(QRCode).filter(
        QRCode.village_id == village.id
    ).offset(skip).limit(limit).all()

    return qr_codes


@router.get("/villages/{village_slug}/qr-codes/{qr_id}", response_model=QRCodeResponse)
def get_qr_code(
    village_slug: str,
    qr_id: int,
    db: Session = Depends(get_db)
):
    """Get QR code details"""
    village = db.query(Village).filter(Village.slug == village_slug).first()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    qr_code = db.query(QRCode).filter(
        and_(QRCode.id == qr_id, QRCode.village_id == village.id)
    ).first()

    if not qr_code:
        raise HTTPException(status_code=404, detail="QR code not found")

    return qr_code


@router.delete("/villages/{village_slug}/qr-codes/{qr_id}")
def delete_qr_code(
    village_slug: str,
    qr_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a QR code"""
    village = db.query(Village).filter(Village.slug == village_slug).first()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    qr_code = db.query(QRCode).filter(
        and_(QRCode.id == qr_id, QRCode.village_id == village.id)
    ).first()

    if not qr_code:
        raise HTTPException(status_code=404, detail="QR code not found")

    db.delete(qr_code)
    db.commit()

    return {"message": "QR code deleted"}


@router.get("/qr/{code}")
async def scan_qr_code(
    code: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Public scan endpoint - tracks scan and redirects to target URL
    This is the endpoint encoded in the QR code image
    """
    # Get QR code
    qr_code = db.query(QRCode).filter(QRCode.code == code).first()

    if not qr_code or not qr_code.is_active:
        raise HTTPException(status_code=404, detail="QR code not found or inactive")

    # Parse user agent
    ua_string = request.headers.get('user-agent', '')
    user_agent = parse(ua_string)

    # Determine device type
    if user_agent.is_mobile:
        device_type = 'mobile'
    elif user_agent.is_tablet:
        device_type = 'tablet'
    elif user_agent.is_bot:
        device_type = 'bot'
    else:
        device_type = 'desktop'

    # Hash IP address for privacy (GDPR compliant)
    client_ip = request.client.host if request.client else 'unknown'
    ip_hash = hashlib.sha256(client_ip.encode()).hexdigest()

    # Generate session ID (could use cookies for better tracking)
    session_id = hashlib.sha256(f"{ip_hash}{ua_string}".encode()).hexdigest()

    # Create scan record
    scan = QRScan(
        qr_code_id=qr_code.id,
        scanned_at=datetime.utcnow(),
        user_agent=ua_string[:500],  # Limit length
        device_type=device_type,
        browser=user_agent.browser.family if user_agent.browser else None,
        os=user_agent.os.family if user_agent.os else None,
        ip_address_hash=ip_hash,
        session_id=session_id,
        referrer=request.headers.get('referer')
    )

    db.add(scan)

    # Update QR code scan count
    qr_code.scan_count += 1
    qr_code.last_scanned_at = datetime.utcnow()

    db.commit()

    logger.info(f"QR code scanned: {code} from {device_type}")

    # Redirect to target URL
    return RedirectResponse(url=qr_code.target_url, status_code=302)


@router.get("/villages/{village_slug}/qr-codes/{qr_id}/stats", response_model=QRCodeStats)
def get_qr_stats(
    village_slug: str,
    qr_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get analytics for a QR code"""
    village = db.query(Village).filter(Village.slug == village_slug).first()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    qr_code = db.query(QRCode).filter(
        and_(QRCode.id == qr_id, QRCode.village_id == village.id)
    ).first()

    if not qr_code:
        raise HTTPException(status_code=404, detail="QR code not found")

    # Date range
    since = datetime.utcnow() - timedelta(days=days)

    # Total scans in period
    total_scans = db.query(func.count(QRScan.id)).filter(
        and_(QRScan.qr_code_id == qr_id, QRScan.scanned_at >= since)
    ).scalar()

    # Unique visitors
    unique_visitors = db.query(func.count(func.distinct(QRScan.session_id))).filter(
        and_(QRScan.qr_code_id == qr_id, QRScan.scanned_at >= since)
    ).scalar()

    # Scans by device
    device_stats = db.query(
        QRScan.device_type,
        func.count(QRScan.id).label('count')
    ).filter(
        and_(QRScan.qr_code_id == qr_id, QRScan.scanned_at >= since)
    ).group_by(QRScan.device_type).all()

    scans_by_device = {device: count for device, count in device_stats if device}

    # Scans by hour of day
    hour_stats = db.query(
        func.extract('hour', QRScan.scanned_at).label('hour'),
        func.count(QRScan.id).label('count')
    ).filter(
        and_(QRScan.qr_code_id == qr_id, QRScan.scanned_at >= since)
    ).group_by('hour').all()

    scans_by_hour = {int(hour): count for hour, count in hour_stats}

    # Recent scans (last 10)
    recent = db.query(QRScan).filter(
        QRScan.qr_code_id == qr_id
    ).order_by(QRScan.scanned_at.desc()).limit(10).all()

    recent_scans = [
        {
            'scanned_at': scan.scanned_at.isoformat(),
            'device_type': scan.device_type,
            'browser': scan.browser,
            'os': scan.os
        }
        for scan in recent
    ]

    return QRCodeStats(
        total_scans=total_scans or 0,
        unique_visitors=unique_visitors or 0,
        scans_by_device=scans_by_device,
        scans_by_hour=scans_by_hour,
        recent_scans=recent_scans
    )
