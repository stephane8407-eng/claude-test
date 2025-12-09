"""
Media Upload API - Image upload endpoint for hero images
"""
import os
import uuid
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from PIL import Image

from app.database import get_db


router = APIRouter(prefix="/api/upload", tags=["upload"])

# Configuration
UPLOAD_DIR = Path("uploads")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_IMAGE_WIDTH = 1920
THUMBNAIL_WIDTH = 400


def ensure_upload_dirs():
    """Create upload directories if they don't exist."""
    for subdir in ["heroes", "logos", "gpx", "temp"]:
        (UPLOAD_DIR / subdir).mkdir(parents=True, exist_ok=True)


def validate_image(file: UploadFile) -> None:
    """Validate uploaded image file."""
    # Check extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Check content type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")


def generate_unique_filename(original_filename: str, prefix: str = "") -> str:
    """Generate unique filename preserving extension."""
    ext = Path(original_filename).suffix.lower()
    unique_id = uuid.uuid4().hex[:12]
    timestamp = datetime.now().strftime("%Y%m%d")
    return f"{prefix}{timestamp}_{unique_id}{ext}"


def process_image(input_path: Path, output_path: Path, max_width: int = MAX_IMAGE_WIDTH) -> dict:
    """
    Process image: resize, strip EXIF, optimize.
    Returns image metadata.
    """
    with Image.open(input_path) as img:
        # Get original dimensions
        original_width, original_height = img.size

        # Convert to RGB if necessary (handles RGBA, P mode, etc.)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Resize if too wide
        if original_width > max_width:
            ratio = max_width / original_width
            new_height = int(original_height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

        # Save without EXIF data
        img.save(output_path, quality=85, optimize=True)

        return {
            "width": img.width,
            "height": img.height,
            "original_width": original_width,
            "original_height": original_height,
            "resized": original_width > max_width
        }


def create_thumbnail(input_path: Path, output_path: Path, width: int = THUMBNAIL_WIDTH) -> None:
    """Create thumbnail version of image."""
    with Image.open(input_path) as img:
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Calculate height maintaining aspect ratio
        ratio = width / img.width
        height = int(img.height * ratio)

        img_thumb = img.resize((width, height), Image.Resampling.LANCZOS)
        img_thumb.save(output_path, quality=80, optimize=True)


# ============================================================================
# Upload Endpoints
# ============================================================================

@router.post("/", response_model=dict)
async def upload_image(
    file: UploadFile = File(...),
    category: str = Form("heroes"),  # heroes, logos, general
    entity_type: Optional[str] = Form(None),  # village, poi, route, topic, sponsor
    entity_id: Optional[str] = Form(None),  # Optional entity identifier
    db: Session = Depends(get_db)
    # TODO: Add auth dependency
):
    """
    Upload an image file.

    - Validates file type (jpg, png, webp, max 5MB)
    - Resizes to max 1920px width
    - Strips EXIF metadata
    - Creates thumbnail
    - Returns URL to uploaded file

    **Parameters:**
    - **file**: Image file to upload
    - **category**: Type of image (heroes, logos, general)
    - **entity_type**: Optional - what entity this image belongs to
    - **entity_id**: Optional - ID or slug of the entity
    """
    ensure_upload_dirs()

    # Validate file
    validate_image(file)

    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )

    # Validate category
    valid_categories = ["heroes", "logos", "general"]
    if category not in valid_categories:
        category = "general"

    # Generate unique filename
    prefix = f"{entity_type}_{entity_id}_" if entity_type and entity_id else ""
    filename = generate_unique_filename(file.filename, prefix)

    # Create paths
    category_dir = UPLOAD_DIR / category
    category_dir.mkdir(parents=True, exist_ok=True)

    temp_path = UPLOAD_DIR / "temp" / filename
    final_path = category_dir / filename
    thumb_path = category_dir / f"thumb_{filename}"

    try:
        # Save to temp location
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process image
        metadata = process_image(temp_path, final_path)

        # Create thumbnail
        create_thumbnail(final_path, thumb_path)

        # Clean up temp file
        temp_path.unlink(missing_ok=True)

        # Generate URLs
        base_url = f"/uploads/{category}/{filename}"
        thumb_url = f"/uploads/{category}/thumb_{filename}"

        return {
            "success": True,
            "url": base_url,
            "thumbnail_url": thumb_url,
            "filename": filename,
            "category": category,
            "metadata": metadata,
            "size_bytes": final_path.stat().st_size
        }

    except Exception as e:
        # Clean up on error
        temp_path.unlink(missing_ok=True)
        final_path.unlink(missing_ok=True)
        thumb_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Failed to process image: {str(e)}")


@router.post("/gpx", response_model=dict)
async def upload_gpx(
    file: UploadFile = File(...),
    route_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
    # TODO: Add auth dependency
):
    """
    Upload a GPX file for a route.

    - Validates file extension (.gpx)
    - Returns URL to uploaded file
    """
    ensure_upload_dirs()

    # Validate extension
    ext = Path(file.filename).suffix.lower()
    if ext != ".gpx":
        raise HTTPException(status_code=400, detail="File must be a .gpx file")

    # Validate content type
    if file.content_type not in ["application/gpx+xml", "application/xml", "text/xml"]:
        # Some systems don't set correct content type for GPX
        pass  # Allow it anyway if extension is correct

    # Generate unique filename
    prefix = f"route_{route_id}_" if route_id else ""
    unique_id = uuid.uuid4().hex[:12]
    timestamp = datetime.now().strftime("%Y%m%d")
    filename = f"{prefix}{timestamp}_{unique_id}.gpx"

    # Save file
    gpx_dir = UPLOAD_DIR / "gpx"
    file_path = gpx_dir / filename

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "success": True,
            "url": f"/uploads/gpx/{filename}",
            "filename": filename,
            "size_bytes": file_path.stat().st_size
        }

    except Exception as e:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Failed to save GPX file: {str(e)}")


@router.delete("/{category}/{filename}")
async def delete_upload(
    category: str,
    filename: str,
    db: Session = Depends(get_db)
    # TODO: Add auth dependency
):
    """
    Delete an uploaded file.

    Also deletes thumbnail if it exists.
    """
    file_path = UPLOAD_DIR / category / filename
    thumb_path = UPLOAD_DIR / category / f"thumb_{filename}"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    try:
        file_path.unlink()
        thumb_path.unlink(missing_ok=True)

        return {"success": True, "deleted": filename}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")


# ============================================================================
# Serve Uploads (for development - use nginx in production)
# ============================================================================

@router.get("/{category}/{filename}")
async def serve_upload(category: str, filename: str):
    """
    Serve uploaded file.

    Note: In production, serve static files via nginx for better performance.
    """
    file_path = UPLOAD_DIR / category / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path)
