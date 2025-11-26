# 🎯 WEEK 3: IDENTITY ENGINE INFRASTRUCTURE - HANDOFF FOR CLAUDE CODE

**Status**: Ready to build  
**Previous Week**: ✅ Week 2 complete (19 POIs, perfect village isolation)  
**This Week Goal**: Build the data layer for AI-powered village identity analysis  
**Time Estimate**: 6-8 hours

---

## 📋 WHAT WE'RE BUILDING

**Big Picture:**
The Identity Engine is your **competitive advantage**. Anyone can map historical conflicts, but SPV's "Impact Today" framework connects past events to present-day village characteristics across 6 categories:

1. 🏗️ **Infrastructure** - How wars shaped roads, walls, bridges
2. 💰 **Economy** - How conflicts affected trade, agriculture, industry  
3. 🎭 **Identity** - How history created festivals, traditions, symbols
4. 👥 **Demographics** - How wars affected population, migration
5. 🏛️ **Governance** - How conflicts shaped political structures
6. 🎪 **Tourism** - How history can be monetized today

**Week 3 Goal:**
Build the **data collection layer** so we can analyze villages and generate identity themes.

---

## 🗄️ DATABASE SCHEMA (Priority 1)

### Table 1: `identity_categories` (The 6 Impact Categories)

```sql
CREATE TABLE identity_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE, -- "infrastructure", "economy", "identity", "demographics", "governance", "tourism"
    name_fr VARCHAR(50), -- French: "infrastructure", "économie", "identité", "démographie", "gouvernance", "tourisme"
    icon VARCHAR(50), -- Icon identifier: "building", "coins", "flag", "users", "landmark", "map"
    color VARCHAR(7), -- Hex color: "#3B82F6"
    description TEXT,
    example_themes TEXT, -- Examples: "Phoenix Village (infrastructure), Sleeping Waters (economy)"
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insert the 6 core categories
INSERT INTO identity_categories (name, name_fr, icon, color, description, example_themes) VALUES
('infrastructure', 'Infrastructure', 'building', '#3B82F6', 'How wars shaped roads, walls, bridges, and built environment', 'Phoenix Village (rebuilt after destruction)'),
('economy', 'Économie', 'coins', '#10B981', 'How conflicts affected trade, agriculture, industry, and wealth', 'Sleeping Waters (economic decline after wars)'),
('identity', 'Identité', 'flag', '#8B5CF6', 'How history created festivals, traditions, symbols, and collective memory', 'Villages Brûlés (burned village identity)'),
('demographics', 'Démographie', 'users', '#F59E0B', 'How wars affected population, migration, family structures', 'Migration Hub (refugees settled here)'),
('governance', 'Gouvernance', 'landmark', '#EF4444', 'How conflicts shaped political structures, administration, laws', 'Border Village (governance changed with borders)'),
('tourism', 'Tourisme', 'map', '#06B6D4', 'How history can be monetized through heritage tourism today', 'Heritage Trail (tourist circuit opportunity)');

CREATE INDEX idx_identity_categories_name ON identity_categories(name);
```

---

### Table 2: `identity_themes` (Village-Specific Identity Stories)

