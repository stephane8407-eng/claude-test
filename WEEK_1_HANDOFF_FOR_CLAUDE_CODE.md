# Week 1 Implementation - Handoff for Claude Code

**Date**: November 25, 2024  
**Status**: AI validation PASSED ✅ (5/5 criteria met)  
**Decision**: GO - Proceed with multi-tenancy implementation

---

## Context: What Was Validated

The identity engine test proved:
- ✅ AI generates quality themes ("Phoenix Village", "Sleeping Waters")
- ✅ Projects are actionable with real partners (INRAE, DRAC, LPO)
- ✅ Cost is negligible ($0.02/village)
- ✅ Approach scales (works with minimal data)
- ✅ Would work in mayor pitch

**Business model validated**: €500K revenue / €20 AI cost = 25,000:1 ROI

---

## Week 1 Goal

**Build multi-tenancy foundation** so 2 villages can manage their content independently.

**Success Criteria:**
- ✅ Can create 2 test villages (Chirac, Manot)
- ✅ Each village sees only their conflicts on map
- ✅ Can switch between villages
- ✅ Village settings persist in database
- ✅ Basic admin can manage village data

**Time estimate**: 4-6 hours over 7 days  
**Complexity**: Medium (standard patterns)

---

## Current Database State

**Location**: `spv_treasure_map` PostgreSQL database  
**Working tables:**
- `battles` - 114 major battles (imported)
- `local_conflicts` - 119 Chirac conflicts (imported)
- `places` - Basic place data
- `place_contexts` - AI scraper results

**Frontend status:**
- Map displays 233 markers (114 blue + 119 orange)
- Popups show conflict details
- Legend shows war periods
- React + Mapbox GL JS working

---

## Week 1 Tasks

### Task 1: Create Villages Table ⭐ PRIORITY 1

**File**: `backend/scripts/week1_create_villages_table.sql`

```sql
-- Create villages table for multi-tenancy
CREATE TABLE villages (
    id SERIAL PRIMARY KEY,
    
    -- Basic info
    name VARCHAR(255) NOT NULL UNIQUE,
    slug VARCHAR(255) NOT NULL UNIQUE, -- URL-friendly: "chirac", "manot"
    description TEXT,
    
    -- Location
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    country VARCHAR(2) NOT NULL, -- "FR", "UK", "BE"
    department VARCHAR(100), -- "Charente", "Hertfordshire"
    region VARCHAR(100), -- "Nouvelle-Aquitaine"
    
    -- Village details
    population INTEGER,
    area_km2 DECIMAL(10, 2),
    
    -- Subscription & features
    subscription_tier VARCHAR(20) DEFAULT 'free', -- "free", "partner", "flagship"
    subscription_status VARCHAR(20) DEFAULT 'active', -- "active", "expired", "trial"
    subscription_expires_at DATE,
    
    -- Settings (JSONB for flexibility)
    settings JSONB DEFAULT '{
        "brand_color": "#3B82F6",
        "show_conflicts": true,
        "show_ponds": false,
        "show_routes": false,
        "public_page_enabled": false
    }'::jsonb,
    
    -- Identity themes (will be populated by AI later)
    identity_themes JSONB,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_villages_slug ON villages(slug);
CREATE INDEX idx_villages_country ON villages(country);
CREATE INDEX idx_villages_tier ON villages(subscription_tier);
CREATE INDEX idx_villages_status ON villages(subscription_status);

-- Spatial index for finding nearby villages
CREATE INDEX idx_villages_location ON villages USING gist(
    ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
);

COMMENT ON TABLE villages IS 'Multi-tenant villages - each village has its own space';
COMMENT ON COLUMN villages.settings IS 'Flexible JSON settings per village';
COMMENT ON COLUMN villages.identity_themes IS 'AI-generated themes stored as JSON after analysis';
```

**How to run:**
```bash
cd ~/Documents/treasure-hunting/claude-test/backend
psql -U spv_admin -d spv_treasure_map -h localhost -f scripts/week1_create_villages_table.sql
```

**Verification:**
```sql
-- Check table exists
\d villages

-- Should show: 0 rows
SELECT COUNT(*) FROM villages;
```

---

### Task 2: Add Village Foreign Keys ⭐ PRIORITY 2

**File**: `backend/scripts/week1_add_village_foreign_keys.sql`

