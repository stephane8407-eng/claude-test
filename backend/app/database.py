"""
Database configuration and session management for SPV Treasure Map.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://spv_admin:password@localhost:5432/spv_treasure_map"
)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10,        # Connection pool size
    max_overflow=20      # Max connections beyond pool_size
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency for FastAPI routes to get database session.

    Usage:
        @app.get("/api/battles")
        def get_battles(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database - create all tables.
    Call this after defining all models.
    """
    import app.models  # noqa: F401 - Import to register models
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")


def check_postgis():
    """
    Verify PostGIS extension is enabled.
    """
    from sqlalchemy import text

    with engine.connect() as conn:
        result = conn.execute(text("SELECT PostGIS_version();"))
        version = result.fetchone()[0]
        print(f"✅ PostGIS version: {version}")
        return version