```sql
CREATE TABLE identity_themes (
    id SERIAL PRIMARY KEY,
    village_id INTEGER NOT NULL REFERENCES villages(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES identity_categories(id),
    
    -- Core Identity
    theme_name VARCHAR(100) NOT NULL, -- "Phoenix Village", "Sleeping Waters", etc.
    theme_name_fr VARCHAR(100),
    tagline VARCHAR(200), -- One-sentence summary
    tagline_fr VARCHAR(200),
    
    -- AI-Generated Content
    story_markdown TEXT NOT NULL, -- Full identity story (markdown format)
    impact_summary TEXT, -- 2-3 sentence summary of modern impact
    
    -- Evidence & Sources
    evidence_conflicts INTEGER[], -- Array of conflict IDs supporting this theme
    evidence_pois INTEGER[], -- Array of POI IDs supporting this theme
    evidence_data JSONB, -- Supporting data: {"population_decline": "45% since 1900", "wars_experienced": 7}
    
    -- Actionable Projects (Tourism Monetization)
    project_ideas JSONB, -- Array of projects: [{"title": "QR Route", "budget": "€2000", "roi": "€8000/year"}]
    
    -- Metadata
    confidence_score DECIMAL(3,2), -- 0.00-1.00 (how strong is the evidence?)
    is_featured BOOLEAN DEFAULT FALSE, -- Show on village homepage
    display_order INTEGER DEFAULT 0, -- Sort order on village page
    
    -- AI Generation Tracking
    ai_model VARCHAR(50), -- "claude-sonnet-4-20250514"
    ai_prompt_version VARCHAR(20), -- "v1.2" (for tracking prompt improvements)
    generated_at TIMESTAMP DEFAULT NOW(),
    reviewed_by_human BOOLEAN DEFAULT FALSE,
    human_edits_made BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(village_id, category_id, theme_name) -- One theme per category per village
);

CREATE INDEX idx_identity_themes_village ON identity_themes(village_id);
CREATE INDEX idx_identity_themes_category ON identity_themes(category_id);
CREATE INDEX idx_identity_themes_featured ON identity_themes(is_featured);
CREATE INDEX idx_identity_themes_conflicts ON identity_themes USING gin(evidence_conflicts);
CREATE INDEX idx_identity_themes_pois ON identity_themes USING gin(evidence_pois);

COMMENT ON TABLE identity_themes IS 'AI-generated village identity stories based on historical analysis';
COMMENT ON COLUMN identity_themes.evidence_conflicts IS 'Array of conflict IDs that support this identity theme';
COMMENT ON COLUMN identity_themes.confidence_score IS 'How strongly does evidence support this theme? 0.0 = weak, 1.0 = very strong';
```

---

### Table 3: `village_data_snapshots` (Cached Village Data for AI Analysis)

```sql
CREATE TABLE village_data_snapshots (
    id SERIAL PRIMARY KEY,
    village_id INTEGER NOT NULL REFERENCES villages(id) ON DELETE CASCADE,
    
    -- Data Collection Timestamp
    snapshot_date TIMESTAMP DEFAULT NOW(),
    data_version VARCHAR(20) DEFAULT 'v1.0', -- Track schema versions
    
    -- Conflict Summary (Pre-computed for AI)
    total_conflicts INTEGER DEFAULT 0,
    conflicts_by_period JSONB, -- {"Medieval": 25, "WW1": 3, "WW2": 5}
    conflicts_by_type JSONB, -- {"siege": 12, "battle": 8, "raid": 5}
    most_destructive_conflicts JSONB, -- Top 5 worst conflicts with details
    conflict_density_score DECIMAL(5,2), -- Conflicts per 100 years
    
    -- POI Summary
    total_pois INTEGER DEFAULT 0,
    pois_by_type JSONB, -- {"church": 3, "château": 1, "pond": 15}
    heritage_buildings INTEGER DEFAULT 0, -- Count of historical buildings
    
    -- Demographics (Future: INSEE API)
    current_population INTEGER,
    population_peak INTEGER,
    population_peak_year INTEGER,
    population_decline_pct DECIMAL(5,2), -- Percentage decline from peak
    
    -- Economy (Future: INSEE API)
    primary_industry VARCHAR(100), -- "Agriculture", "Tourism", "Manufacturing"
    unemployment_rate DECIMAL(5,2),
    median_income INTEGER,
    
    -- Geographic Context
    distance_to_major_city INTEGER, -- km to nearest city >50k population
    border_proximity BOOLEAN DEFAULT FALSE, -- Within 20km of national border?
    strategic_location TEXT, -- "Trade route", "River crossing", "Mountain pass"
    
    -- Computed Scores (For AI Prompts)
    conflict_trauma_score DECIMAL(3,2), -- 0.00-1.00 (how traumatic was history?)
    resilience_score DECIMAL(3,2), -- 0.00-1.00 (how well did village recover?)
    heritage_richness_score DECIMAL(3,2), -- 0.00-1.00 (how much heritage to monetize?)
    tourism_potential_score DECIMAL(3,2), -- 0.00-1.00 (tourism opportunity?)
    
    -- AI Usage Tracking
    used_for_identity_generation BOOLEAN DEFAULT FALSE,
    identity_generation_timestamp TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_village_data_snapshots_village ON village_data_snapshots(village_id);
CREATE INDEX idx_village_data_snapshots_date ON village_data_snapshots(snapshot_date DESC);

COMMENT ON TABLE village_data_snapshots IS 'Pre-computed village data for efficient AI identity generation';
COMMENT ON COLUMN village_data_snapshots.conflict_density_score IS 'Number of conflicts per 100 years of village history';
COMMENT ON COLUMN village_data_snapshots.conflict_trauma_score IS 'How traumatic was the village history? Used in AI prompts';
```