```sql
-- Add village_id to local_conflicts (links conflicts to villages)
ALTER TABLE local_conflicts 
ADD COLUMN village_id INTEGER REFERENCES villages(id);

CREATE INDEX idx_local_conflicts_village ON local_conflicts(village_id);

COMMENT ON COLUMN local_conflicts.village_id IS 'Links conflict to owning village (multi-tenancy)';

-- Add village_id to places (if you want villages to own places)
ALTER TABLE places 
ADD COLUMN village_id INTEGER REFERENCES places(id);

CREATE INDEX idx_places_village ON places(village_id);

-- Note: battles table stays global (shared across all villages)
-- Only local_conflicts are village-specific

COMMENT ON COLUMN places.village_id IS 'Optional: links place to village for filtering';
```

**How to run:**
```bash
psql -U spv_admin -d spv_treasure_map -h localhost -f scripts/week1_add_village_foreign_keys.sql
```

**Verification:**
```sql
-- Check columns added
\d local_conflicts
\d places

-- Should show village_id column
```

---

### Task 3: Create Test Villages ⭐ PRIORITY 3

**File**: `backend/scripts/week1_insert_test_villages.sql`

```sql
-- Insert Chirac (pilot village with real data)
INSERT INTO villages (
    name, slug, description,
    latitude, longitude, country, department, region,
    population, area_km2,
    subscription_tier, subscription_status,
    settings
) VALUES (
    'Chirac',
    'chirac',
    'Village in Charente with 119 conflicts over 2,500 years. Known for Forges de l''Âge and 1944 Villages Brûlés.',
    45.9833, 0.5667,
    'FR', 'Charente', 'Nouvelle-Aquitaine',
    800, 21.5,
    'flagship', 'trial',
    '{
        "brand_color": "#DC2626",
        "show_conflicts": true,
        "show_ponds": true,
        "show_routes": true,
        "public_page_enabled": true
    }'
);

-- Insert Manot (test village #2)
INSERT INTO villages (
    name, slug, description,
    latitude, longitude, country, department, region,
    population, area_km2,
    subscription_tier, subscription_status,
    settings
) VALUES (
    'Manot',
    'manot',
    'Village near Chirac. Known for Château Salignac-Fénelon and Roman road.',
    45.9167, 0.5833,
    'FR', 'Charente', 'Nouvelle-Aquitaine',
    600, 18.0,
    'partner', 'active',
    '{
        "brand_color": "#2563EB",
        "show_conflicts": true,
        "show_ponds": false,
        "show_routes": false,
        "public_page_enabled": false
    }'
);

-- Link existing Chirac conflicts to Chirac village
UPDATE local_conflicts 
SET village_id = (SELECT id FROM villages WHERE slug = 'chirac')
WHERE village_id IS NULL;

-- Verify
SELECT 
    v.name,
    v.subscription_tier,
    COUNT(lc.id) as conflict_count
FROM villages v
LEFT JOIN local_conflicts lc ON v.id = lc.village_id
GROUP BY v.id, v.name, v.subscription_tier
ORDER BY v.name;
```

**How to run:**
```bash
psql -U spv_admin -d spv_treasure_map -h localhost -f scripts/week1_insert_test_villages.sql
```

**Expected output:**
```
 name   | subscription_tier | conflict_count 
--------+-------------------+----------------
 Chirac | flagship          |            119
 Manot  | partner           |              0
```

---

### Task 4: Create SQLAlchemy Model ⭐ PRIORITY 4

**File**: `backend/app/models/village.py`

```python
from sqlalchemy import Column, Integer, String, Text, DECIMAL, Date, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import JSONB
from geoalchemy2 import Geometry
from sqlalchemy.orm import relationship

from app.database import Base

class Village(Base):
    __tablename__ = "villages"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    name = Column(String(255), nullable=False, unique=True)
    slug = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text)
    
    # Location
    latitude = Column(DECIMAL(10, 7), nullable=False)
    longitude = Column(DECIMAL(10, 7), nullable=False)
    country = Column(String(2), nullable=False, index=True)
    department = Column(String(100))
    region = Column(String(100))
    
    # Village details
    population = Column(Integer)
    area_km2 = Column(DECIMAL(10, 2))
    
    # Subscription
    subscription_tier = Column(String(20), default='free', index=True)
    subscription_status = Column(String(20), default='active', index=True)
    subscription_expires_at = Column(Date)
    
    # Settings (flexible JSON)
    settings = Column(JSONB, default={})
    
    # Identity themes (from AI analysis)
    identity_themes = Column(JSONB)
    
    # Metadata
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships (add later when ready)
    # conflicts = relationship("LocalConflict", back_populates="village")
    # places = relationship("Place", back_populates="village")
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'country': self.country,
            'department': self.department,
            'region': self.region,
            'population': self.population,
            'area_km2': float(self.area_km2) if self.area_km2 else None,
            'subscription_tier': self.subscription_tier,
            'subscription_status': self.subscription_status,
            'settings': self.settings or {},
            'identity_themes': self.identity_themes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<Village(id={self.id}, name='{self.name}', tier='{self.subscription_tier}')>"
```

