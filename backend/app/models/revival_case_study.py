"""
RevivalCaseStudy model - Real-world examples of successful village revivals for RAG context
"""
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ARRAY
from sqlalchemy.sql import func
from app.database import Base


class RevivalCaseStudy(Base):
    __tablename__ = "revival_case_studies"

    id = Column(Integer, primary_key=True, index=True)

    # Village info
    village_name = Column(String(255), nullable=False)
    country = Column(String(100), nullable=False, index=True)
    region = Column(String(255))
    population_before = Column(Integer)
    population_after = Column(Integer)
    population_band = Column(String(50), index=True)  # 'under_100', '100_500', '500_1000', '1000_5000'

    # Revival details
    revival_type = Column(String(100), index=True)  # 'eco_village', 'artisan_hub', 'heritage_tourism', 'remote_work', 'agriculture'
    strategy = Column(Text, nullable=False)  # Main approach they took
    key_projects = Column(ARRAY(Text))  # Array of main projects
    outcomes = Column(Text, nullable=False)  # What happened
    lessons_learned = Column(Text)  # Key takeaways
    timeline_years = Column(Integer)  # How long the transformation took

    # Tags for matching
    themes = Column(ARRAY(Text))  # 'heritage', 'ecology', 'artisan', 'agriculture', etc.
    geography_tags = Column(ARRAY(Text))  # 'ponds', 'mountains', 'forest', 'coast', etc.
    funding_sources = Column(ARRAY(Text))  # What grants they used

    # Sources
    sources = Column(ARRAY(Text))  # URLs or references

    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Valid population bands
    POPULATION_BANDS = ['under_100', '100_500', '500_1000', '1000_5000', '5000_plus']

    # Valid revival types
    REVIVAL_TYPES = ['eco_village', 'artisan_hub', 'heritage_tourism', 'remote_work', 'agriculture', 'wine_tourism', 'cultural']

    def __repr__(self):
        return f"<RevivalCaseStudy(id={self.id}, village='{self.village_name}', type='{self.revival_type}')>"

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "village_name": self.village_name,
            "country": self.country,
            "region": self.region,
            "population_before": self.population_before,
            "population_after": self.population_after,
            "population_band": self.population_band,
            "revival_type": self.revival_type,
            "strategy": self.strategy,
            "key_projects": self.key_projects or [],
            "outcomes": self.outcomes,
            "lessons_learned": self.lessons_learned,
            "timeline_years": self.timeline_years,
            "themes": self.themes or [],
            "geography_tags": self.geography_tags or [],
            "funding_sources": self.funding_sources or [],
            "sources": self.sources or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def to_rag_context(self):
        """Format for inclusion in AI prompts."""
        projects_str = ", ".join(self.key_projects) if self.key_projects else "N/A"
        funding_str = ", ".join(self.funding_sources) if self.funding_sources else "N/A"

        return f"""{self.village_name} ({self.region}, {self.country})
Population: {self.population_before or '?'} → {self.population_after or '?'}
Strategy: {self.strategy}
Key Projects: {projects_str}
Outcomes: {self.outcomes}
Timeline: {self.timeline_years or '?'} years
Funding: {funding_str}
Lessons: {self.lessons_learned or 'N/A'}"""