---

## 🐍 BACKEND CODE (Priority 2)

### Step 1: Create SQLAlchemy Models

**File:** `backend/app/models/identity_category.py`

```python
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class IdentityCategory(Base):
    __tablename__ = "identity_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    name_fr = Column(String(50))
    icon = Column(String(50))
    color = Column(String(7))
    description = Column(Text)
    example_themes = Column(Text)
    created_at = Column(TIMESTAMP, default=func.now())
    
    # Relationships
    identity_themes = relationship("IdentityTheme", back_populates="category")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "name_fr": self.name_fr,
            "icon": self.icon,
            "color": self.color,
            "description": self.description,
            "example_themes": self.example_themes
        }
```

**File:** `backend/app/models/identity_theme.py`

```python
from sqlalchemy import Column, Integer, String, Text, DECIMAL, Boolean, TIMESTAMP, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class IdentityTheme(Base):
    __tablename__ = "identity_themes"
    
    id = Column(Integer, primary_key=True, index=True)
    village_id = Column(Integer, ForeignKey("villages.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("identity_categories.id"), nullable=False)
    
    # Core identity
    theme_name = Column(String(100), nullable=False)
    theme_name_fr = Column(String(100))
    tagline = Column(String(200))
    tagline_fr = Column(String(200))
    
    # AI-generated content
    story_markdown = Column(Text, nullable=False)
    impact_summary = Column(Text)
    
    # Evidence
    evidence_conflicts = Column(ARRAY(Integer))
    evidence_pois = Column(ARRAY(Integer))
    evidence_data = Column(JSONB)
    
    # Projects
    project_ideas = Column(JSONB)
    
    # Metadata
    confidence_score = Column(DECIMAL(3, 2))
    is_featured = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)
    
    # AI tracking
    ai_model = Column(String(50))
    ai_prompt_version = Column(String(20))
    generated_at = Column(TIMESTAMP, default=func.now())
    reviewed_by_human = Column(Boolean, default=False)
    human_edits_made = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())
    
    # Relationships
    village = relationship("Village", back_populates="identity_themes")
    category = relationship("IdentityCategory", back_populates="identity_themes")
    
    def to_dict(self):
        return {
            "id": self.id,
            "village_id": self.village_id,
            "village_slug": self.village.slug if self.village else None,
            "category": self.category.to_dict() if self.category else None,
            "theme_name": self.theme_name,
            "theme_name_fr": self.theme_name_fr,
            "tagline": self.tagline,
            "tagline_fr": self.tagline_fr,
            "story_markdown": self.story_markdown,
            "impact_summary": self.impact_summary,
            "evidence_conflicts": self.evidence_conflicts or [],
            "evidence_pois": self.evidence_pois or [],
            "evidence_data": self.evidence_data or {},
            "project_ideas": self.project_ideas or [],
            "confidence_score": float(self.confidence_score) if self.confidence_score else None,
            "is_featured": self.is_featured,
            "display_order": self.display_order,
            "ai_model": self.ai_model,
            "ai_prompt_version": self.ai_prompt_version,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
            "reviewed_by_human": self.reviewed_by_human,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
```

**File:** `backend/app/models/village_data_snapshot.py`

