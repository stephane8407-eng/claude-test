"""
Phase E Week 2: Grant Matching Service

Matches village projects to relevant funding programs using a scoring algorithm.
Considers: population band, themes, budget compatibility, deadline type.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.funding_program import FundingProgram
from app.models.project_instance import ProjectInstance


class GrantMatcher:
    """Matches projects to funding programs with scoring"""

    # Population bands mapping
    POPULATION_BANDS = [
        (0, 2000, '<2000'),
        (2000, 5000, '2000-5000'),
        (5000, 10000, '5000-10000'),
        (10000, 20000, '10000-20000'),
        (20000, 50000, '20000-50000'),
        (50000, float('inf'), '>50000')
    ]

    @staticmethod
    def get_population_band(population: int) -> str:
        """Convert population to band string"""
        for min_pop, max_pop, band_name in GrantMatcher.POPULATION_BANDS:
            if min_pop <= population < max_pop:
                return band_name
        return '>50000'

    @staticmethod
    def calculate_match_score(
        project: ProjectInstance,
        program: FundingProgram,
        village_population: int,
        village_region: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate match score 0-100 based on:
        - Population band match (30 points)
        - Theme overlap (30 points)
        - Budget compatibility (25 points)
        - Deadline urgency (15 points)
        """
        score = 0
        reasons = []
        warnings = []

        # Get project themes from project_data
        project_data = project.project_data or {}
        project_themes = set()
        
        # Try different theme field names
        if 'themes' in project_data:
            project_themes = set(project_data['themes']) if isinstance(project_data['themes'], list) else set()
        elif 'funding_sources' in project_data:
            # Extract themes from funding sources
            for source in project_data.get('funding_sources', []):
                if isinstance(source, str):
                    project_themes.add(source.lower())

        # Get project budget
        project_budget = project.budget_estimated_max or project.budget_estimated_min or 0
        if not project_budget and project_data:
            project_budget = project_data.get('budget_max') or project_data.get('budgetMax') or \
                           project_data.get('budget_min') or project_data.get('budgetMin') or 0

        # ========================================
        # 1. Population band match (30 points)
        # ========================================
        pop_band = GrantMatcher.get_population_band(village_population)
        eligible_bands = program.eligible_population_bands or []
        
        if not eligible_bands or 'all' in [b.lower() for b in eligible_bands]:
            score += 30
            reasons.append(f"Toutes populations éligibles")
        elif pop_band in eligible_bands:
            score += 30
            reasons.append(f"Population {village_population:,} hab. compatible ({pop_band})")
        else:
            warnings.append(f"Population hors critères: besoin {', '.join(eligible_bands)}")

        # ========================================
        # 2. Region eligibility (bonus 10 points)
        # ========================================
        eligible_regions = program.eligible_regions or []
        if not eligible_regions or 'All regions' in eligible_regions:
            score += 10
            reasons.append("Toutes régions éligibles")
        elif village_region and village_region in eligible_regions:
            score += 10
            reasons.append(f"Région {village_region} éligible")
        elif village_region:
            warnings.append(f"Région non éligible: besoin {', '.join(eligible_regions)}")

        # ========================================
        # 3. Theme overlap (30 points max)
        # ========================================
        program_themes = set(program.eligible_themes or [])
        
        if not program_themes:
            score += 15  # Half points if program accepts all themes
            reasons.append("Programme multi-thématique")
        elif project_themes:
            overlap = project_themes & program_themes
            if overlap:
                theme_score = min(30, len(overlap) * 10)
                score += theme_score
                reasons.append(f"Thématiques compatibles: {', '.join(overlap)}")
            else:
                # Check for partial match (project may have French themes)
                for pt in project_themes:
                    for pgt in program_themes:
                        if pt.lower() in pgt.lower() or pgt.lower() in pt.lower():
                            score += 10
                            reasons.append(f"Thématique proche: {pgt}")
                            break
                if score < 40:  # No theme match found
                    warnings.append(f"Thématiques différentes: programme = {', '.join(list(program_themes)[:3])}")
        else:
            score += 10  # Some points for projects without explicit themes
            reasons.append("Thématiques à préciser")

        # ========================================
        # 4. Budget compatibility (25 points)
        # ========================================
        if project_budget > 0:
            amount_min = program.amount_min or 0
            amount_max = program.amount_max or float('inf')
            
            if amount_min <= project_budget <= amount_max:
                score += 25
                reasons.append(f"Budget {project_budget:,}€ dans la fourchette ({amount_min:,}€ - {amount_max:,}€)")
            elif project_budget < amount_min:
                diff = amount_min - project_budget
                if diff < amount_min * 0.3:  # Within 30% of minimum
                    score += 10
                    warnings.append(f"Budget légèrement en dessous (min: {amount_min:,}€)")
                else:
                    warnings.append(f"Budget trop bas: minimum requis {amount_min:,}€")
            else:
                diff = project_budget - amount_max
                if diff < amount_max * 0.3:  # Within 30% of maximum
                    score += 10
                    warnings.append(f"Budget légèrement au-dessus (max: {amount_max:,}€)")
                else:
                    warnings.append(f"Budget trop élevé: maximum {amount_max:,}€")
        else:
            score += 10
            reasons.append("Budget à préciser")

        # ========================================
        # 5. Deadline type (15 points)
        # ========================================
        deadline = program.deadline_type or 'rolling'
        if deadline in ['rolling', 'permanent']:
            score += 15
            reasons.append("Dépôt permanent - candidature possible à tout moment")
        elif deadline == 'annual':
            score += 10
            reasons.append("Appel annuel - vérifier les dates")
        elif deadline == 'quarterly':
            score += 12
            reasons.append("Appel trimestriel")
        else:
            score += 5
            warnings.append(f"Vérifier les dates de dépôt ({deadline})")

        return {
            'program_id': program.id,
            'program_name': program.name,
            'organization': program.organization,
            'level': program.level or 'National',
            'score': min(100, score),  # Cap at 100
            'amount_min': program.amount_min,
            'amount_max': program.amount_max,
            'funding_percentage_min': program.funding_percentage_min,
            'funding_percentage_max': program.funding_percentage_max,
            'deadline_type': program.deadline_type,
            'website_url': program.website_url,
            'application_url': program.application_url,
            'description': program.description,
            'requirements': program.requirements,
            'required_documents': program.required_documents,
            'reasons': reasons,
            'warnings': warnings
        }

    @staticmethod
    def match_programs(
        db: Session,
        project_id: int,
        village_population: int,
        village_region: Optional[str] = None,
        limit: int = 10,
        min_score: int = 0
    ) -> List[Dict[str, Any]]:
        """Find and rank matching funding programs for a project"""

        # Get project
        project = db.query(ProjectInstance).filter(ProjectInstance.id == project_id).first()
        if not project:
            return []

        # Get all active programs
        programs = db.query(FundingProgram).filter(FundingProgram.is_active == True).all()

        # Score each program
        matches = []
        for program in programs:
            match_data = GrantMatcher.calculate_match_score(
                project, program, village_population, village_region
            )
            if match_data['score'] >= min_score:
                matches.append(match_data)

        # Sort by score descending
        matches.sort(key=lambda x: x['score'], reverse=True)

        # Return top N
        return matches[:limit]

    @staticmethod
    def match_programs_for_all_projects(
        db: Session,
        village_id: int,
        village_population: int,
        village_region: Optional[str] = None,
        limit_per_project: int = 5
    ) -> Dict[int, List[Dict[str, Any]]]:
        """Match programs for all projects of a village"""

        # Get all projects for village
        projects = db.query(ProjectInstance).filter(
            ProjectInstance.village_id == village_id,
            ProjectInstance.status.in_(['exploring', 'planning', 'in_progress'])
        ).all()

        # Get all active programs once
        programs = db.query(FundingProgram).filter(FundingProgram.is_active == True).all()

        results = {}
        for project in projects:
            matches = []
            for program in programs:
                match_data = GrantMatcher.calculate_match_score(
                    project, program, village_population, village_region
                )
                matches.append(match_data)

            matches.sort(key=lambda x: x['score'], reverse=True)
            results[project.id] = matches[:limit_per_project]

        return results
