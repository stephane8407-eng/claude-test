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
            "conflict_trauma_score": float(self.conflict_trauma_score) if self.conflict_trauma_score is not None else None,
            "resilience_score": float(self.resilience_score) if self.resilience_score is not None else None,
            "heritage_richness_score": float(self.heritage_richness_score) if self.heritage_richness_score is not None else None,
            "tourism_potential_score": float(self.tourism_potential_score) if self.tourism_potential_score is not None else None
        }