```python
from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class VillageDataSnapshot(Base):
    __tablename__ = "village_data_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    village_id = Column(Integer, ForeignKey("villages.id"), nullable=False)
    
    # Metadata
    snapshot_date = Column(TIMESTAMP, default=func.now())
    data_version = Column(String(20), default='v1.0')
    
    # Conflict data
    total_conflicts = Column(Integer, default=0)
    conflicts_by_period = Column(JSONB)
    conflicts_by_type = Column(JSONB)
    most_destructive_conflicts = Column(JSONB)
    conflict_density_score = Column(DECIMAL(5, 2))
    
    # POI data
    total_pois = Column(Integer, default=0)
    pois_by_type = Column(JSONB)
    heritage_buildings = Column(Integer, default=0)
    
    # Demographics
    current_population = Column(Integer)
    population_peak = Column(Integer)
    population_peak_year = Column(Integer)
    population_decline_pct = Column(DECIMAL(5, 2))
    
    # Economy
    primary_industry = Column(String(100))
    unemployment_rate = Column(DECIMAL(5, 2))
    median_income = Column(Integer)
    
    # Geography
    distance_to_major_city = Column(Integer)
    border_proximity = Column(Boolean, default=False)
    strategic_location = Column(String(200))
    
    # Computed scores
    conflict_trauma_score = Column(DECIMAL(3, 2))
    resilience_score = Column(DECIMAL(3, 2))
    heritage_richness_score = Column(DECIMAL(3, 2))
    tourism_potential_score = Column(DECIMAL(3, 2))
    
    # AI tracking
    used_for_identity_generation = Column(Boolean, default=False)
    identity_generation_timestamp = Column(TIMESTAMP)
    
    # Timestamps
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())
    
    # Relationships
    village = relationship("Village", back_populates="data_snapshots")
    
    def to_dict(self):
        return {
            "id": self.id,
            "village_id": self.village_id,
            "village_slug": self.village.slug if self.village else None,
            "snapshot_date": self.snapshot_date.isoformat() if self.snapshot_date else None,
            "data_version": self.data_version,
            "total_conflicts": self.total_conflicts,
            "conflicts_by_period": self.conflicts_by_period or {},
            "conflicts_by_type": self.conflicts_by_type or {},
            "most_destructive_conflicts": self.most_destructive_conflicts or [],
            "conflict_density_score": float(self.conflict_density_score) if self.conflict_density_score else None,
            "total_pois": self.total_pois,
            "pois_by_type": self.pois_by_type or {},
            "heritage_buildings": self.heritage_buildings,
            "current_population": self.current_population,
            "population_peak": self.population_peak,
            "population_peak_year": self.population_peak_year,
            "population_decline_pct": float(self.population_decline_pct) if self.population_decline_pct else None,
            "primary_industry": self.primary_industry,
            "strategic_location": self.strategic_location,
            "conflict_trauma_score": float(self.conflict_trauma_score) if self.conflict_trauma_score else None,
            "resilience_score": float(self.resilience_score) if self.resilience_score else None,
            "heritage_richness_score": float(self.heritage_richness_score) if self.heritage_richness_score else None,
            "tourism_potential_score": float(self.tourism_potential_score) if self.tourism_potential_score else None
        }
```

**Update:** `backend/app/models/__init__.py`
```python
from .village import Village
from .conflict import Conflict
from .poi import POI, POIType
from .identity_category import IdentityCategory
from .identity_theme import IdentityTheme
from .village_data_snapshot import VillageDataSnapshot

__all__ = [
    "Village", 
    "Conflict", 
    "POI", 
    "POIType",
    "IdentityCategory",
    "IdentityTheme", 
    "VillageDataSnapshot"
]
```

**Update:** `backend/app/models/village.py`
```python
# Add these lines to Village class:
identity_themes = relationship("IdentityTheme", back_populates="village")
data_snapshots = relationship("VillageDataSnapshot", back_populates="village")
```

---

### Step 2: Create API Endpoints

