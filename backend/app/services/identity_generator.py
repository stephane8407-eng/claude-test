"""
AI Identity Theme Generator using Claude API

Generates compelling village identity themes based on historical data,
conflicts, POIs, and computed scores from village data snapshots.
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime
from anthropic import Anthropic
from sqlalchemy.orm import Session

from app.models import (
    Village,
    VillageDataSnapshot,
    IdentityCategory,
    IdentityTheme,
    LocalConflict,
    POI,
    POIType
)


class IdentityGenerator:
    """Claude-powered identity theme generator for villages"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the identity generator with Claude API

        Args:
            api_key: Anthropic API key (defaults to env var ANTHROPIC_API_KEY)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-5-20250929"
        self.prompt_version = "v1.0"

    def build_context_prompt(
        self,
        db: Session,
        village: Village,
        snapshot: VillageDataSnapshot,
        category: IdentityCategory
    ) -> str:
        """
        Build rich context prompt from village data

        Args:
            db: Database session
            village: Village object
            snapshot: VillageDataSnapshot with computed scores
            category: IdentityCategory to generate theme for

        Returns:
            Formatted prompt string with all relevant context
        """
        # Get conflicts and POIs for evidence
        conflicts = db.query(LocalConflict).filter(
            LocalConflict.village_id == village.id
        ).limit(10).all()

        # Query POIs with their types
        poi_query = db.query(POI, POIType).join(
            POIType, POI.poi_type_id == POIType.id
        ).filter(
            POI.village_id == village.id
        ).limit(20).all()

        # Build conflict summary
        conflict_summary = ""
        if conflicts:
            conflict_summary = "\n".join([
                f"- {c.name} ({c.period or 'unknown period'}): {(c.strategic_importance or c.consequences or 'No details')[:100]}..."
                for c in conflicts[:5]
            ])

        # Build POI summary
        poi_summary = ""
        if poi_query:
            poi_summary = "\n".join([
                f"- {poi.name} ({poi_type.name}): {poi.description[:100] if poi.description else 'No description'}"
                for poi, poi_type in poi_query[:10]
            ])

        prompt = f"""You are an expert in rural French village identity and storytelling. You help villages discover compelling narratives from their historical data.

VILLAGE: {village.name}
CATEGORY: {category.name} - {category.description}

DATA SNAPSHOT:
- Total conflicts recorded: {snapshot.total_conflicts}
- Total points of interest: {snapshot.total_pois}
- Conflict trauma score: {snapshot.conflict_trauma_score}/1.0
- Resilience score: {snapshot.resilience_score}/1.0
- Heritage richness score: {snapshot.heritage_richness_score}/1.0
- Tourism potential score: {snapshot.tourism_potential_score}/1.0

SAMPLE CONFLICTS:
{conflict_summary or "No conflicts recorded"}

SAMPLE POINTS OF INTEREST:
{poi_summary or "No POIs recorded"}

ADDITIONAL CONTEXT:
- Primary industry: {snapshot.primary_industry or "Unknown"}
- Strategic location: {snapshot.strategic_location or "Not specified"}
- Conflicts by period: {json.dumps(snapshot.conflicts_by_period or {})}
- POIs by type: {json.dumps(snapshot.pois_by_type or {})}

Generate ONE compelling identity theme for this village in the "{category.name}" category.

Requirements:
1. Theme should be authentic and evidence-based
2. Use specific conflicts/POIs as evidence
3. Be inspiring yet realistic
4. Focus on actionable opportunities
5. Generate 2-3 concrete project ideas

Return ONLY a valid JSON object with this exact structure:
{{
    "theme_name": "Short, memorable theme name (3-5 words)",
    "tagline": "Compelling one-line tagline (max 200 chars)",
    "story_markdown": "Rich narrative story in markdown format (300-500 words). Use ## for sections. Tell a compelling story about this village's identity.",
    "impact_summary": "Brief summary of potential impact (100-150 words)",
    "evidence_conflict_ids": [],  // Leave empty - we will populate this automatically
    "evidence_poi_ids": [],  // Leave empty - we will populate this automatically
    "project_ideas": [
        {{
            "title": "Project title",
            "description": "What this project would accomplish",
            "difficulty": "easy|medium|hard",
            "estimated_impact": "low|medium|high"
        }}
    ],
    "confidence_score": 0.0-1.0 (how confident are you in this theme based on available data)
}}

Focus on the "{category.name}" category. Be creative but grounded in the data.
"""
        return prompt

    def generate_theme(
        self,
        db: Session,
        village: Village,
        category: IdentityCategory,
        snapshot: Optional[VillageDataSnapshot] = None
    ) -> Dict:
        """
        Generate a single identity theme using Claude

        Args:
            db: Database session
            village: Village to generate theme for
            category: Identity category for the theme
            snapshot: Data snapshot (will fetch latest if not provided)

        Returns:
            Dictionary with theme data ready for database insertion
        """
        # Get latest snapshot if not provided
        if not snapshot:
            snapshot = db.query(VillageDataSnapshot).filter(
                VillageDataSnapshot.village_id == village.id
            ).order_by(VillageDataSnapshot.snapshot_date.desc()).first()

            if not snapshot:
                raise ValueError(f"No data snapshot found for village {village.name}")

        # Build context prompt
        prompt = self.build_context_prompt(db, village, snapshot, category)

        # Call Claude API
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract JSON from response
            response_text = message.content[0].text

            # Strip markdown code blocks if present
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]  # Remove ```json
            if response_text.startswith("```"):
                response_text = response_text[3:]  # Remove ```
            if response_text.endswith("```"):
                response_text = response_text[:-3]  # Remove trailing ```
            response_text = response_text.strip()

            # Parse JSON
            theme_data = json.loads(response_text)

            # Add metadata
            theme_data["village_id"] = village.id
            theme_data["category_id"] = category.id
            theme_data["ai_model"] = self.model
            theme_data["ai_prompt_version"] = self.prompt_version
            theme_data["generated_at"] = datetime.now()

            # Rename fields to match database schema
            theme_data["evidence_conflicts"] = theme_data.pop("evidence_conflict_ids", [])
            theme_data["evidence_pois"] = theme_data.pop("evidence_poi_ids", [])

            return theme_data

        except json.JSONDecodeError as e:
            raise ValueError(f"Claude returned invalid JSON: {str(e)}\nResponse: {response_text}")
        except Exception as e:
            raise RuntimeError(f"Error calling Claude API: {str(e)}")

    def generate_multiple_themes(
        self,
        db: Session,
        village: Village,
        categories: List[IdentityCategory],
        snapshot: Optional[VillageDataSnapshot] = None
    ) -> List[Dict]:
        """
        Generate multiple themes for different categories

        Args:
            db: Database session
            village: Village to generate themes for
            categories: List of categories to generate themes for
            snapshot: Data snapshot (will fetch latest if not provided)

        Returns:
            List of theme dictionaries
        """
        themes = []

        for category in categories:
            try:
                theme = self.generate_theme(db, village, category, snapshot)
                themes.append(theme)
            except Exception as e:
                print(f"Error generating theme for category {category.name}: {str(e)}")
                continue

        return themes

    def save_theme_to_db(self, db: Session, theme_data: Dict) -> IdentityTheme:
        """
        Save a generated theme to the database

        Args:
            db: Database session
            theme_data: Theme dictionary from generate_theme()

        Returns:
            Created IdentityTheme object
        """
        # Create new IdentityTheme
        theme = IdentityTheme(**theme_data)

        db.add(theme)
        db.commit()
        db.refresh(theme)

        return theme

    def generate_and_save_themes(
        self,
        db: Session,
        village_slug: str,
        category_names: Optional[List[str]] = None
    ) -> List[IdentityTheme]:
        """
        Complete workflow: generate and save themes to database

        Args:
            db: Database session
            village_slug: Village slug to generate themes for
            category_names: List of category names (generates for all if None)

        Returns:
            List of created IdentityTheme objects
        """
        # Get village
        village = db.query(Village).filter(Village.slug == village_slug).first()
        if not village:
            raise ValueError(f"Village not found: {village_slug}")

        # Get categories
        if category_names:
            categories = db.query(IdentityCategory).filter(
                IdentityCategory.name.in_(category_names)
            ).all()
        else:
            categories = db.query(IdentityCategory).all()

        if not categories:
            raise ValueError("No categories found")

        # Get latest snapshot
        snapshot = db.query(VillageDataSnapshot).filter(
            VillageDataSnapshot.village_id == village.id
        ).order_by(VillageDataSnapshot.snapshot_date.desc()).first()

        if not snapshot:
            raise ValueError(f"No data snapshot found for {village.name}")

        # Mark snapshot as used for identity generation
        if not snapshot.used_for_identity_generation:
            snapshot.used_for_identity_generation = True
            snapshot.identity_generation_timestamp = datetime.now()
            db.commit()

        # Generate themes
        theme_dicts = self.generate_multiple_themes(db, village, categories, snapshot)

        # Save to database
        saved_themes = []
        for theme_data in theme_dicts:
            theme = self.save_theme_to_db(db, theme_data)
            saved_themes.append(theme)

        return saved_themes


# Predefined theme suggestions for specific scenarios
THEME_SUGGESTIONS = {
    "infrastructure": {
        "phoenix_village": {
            "description": "Village rebuilt after destruction",
            "keywords": ["reconstruction", "resilience", "modernization"]
        },
        "bridge_builder": {
            "description": "Village connecting regions through infrastructure",
            "keywords": ["connectivity", "roads", "bridges"]
        }
    },
    "economy": {
        "sleeping_waters": {
            "description": "Untapped water resources (ponds, rivers)",
            "keywords": ["ponds", "aquaculture", "irrigation"]
        },
        "artisan_revival": {
            "description": "Traditional crafts and local production",
            "keywords": ["crafts", "artisan", "local economy"]
        }
    },
    "tourism": {
        "heritage_trail": {
            "description": "Historical tourism opportunity",
            "keywords": ["heritage", "history", "tourism"]
        },
        "nature_gateway": {
            "description": "Nature and outdoor tourism",
            "keywords": ["nature", "hiking", "ecotourism"]
        }
    }
}
