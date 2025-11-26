"""
Health check endpoint for monitoring system status
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import os
import sys

from app.database import get_db


router = APIRouter(tags=["Health"])


@router.get("/api/health")
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint

    Returns system status including:
    - API status
    - Database connection
    - Version information
    - Timestamp

    Returns:
        Health status information
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + 'Z',
        "version": get_version(),
        "environment": os.getenv('ENVIRONMENT', 'development'),
        "checks": {}
    }

    # Check database connection
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }

    # Check Python version
    health_status["checks"]["python"] = {
        "status": "healthy",
        "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    }

    # Overall status
    all_healthy = all(
        check.get("status") == "healthy"
        for check in health_status["checks"].values()
    )

    if not all_healthy:
        health_status["status"] = "unhealthy"

    return health_status


@router.get("/api/health/db")
def health_check_database(db: Session = Depends(get_db)):
    """
    Detailed database health check

    Returns:
        Database health information
    """
    try:
        # Check basic connection
        db.execute(text("SELECT 1"))

        # Check if we can query tables
        result = db.execute(text("SELECT COUNT(*) FROM villages"))
        village_count = result.scalar()

        return {
            "status": "healthy",
            "message": "Database connection successful",
            "details": {
                "villages_count": village_count
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database health check failed: {str(e)}"
        )


@router.get("/api/health/ready")
def readiness_check(db: Session = Depends(get_db)):
    """
    Readiness check for Kubernetes/orchestration

    Returns:
        Ready status
    """
    try:
        # Check database
        db.execute(text("SELECT 1"))

        return {
            "ready": True,
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service not ready: {str(e)}"
        )


@router.get("/api/health/live")
def liveness_check():
    """
    Liveness check for Kubernetes/orchestration

    Returns:
        Alive status (always returns 200 if process is running)
    """
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat() + 'Z'
    }


def get_version() -> str:
    """
    Get application version

    Returns:
        Version string
    """
    # Try to read version from file or environment
    version = os.getenv('APP_VERSION', 'dev')

    # Could also read from VERSION file or package metadata
    version_file = os.path.join(
        os.path.dirname(__file__),
        '..',
        '..',
        'VERSION'
    )

    if os.path.exists(version_file):
        try:
            with open(version_file, 'r') as f:
                version = f.read().strip()
        except Exception:
            pass

    return version