**File:** `backend/app/api/identity.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Village, IdentityCategory, IdentityTheme

router = APIRouter()

# =====================================
# IDENTITY CATEGORY ENDPOINTS
# =====================================

@router.get("/api/identity/categories", tags=["Identity"])
def get_identity_categories(db: Session = Depends(get_db)):
    """Get all 6 identity categories"""
    categories = db.query(IdentityCategory).all()
    return [cat.to_dict() for cat in categories]

# =====================================
# IDENTITY THEME ENDPOINTS
# =====================================

@router.get("/api/villages/{village_slug}/identity", tags=["Identity"])
def get_village_identity_themes(
    village_slug: str,
    db: Session = Depends(get_db)
):
    """Get all identity themes for a village"""
    village = db.query(Village).filter(Village.slug == village_slug).first()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")
    
    themes = db.query(IdentityTheme).filter(
        IdentityTheme.village_id == village.id
    ).order_by(IdentityTheme.display_order).all()
    
    return [theme.to_dict() for theme in themes]

@router.get("/api/villages/{village_slug}/identity/{theme_id}", tags=["Identity"])
def get_identity_theme_detail(
    village_slug: str,
    theme_id: int,
    db: Session = Depends(get_db)
):
    """Get details of a specific identity theme"""
    village = db.query(Village).filter(Village.slug == village_slug).first()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")
    
    theme = db.query(IdentityTheme).filter(
        IdentityTheme.id == theme_id,
        IdentityTheme.village_id == village.id  # Village isolation
    ).first()
    
    if not theme:
        raise HTTPException(status_code=404, detail="Identity theme not found")
    
    return theme.to_dict()

@router.get("/api/villages/{village_slug}/identity-summary", tags=["Identity"])
def get_village_identity_summary(
    village_slug: str,
    db: Session = Depends(get_db)
):
    """Get summary of village identity (featured themes only)"""
    village = db.query(Village).filter(Village.slug == village_slug).first()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")
    
    featured_themes = db.query(IdentityTheme).filter(
        IdentityTheme.village_id == village.id,
        IdentityTheme.is_featured == True
    ).order_by(IdentityTheme.display_order).all()
    
    return {
        "village": village.to_dict(),
        "featured_themes": [theme.to_dict() for theme in featured_themes],
        "total_themes": db.query(IdentityTheme).filter(
            IdentityTheme.village_id == village.id
        ).count()
    }
```

**Update:** `backend/main.py`
```python
from app.api import identity  # ADD THIS IMPORT

# Add this line after existing routers:
app.include_router(identity.router)
```

---

## 🧪 TEST DATA (Priority 3)

**File:** `backend/scripts/week3_generate_chirac_snapshot.py`