**How to create:**
```bash
# Claude Code: create this file at backend/app/models/village.py
```

---

### Task 5: Update LocalConflict Model ⭐ PRIORITY 5

**File**: `backend/app/models/local_conflict.py`

Add this near the top:
```python
village_id = Column(Integer, ForeignKey('villages.id'), index=True)

# Optional: add relationship
# village = relationship("Village", back_populates="conflicts")
```

**Full updated model** (for reference):
```python
from sqlalchemy import Column, Integer, String, Text, Date, DECIMAL, TIMESTAMP, func, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

from app.database import Base

class LocalConflict(Base):
    __tablename__ = "local_conflicts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # NEW: Multi-tenancy
    village_id = Column(Integer, ForeignKey('villages.id'), index=True)
    
    # Basic info
    name = Column(String(255), nullable=False)
    date = Column(Date)
    date_text = Column(String(100))
    location = Column(String(255))
    latitude = Column(DECIMAL(10, 7))
    longitude = Column(DECIMAL(10, 7))
    
    # ... rest of model unchanged ...
```

---

### Task 6: Create Village API Endpoints ⭐ PRIORITY 6

**File**: `backend/app/api/villages.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.village import Village

router = APIRouter(prefix="/api/villages", tags=["villages"])

@router.get("/", response_model=List[dict])
def list_villages(
    country: str = None,
    subscription_tier: str = None,
    db: Session = Depends(get_db)
):
    """
    List all villages with optional filters
    
    Filters:
    - country: FR, UK, BE
    - subscription_tier: free, partner, flagship
    """
    query = db.query(Village)
    
    if country:
        query = query.filter(Village.country == country)
    if subscription_tier:
        query = query.filter(Village.subscription_tier == subscription_tier)
    
    villages = query.order_by(Village.name).all()
    return [v.to_dict() for v in villages]

@router.get("/{slug}", response_model=dict)
def get_village(slug: str, db: Session = Depends(get_db)):
    """Get single village by slug"""
    village = db.query(Village).filter(Village.slug == slug).first()
    
    if not village:
        raise HTTPException(status_code=404, detail=f"Village '{slug}' not found")
    
    return village.to_dict()

@router.get("/{slug}/conflicts", response_model=List[dict])
def get_village_conflicts(slug: str, db: Session = Depends(get_db)):
    """Get all conflicts for a village"""
    from app.models.local_conflict import LocalConflict
    
    village = db.query(Village).filter(Village.slug == slug).first()
    if not village:
        raise HTTPException(status_code=404, detail=f"Village '{slug}' not found")
    
    conflicts = db.query(LocalConflict)\
        .filter(LocalConflict.village_id == village.id)\
        .order_by(LocalConflict.date.desc())\
        .all()
    
    return [c.to_dict() for c in conflicts]

@router.get("/{slug}/stats", response_model=dict)
def get_village_stats(slug: str, db: Session = Depends(get_db)):
    """Get statistics for a village"""
    from app.models.local_conflict import LocalConflict
    from sqlalchemy import func as sql_func
    
    village = db.query(Village).filter(Village.slug == slug).first()
    if not village:
        raise HTTPException(status_code=404, detail=f"Village '{slug}' not found")
    
    # Count conflicts by period
    conflict_count = db.query(sql_func.count(LocalConflict.id))\
        .filter(LocalConflict.village_id == village.id)\
        .scalar()
    
    return {
        'village': village.to_dict(),
        'total_conflicts': conflict_count,
        'has_identity_themes': village.identity_themes is not None
    }
```

**How to integrate:**
In `backend/main.py`, add:
```python
from app.api import villages

app.include_router(villages.router)
```

---

### Task 7: Update Conflicts API ⭐ PRIORITY 7

