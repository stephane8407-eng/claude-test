"""
FundingProgram model - Grants and funding opportunities for village projects

Updated for Phase E Week 2: Includes columns matching database schema.
"""
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ARRAY, Boolean, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class FundingProgram(Base):
    __tablename__ = "funding_programs"

    id = Column(Integer, primary_key=True, index=True)

    # Basic info
    name = Column(String(255), nullable=False)
    organization = Column(String(255), nullable=False)  # 'Commission Européenne', 'Ministère', 'Région', etc.
    country = Column(String(100), nullable=False, index=True)
    level = Column(String(50), index=True)  # 'European', 'National', 'Regional', 'Departmental', 'Intercommunal'
    program_type = Column(String(100))  # Type of program

    # Eligibility
    eligible_themes = Column(ARRAY(Text))  # 'heritage', 'ecology', 'tourism', etc.
    eligible_countries = Column(ARRAY(Text), default=['FR'])  # Countries eligible
    eligible_population_max = Column(Integer)  # NULL if no limit (legacy)
    eligible_population_bands = Column(ARRAY(Text))  # ['<2000', '2000-5000', '5000-10000', etc.]
    eligible_regions = Column(ARRAY(Text))  # ['Nouvelle-Aquitaine', 'All regions', etc.]

    # Funding details
    funding_type = Column(String(50))  # 'grant', 'loan', 'subsidy', 'tax_credit'
    amount_min = Column(Integer)
    amount_max = Column(Integer)
    funding_percentage_min = Column(Integer)  # e.g., 20 for "from 20%"
    funding_percentage_max = Column(Integer)  # e.g., 80 for "up to 80%"

    # Description and requirements
    description = Column(Text)  # Full program description
    requirements = Column(Text)  # Eligibility requirements
    required_documents = Column(ARRAY(Text))  # Documents needed for application (array)

    # Application info
    website_url = Column(String(500))  # Official program website
    application_url = Column(Text)  # Direct application link
    deadline_type = Column(String(50))  # 'rolling', 'annual', 'quarterly', 'one_time', 'permanent'
    deadline_date = Column(Date)  # Specific deadline if applicable
    next_deadline = Column(TIMESTAMP)  # Next deadline timestamp

    # Process guidance (legacy fields)
    process_summary = Column(Text)  # Step-by-step overview
    typical_timeline_months = Column(Integer)  # How long to get approval
    tips = Column(Text)  # Best practices from successful applications

    # Sources and status
    sources = Column(ARRAY(Text))
    is_active = Column(Boolean, default=True, index=True)

    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    grant_applications = relationship("GrantApplication", back_populates="funding_program")

    # Valid funding types
    FUNDING_TYPES = ['grant', 'loan', 'subsidy', 'tax_credit', 'guarantee']

    # Valid deadline types
    DEADLINE_TYPES = ['rolling', 'annual', 'quarterly', 'one_time']

    def __repr__(self):
        return f"<FundingProgram(id={self.id}, name='{self.name}', organization='{self.organization}')>"

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "name": self.name,
            "organization": self.organization,
            "country": self.country,
            "level": self.level,
            "program_type": self.program_type,
            "eligible_themes": self.eligible_themes or [],
            "eligible_countries": self.eligible_countries or ['FR'],
            "eligible_population_max": self.eligible_population_max,
            "eligible_population_bands": self.eligible_population_bands or [],
            "eligible_regions": self.eligible_regions or [],
            "funding_type": self.funding_type,
            "amount_min": self.amount_min,
            "amount_max": self.amount_max,
            "funding_percentage_min": self.funding_percentage_min,
            "funding_percentage_max": self.funding_percentage_max,
            "description": self.description,
            "requirements": self.requirements,
            "required_documents": self.required_documents or [],
            "website_url": self.website_url,
            "application_url": self.application_url,
            "deadline_type": self.deadline_type,
            "deadline_date": self.deadline_date.isoformat() if self.deadline_date else None,
            "next_deadline": self.next_deadline.isoformat() if self.next_deadline else None,
            "process_summary": self.process_summary,
            "typical_timeline_months": self.typical_timeline_months,
            "tips": self.tips,
            "sources": self.sources or [],
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def to_rag_context(self):
        """Format for inclusion in AI prompts."""
        themes_str = ", ".join(self.eligible_themes) if self.eligible_themes else "All"
        amount_str = f"€{self.amount_min:,}-{self.amount_max:,}" if self.amount_min and self.amount_max else "Varies"
        percentage_str = f"up to {self.funding_percentage_max}%" if self.funding_percentage_max else "N/A"

        return f"""{self.name} ({self.organization})
Eligible themes: {themes_str}
Amount: {amount_str} ({percentage_str})
Deadline: {self.deadline_type}
Timeline: {self.typical_timeline_months or '?'} months
Process: {self.process_summary or 'N/A'}
Tips: {self.tips or 'N/A'}"""

    def get_funding_range_display(self):
        """Get human-readable funding range."""
        if self.amount_min and self.amount_max:
            return f"€{self.amount_min:,} - €{self.amount_max:,}"
        elif self.amount_max:
            return f"Up to €{self.amount_max:,}"
        elif self.amount_min:
            return f"From €{self.amount_min:,}"
        return "Variable"