```python
#!/usr/bin/env python3
"""
Generate data snapshot for Chirac village
This computes all the stats needed for AI identity generation
Run: python backend/scripts/week3_generate_chirac_snapshot.py
"""
import sys
sys.path.insert(0, '/Users/stephanevergnaud/Documents/treasure-hunting/claude-test')

from app.database import SessionLocal
from app.models import Village, Conflict, POI, VillageDataSnapshot
from sqlalchemy import func
from collections import Counter

def generate_chirac_snapshot():
    db = SessionLocal()
    
    try:
        # Get Chirac
        chirac = db.query(Village).filter(Village.slug == "chirac").first()
        if not chirac:
            print("❌ Chirac village not found!")
            return
        
        print(f"✅ Found Chirac (ID: {chirac.id})")
        
        # Clear existing snapshots
        db.query(VillageDataSnapshot).filter(VillageDataSnapshot.village_id == chirac.id).delete()
        db.commit()
        print("🧹 Cleared existing snapshots")
        
        # ==================================
        # COMPUTE CONFLICT DATA
        # ==================================
        
        conflicts = db.query(Conflict).filter(Conflict.village_id == chirac.id).all()
        total_conflicts = len(conflicts)
        print(f"\n📊 Analyzing {total_conflicts} conflicts...")
        
        # Group by period
        conflicts_by_period = {}
        for conflict in conflicts:
            period = conflict.period or "Unknown"
            conflicts_by_period[period] = conflicts_by_period.get(period, 0) + 1
        
        # Group by type (extract from description/name)
        conflicts_by_type = {"siege": 0, "battle": 0, "raid": 0, "other": 0}
        for conflict in conflicts:
            text = (conflict.name + " " + (conflict.description or "")).lower()
            if "siege" in text or "siège" in text:
                conflicts_by_type["siege"] += 1
            elif "battle" in text or "bataille" in text:
                conflicts_by_type["battle"] += 1
            elif "raid" in text or "pillage" in text:
                conflicts_by_type["raid"] += 1
            else:
                conflicts_by_type["other"] += 1
        
        # Most destructive (sort by severity if available, else take first 5)
        most_destructive = sorted(
            conflicts,
            key=lambda c: c.severity if c.severity else 5,
            reverse=True
        )[:5]
        
        most_destructive_data = [
            {
                "id": c.id,
                "name": c.name,
                "year": c.year,
                "period": c.period,
                "severity": c.severity,
                "description": c.description[:200] if c.description else None
            }
            for c in most_destructive
        ]
        
        # Conflict density (conflicts per 100 years)
        # Chirac data spans ~2500 years (500 BC to 2000 AD)
        conflict_density = round(total_conflicts / 25, 2)  # 25 centuries
        
        print(f"   Conflicts by period: {conflicts_by_period}")
        print(f"   Conflict density: {conflict_density} per century")
        
        # ==================================
        # COMPUTE POI DATA
        # ==================================
        
        pois = db.query(POI).filter(POI.village_id == chirac.id).all()
        total_pois = len(pois)
        print(f"\n🏛️ Analyzing {total_pois} POIs...")
        
        # Group by type
        pois_by_type = {}
        heritage_count = 0
        for poi in pois:
            if poi.poi_type:
                type_name = poi.poi_type.name
                pois_by_type[type_name] = pois_by_type.get(type_name, 0) + 1
                
                # Count heritage buildings
                if poi.heritage_status:
                    heritage_count += 1
        
        print(f"   POIs by type: {pois_by_type}")
        print(f"   Heritage buildings: {heritage_count}")
        
        # ==================================
        # COMPUTE SCORES
        # ==================================
        
        # Conflict trauma score (0.0-1.0)
        # Based on: conflict density, destructive events
        trauma_score = min(1.0, conflict_density / 10)  # 10+ conflicts/century = max trauma
        
        # Resilience score (0.0-1.0)
        # Based on: still exists, has heritage, population
        resilience_score = 0.75  # Chirac survived, has POIs, still populated
        
        # Heritage richness score (0.0-1.0)
        # Based on: number of heritage POIs, diversity
        heritage_score = min(1.0, heritage_count / 10)  # 10+ heritage = max
        
        # Tourism potential score (0.0-1.0)
        # Based on: conflicts + POIs + heritage
        tourism_score = min(1.0, (total_conflicts / 100 + total_pois / 20 + heritage_count / 10) / 3)
        
        print(f"\n🎯 Computed Scores:")
        print(f"   Trauma: {trauma_score:.2f}")
        print(f"   Resilience: {resilience_score:.2f}")
        print(f"   Heritage: {heritage_score:.2f}")
        print(f"   Tourism Potential: {tourism_score:.2f}")
        
        # ==================================
        # CREATE SNAPSHOT
        # ==================================
        
        snapshot = VillageDataSnapshot(
            village_id=chirac.id,
            data_version="v1.0",
            
            # Conflict data
            total_conflicts=total_conflicts,
            conflicts_by_period=conflicts_by_period,
            conflicts_by_type=conflicts_by_type,
            most_destructive_conflicts=most_destructive_data,
            conflict_density_score=conflict_density,
            
            # POI data
            total_pois=total_pois,
            pois_by_type=pois_by_type,
            heritage_buildings=heritage_count,
            
            # Demographics (placeholder - will add INSEE data later)
            current_population=800,
            population_peak=1200,
            population_peak_year=1850,
            population_decline_pct=33.33,
            
            # Economy (placeholder)
            primary_industry="Agriculture",
            
            # Geography (Chirac context)
            distance_to_major_city=45,  # ~45km to Angoulême
            border_proximity=False,
            strategic_location="River crossing, trade route",
            
            # Computed scores
            conflict_trauma_score=trauma_score,
            resilience_score=resilience_score,
            heritage_richness_score=heritage_score,
            tourism_potential_score=tourism_score
        )
        
        db.add(snapshot)
        db.commit()
        
        print(f"\n🎉 SUCCESS! Created data snapshot for Chirac")
        print(f"   Snapshot ID: {snapshot.id}")
        print(f"   Ready for AI identity generation in Week 4!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    generate_chirac_snapshot()
```

Make executable:
```bash
chmod +x backend/scripts/week3_generate_chirac_snapshot.py
```

---

## ✅ TESTING CHECKLIST

### Database Tests
```bash
# 1. Create tables
psql -U spv_admin -d spv_treasure_map -h localhost -f backend/schema/week3_identity_schema.sql

# 2. Verify tables exist
psql -U spv_admin -d spv_treasure_map -h localhost -c "\dt identity*"
psql -U spv_admin -d spv_treasure_map -h localhost -c "\dt village_data*"

# Expected:
#   identity_categories | table
#   identity_themes     | table
#   village_data_snapshots | table

# 3. Check identity categories
psql -U spv_admin -d spv_treasure_map -h localhost -c "SELECT name, name_fr, icon FROM identity_categories;"

# Expected: 6 rows (infrastructure, economy, identity, demographics, governance, tourism)
```