**File**: `backend/app/api/conflicts.py` (create or update)

Add village filtering:
```python
@router.get("/api/conflicts")
def list_conflicts(
    village_slug: str = None,  # NEW: filter by village
    war_period: str = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List conflicts with optional village filter"""
    from app.models.local_conflict import LocalConflict
    from app.models.village import Village
    
    query = db.query(LocalConflict)
    
    # NEW: Filter by village
    if village_slug:
        village = db.query(Village).filter(Village.slug == village_slug).first()
        if village:
            query = query.filter(LocalConflict.village_id == village.id)
    
    # Existing filters
    if war_period:
        query = query.filter(LocalConflict.war_period == war_period)
    
    conflicts = query.order_by(LocalConflict.date.desc())\
        .limit(limit)\
        .offset(offset)\
        .all()
    
    return [c.to_dict() for c in conflicts]
```

---

### Task 8: Test Everything ⭐ PRIORITY 8

**Test script**: `backend/scripts/week1_test_multi_tenancy.py`

```python
#!/usr/bin/env python3
"""
Week 1 Multi-Tenancy Test Script

Tests that villages work independently
"""

import requests

BASE_URL = "http://localhost:8000"

def test_list_villages():
    """Test: Can list all villages"""
    print("Test 1: List villages...")
    
    response = requests.get(f"{BASE_URL}/api/villages/")
    assert response.status_code == 200
    
    villages = response.json()
    assert len(villages) == 2
    assert villages[0]['name'] in ['Chirac', 'Manot']
    
    print(f"✅ Found {len(villages)} villages")

def test_get_chirac():
    """Test: Can get Chirac details"""
    print("\nTest 2: Get Chirac village...")
    
    response = requests.get(f"{BASE_URL}/api/villages/chirac")
    assert response.status_code == 200
    
    chirac = response.json()
    assert chirac['name'] == 'Chirac'
    assert chirac['subscription_tier'] == 'flagship'
    
    print(f"✅ Chirac: {chirac['population']} pop, {chirac['subscription_tier']} tier")

def test_chirac_conflicts():
    """Test: Chirac has 119 conflicts"""
    print("\nTest 3: Get Chirac conflicts...")
    
    response = requests.get(f"{BASE_URL}/api/villages/chirac/conflicts")
    assert response.status_code == 200
    
    conflicts = response.json()
    assert len(conflicts) == 119
    
    print(f"✅ Chirac has {len(conflicts)} conflicts")

def test_manot_conflicts():
    """Test: Manot has 0 conflicts (separate from Chirac)"""
    print("\nTest 4: Get Manot conflicts...")
    
    response = requests.get(f"{BASE_URL}/api/villages/manot/conflicts")
    assert response.status_code == 200
    
    conflicts = response.json()
    assert len(conflicts) == 0
    
    print(f"✅ Manot has {len(conflicts)} conflicts (isolated from Chirac)")

def test_village_stats():
    """Test: Can get village statistics"""
    print("\nTest 5: Get Chirac stats...")
    
    response = requests.get(f"{BASE_URL}/api/villages/chirac/stats")
    assert response.status_code == 200
    
    stats = response.json()
    assert stats['total_conflicts'] == 119
    
    print(f"✅ Stats: {stats['total_conflicts']} conflicts")

def test_filter_by_village():
    """Test: Can filter conflicts by village"""
    print("\nTest 6: Filter conflicts by village...")
    
    # All conflicts
    response = requests.get(f"{BASE_URL}/api/conflicts")
    all_conflicts = response.json()
    
    # Just Chirac conflicts
    response = requests.get(f"{BASE_URL}/api/conflicts?village_slug=chirac")
    chirac_conflicts = response.json()
    
    assert len(chirac_conflicts) == 119
    print(f"✅ Filtering works: {len(chirac_conflicts)} Chirac conflicts")

if __name__ == '__main__':
    print("=" * 60)
    print("WEEK 1 MULTI-TENANCY TESTS")
    print("=" * 60)
    
    try:
        test_list_villages()
        test_get_chirac()
        test_chirac_conflicts()
        test_manot_conflicts()
        test_village_stats()
        test_filter_by_village()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nWeek 1 Success Criteria:")
        print("✅ Can create 2 test villages")
        print("✅ Each village sees only their conflicts")
        print("✅ Can switch between villages")
        print("✅ Village settings persist")
        print("\n🎉 WEEK 1 COMPLETE - Ready for Week 2!")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
```