### Backend Tests
```bash
# 1. Start server
cd ~/Documents/treasure-hunting/claude-test/backend
source venv/bin/activate
python main.py

# 2. Test identity categories endpoint
curl http://localhost:8000/api/identity/categories

# Expected: JSON array with 6 categories

# 3. Generate Chirac data snapshot
python scripts/week3_generate_chirac_snapshot.py

# Expected output:
#   ✅ Found Chirac (ID: 1)
#   📊 Analyzing 123 conflicts...
#   🏛️ Analyzing 19 POIs...
#   🎯 Computed Scores: (trauma, resilience, heritage, tourism)
#   🎉 SUCCESS! Created data snapshot

# 4. Verify snapshot created
curl http://localhost:8000/api/villages/chirac/data-snapshot

# Expected: JSON with conflict stats, POI stats, scores

# 5. Test identity themes endpoint (should be empty for now)
curl http://localhost:8000/api/villages/chirac/identity

# Expected: [] (no themes yet - we'll generate in Week 4)
```

---

## 🎯 SUCCESS CRITERIA

**You know Week 3 is COMPLETE when:**

✅ **Database:**
- [ ] `identity_categories` table with 6 categories
- [ ] `identity_themes` table (empty for now - Week 4 will populate)
- [ ] `village_data_snapshots` table with Chirac snapshot

✅ **Backend:**
- [ ] 3 new models (IdentityCategory, IdentityTheme, VillageDataSnapshot)
- [ ] 4 new API endpoints working
- [ ] Chirac has 1 data snapshot with computed scores

✅ **Data Quality:**
- [ ] Snapshot shows 123 conflicts analyzed
- [ ] Snapshot shows 19 POIs analyzed
- [ ] Snapshot shows 4 computed scores (trauma, resilience, heritage, tourism)
- [ ] Scores are reasonable (0.0-1.0 range)

✅ **Testing:**
- [ ] Can GET all 6 identity categories
- [ ] Can GET Chirac's data snapshot
- [ ] Can GET Chirac's identity themes (empty array for now)
- [ ] Manot has no snapshot (village isolation works)

---

## 📂 FILES TO CREATE/MODIFY

**NEW FILES:**
1. `backend/schema/week3_identity_schema.sql` (3 tables + inserts)
2. `backend/app/models/identity_category.py`
3. `backend/app/models/identity_theme.py`
4. `backend/app/models/village_data_snapshot.py`
5. `backend/app/api/identity.py` (4 endpoints)
6. `backend/scripts/week3_generate_chirac_snapshot.py`

**MODIFY FILES:**
1. `backend/app/models/__init__.py` (add 3 new imports)
2. `backend/app/models/village.py` (add 2 relationships)
3. `backend/main.py` (add identity router)

---

## ⏱️ TIME BREAKDOWN

| Task | Estimated Time |
|------|----------------|
| Create database schema (3 tables) | 1 hour |
| Create SQLAlchemy models (3 models) | 1.5 hours |
| Create API endpoints (4 endpoints) | 1 hour |
| Create snapshot generation script | 1.5 hours |
| Test all endpoints | 1 hour |
| Fix bugs | 30 mins |
| **TOTAL** | **6-8 hours** |

---

## 🚀 WHAT'S NEXT? (Week 4 Preview)

**Week 4: AI Identity Generation**
- Write prompt templates for Claude API
- Generate 2-3 identity themes for Chirac (Phoenix Village, Sleeping Waters, etc.)
- Test AI generation quality
- Build village hub page to display themes
- Add human review workflow

**Week 3 prepares the data layer, Week 4 adds the AI magic!** ✨

---

## 🎯 COMPLETION CHECKLIST

When done, verify:
- [ ] All 9 files created/modified
- [ ] 3 database tables exist with correct schemas
- [ ] 6 identity categories inserted
- [ ] Chirac has 1 data snapshot
- [ ] API endpoints return correct data
- [ ] Village isolation working
- [ ] Code committed to git with message: "Week 3 Complete: Identity Engine data layer with Chirac snapshot"

**Then you're ready for Week 4 (AI generation)!** 🎉