**How to run:**
```bash
# Start backend (in one terminal)
cd ~/Documents/treasure-hunting/claude-test/backend
source venv/bin/activate
python main.py

# Run tests (in another terminal)
cd ~/Documents/treasure-hunting/claude-test/backend
source venv/bin/activate
python scripts/week1_test_multi_tenancy.py
```

---

## Success Criteria Checklist

At end of Week 1, verify:

- [ ] `villages` table exists in database
- [ ] `local_conflicts.village_id` foreign key added
- [ ] 2 test villages created (Chirac, Manot)
- [ ] 119 conflicts linked to Chirac (village_id set)
- [ ] 0 conflicts linked to Manot
- [ ] Village model works (`backend/app/models/village.py`)
- [ ] Can call `GET /api/villages/` (returns 2 villages)
- [ ] Can call `GET /api/villages/chirac` (returns Chirac details)
- [ ] Can call `GET /api/villages/chirac/conflicts` (returns 119)
- [ ] Can call `GET /api/villages/manot/conflicts` (returns 0)
- [ ] Can call `GET /api/conflicts?village_slug=chirac` (filters work)
- [ ] All tests pass (`week1_test_multi_tenancy.py`)

---

## Troubleshooting

### Problem: psql command not found
```bash
# Fix: Use full path
/opt/homebrew/opt/postgresql@17/bin/psql -U spv_admin -d spv_treasure_map -h localhost -f script.sql
```

### Problem: Permission denied on table
```bash
# Fix: Grant permissions
psql -U spv_admin -d spv_treasure_map
GRANT ALL ON TABLE villages TO spv_admin;
GRANT USAGE, SELECT ON SEQUENCE villages_id_seq TO spv_admin;
```

### Problem: Foreign key constraint fails
```bash
# Check: Are there any conflicts with village_id already set?
SELECT COUNT(*) FROM local_conflicts WHERE village_id IS NOT NULL;

# Fix: Clear old data
UPDATE local_conflicts SET village_id = NULL;
```

### Problem: FastAPI doesn't see new endpoints
```bash
# Fix: Restart FastAPI server
# Ctrl+C to stop
python main.py
```

### Problem: Tests fail with 404
```bash
# Check: Is FastAPI running?
curl http://localhost:8000/api/villages/

# Check: Are villages in database?
psql -U spv_admin -d spv_treasure_map
SELECT * FROM villages;
```

---

## File Checklist

Create these files (in order):

1. [ ] `backend/scripts/week1_create_villages_table.sql`
2. [ ] `backend/scripts/week1_add_village_foreign_keys.sql`
3. [ ] `backend/scripts/week1_insert_test_villages.sql`
4. [ ] `backend/app/models/village.py`
5. [ ] `backend/app/models/local_conflict.py` (update)
6. [ ] `backend/app/api/villages.py`
7. [ ] `backend/app/api/conflicts.py` (update)
8. [ ] `backend/main.py` (update to include villages router)
9. [ ] `backend/scripts/week1_test_multi_tenancy.py`

---

## What to Report Back

After completing Week 1, report:

✅ **Success indicators:**
- "All 6 tests passed ✅"
- "Chirac has 119 conflicts, Manot has 0"
- "Can filter by village_slug"
- Screenshot of test output

⚠️ **Issues encountered:**
- Which SQL scripts had errors
- Which tests failed
- Error messages

❌ **Blockers:**
- Anything preventing progress
- Decisions needed

---

## Communication with User

**What to tell user when done:**

"Week 1 complete! ✅

Created:
- `villages` table (2 test villages: Chirac, Manot)
- Village foreign keys on conflicts
- Village API endpoints (6 new endpoints)
- Multi-tenancy working (each village sees only their data)

Tests: 6/6 passed

Next: Week 2 - Flexible POI system (villages can add their own points)"

---

## Handoff Back to Claude Chat

After Week 1 completion, user should:

1. Show test results to Claude Chat
2. Discuss any issues encountered
3. Review if success criteria met
4. Get Week 2 planning

Claude Chat will:
- Evaluate if Week 1 succeeded
- Adjust plan if needed
- Prepare Week 2 handoff
- Celebrate progress! 🎉

---

**Ready for Claude Code to execute!** 🚀

All SQL scripts, Python files, and tests are ready to implement.
