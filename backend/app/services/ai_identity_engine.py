"""
AI Identity Engine - Enhanced Claude API integration with RAG context

This service generates village identity options using:
1. Audit data from the 5-step wizard
2. Similar case studies (RAG context)
3. Matching funding programs
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime
from anthropic import Anthropic
from sqlalchemy.orm import Session

from app.models import Village
from app.models.revival_case_study import RevivalCaseStudy
from app.models.funding_program import FundingProgram
from app.models.local_conflict import LocalConflict


class AIIdentityEngine:
    """Enhanced Claude-powered identity generator with RAG context"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AI identity engine with Claude API

        Args:
            api_key: Anthropic API key (defaults to env var ANTHROPIC_API_KEY)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"  # Per spec
        self.max_tokens = 20000  # High limit to prevent JSON truncation with full identity options
        self.temperature = 0.7

    def find_similar_case_studies(
        self,
        db: Session,
        population: Optional[int] = None,
        themes: Optional[List[str]] = None,
        geography: Optional[List[str]] = None,
        limit: int = 5
    ) -> List[Dict]:
        """
        Find case studies similar to the given parameters.

        Returns case studies with relevance scores for RAG context.
        """
        all_case_studies = db.query(RevivalCaseStudy).all()

        # Determine population band
        search_pop_band = None
        if population:
            if population < 100:
                search_pop_band = 'under_100'
            elif population < 500:
                search_pop_band = '100_500'
            elif population < 1000:
                search_pop_band = '500_1000'
            elif population < 5000:
                search_pop_band = '1000_5000'
            else:
                search_pop_band = '5000_plus'

        # Score each case study
        scored_results = []

        for cs in all_case_studies:
            score = 0

            # Theme matching (+3 per match)
            if themes and cs.themes:
                theme_matches = len(set(themes) & set(cs.themes))
                score += theme_matches * 3

            # Geography matching (+2 per match)
            if geography and cs.geography_tags:
                geo_matches = len(set(geography) & set(cs.geography_tags))
                score += geo_matches * 2

            # Population band matching (+2)
            if search_pop_band and cs.population_band == search_pop_band:
                score += 2

            if score > 0:
                scored_results.append({
                    "case_study": cs,
                    "score": score
                })

        # Sort by score and limit
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        return scored_results[:limit]

    def find_matching_funding(
        self,
        db: Session,
        themes: Optional[List[str]] = None,
        budget: Optional[int] = None,
        population: Optional[int] = None,
        limit: int = 5
    ) -> List[Dict]:
        """
        Find funding programs that match project parameters.
        """
        programs = db.query(FundingProgram).filter(
            FundingProgram.is_active == True
        ).all()

        scored_results = []

        for prog in programs:
            score = 0
            match_reasons = []

            # Theme matching (+3 per match)
            if themes and prog.eligible_themes:
                theme_matches = set(themes) & set(prog.eligible_themes)
                if theme_matches:
                    score += len(theme_matches) * 3
                    match_reasons.append(f"themes: {', '.join(theme_matches)}")

            # Budget range matching (+2)
            if budget and prog.amount_max:
                if budget <= prog.amount_max:
                    score += 2
                    match_reasons.append(f"budget fits (up to €{prog.amount_max:,})")

            # Population eligibility (+1)
            if population and prog.eligible_population_max:
                if population <= prog.eligible_population_max:
                    score += 1

            # Active bonus
            if prog.is_active:
                score += 1

            if score > 1:
                scored_results.append({
                    "program": prog,
                    "score": score,
                    "match_reasons": match_reasons
                })

        scored_results.sort(key=lambda x: x["score"], reverse=True)
        return scored_results[:limit]

    def build_rag_context(
        self,
        similar_case_studies: List[Dict],
        matching_funding: List[Dict]
    ) -> str:
        """
        Build RAG context section for the prompt.
        """
        context_parts = []

        # Case studies section
        if similar_case_studies:
            context_parts.append("SIMILAR SUCCESS STORIES (for inspiration):")
            for i, item in enumerate(similar_case_studies, 1):
                cs = item["case_study"]
                context_parts.append(f"""
{i}. {cs.village_name} ({cs.region}, {cs.country})
   Population: {cs.population_before or '?'} → {cs.population_after or '?'}
   Strategy: {cs.strategy}
   Key Projects: {', '.join(cs.key_projects) if cs.key_projects else 'N/A'}
   Outcomes: {cs.outcomes}
   Timeline: {cs.timeline_years or '?'} years
   Funding used: {', '.join(cs.funding_sources) if cs.funding_sources else 'N/A'}
   Lessons: {cs.lessons_learned or 'N/A'}
""")

        # Funding programs section
        if matching_funding:
            context_parts.append("\nAVAILABLE FUNDING PROGRAMS:")
            for i, item in enumerate(matching_funding, 1):
                prog = item["program"]
                context_parts.append(f"""
{i}. {prog.name} ({prog.provider})
   Eligible themes: {', '.join(prog.eligible_themes) if prog.eligible_themes else 'All'}
   Amount: €{prog.amount_min or 0:,}-€{prog.amount_max or 0:,} (up to {prog.funding_percentage_max or '?'}%)
   Deadline: {prog.deadline_type}
   Timeline: {prog.typical_timeline_months or '?'} months
   Process: {prog.process_summary or 'N/A'}
   Tips: {prog.tips or 'N/A'}
""")

        return "\n".join(context_parts)

    def extract_themes_from_audit(self, audit_data: Dict) -> List[str]:
        """Extract theme tags from audit data for matching."""
        themes = []

        # From history section
        war_periods = audit_data.get("warPeriods", [])
        if "ww2" in war_periods or "WWII" in war_periods:
            themes.extend(["heritage", "ww2", "history"])
        if "ww1" in war_periods or "WWI" in war_periods:
            themes.extend(["heritage", "ww1", "history"])
        if "medieval" in war_periods:
            themes.extend(["heritage", "medieval"])

        event_types = audit_data.get("eventTypes", [])
        if event_types:
            themes.extend(["heritage", "history"])

        # From environment section
        water_features = audit_data.get("waterFeatures", [])
        if water_features:
            themes.extend(["ecology", "water", "nature"])
            if "ponds" in water_features:
                themes.append("ponds")
            if "river" in water_features:
                themes.append("rivers")

        landscape = audit_data.get("landscape", [])
        if "forest" in landscape:
            themes.extend(["ecology", "forestry", "nature"])
        if "mountains" in landscape:
            themes.extend(["tourism", "hiking"])

        # From economy section
        local_products = audit_data.get("localProducts", [])
        if local_products:
            themes.extend(["agriculture", "local_products", "gastronomy"])

        services = audit_data.get("services", [])
        vibe = audit_data.get("vibe", "")

        if "artisan" in str(local_products).lower():
            themes.append("artisan")

        # Deduplicate
        return list(set(themes))

    def extract_geography_from_audit(self, audit_data: Dict) -> List[str]:
        """Extract geography tags from audit data."""
        geography = []

        water_features = audit_data.get("waterFeatures", [])
        for wf in water_features:
            if wf.lower() in ["ponds", "river", "lake", "streams"]:
                geography.append(wf.lower())

        landscape = audit_data.get("landscape", [])
        for ls in landscape:
            if ls.lower() in ["forest", "mountains", "valley", "coast", "plateau", "hills"]:
                geography.append(ls.lower())

        return list(set(geography))

    def analyze_village_unique_assets(
        self,
        db: Session,
        village: Village,
        audit_data: Dict
    ) -> str:
        """
        Extract village's unique assets for breakthrough innovation ideas.
        These assets help generate Tier 2 and Tier 3 breakthrough concepts.
        """
        assets = []

        # Geographic/Environmental features from audit
        water_features = audit_data.get("waterFeatures", [])
        if water_features:
            water_str = ", ".join(water_features)
            if any(w.lower() in ["ponds", "étangs", "lacs"] for w in water_features):
                assets.append(f"- **Étangs/Plans d'eau ({water_str}):** Aquaculture durable, aquaponie, recherche qualité de l'eau, tourisme nature, réserve écologique")
            if any(w.lower() in ["river", "rivière", "ruisseau"] for w in water_features):
                assets.append(f"- **Cours d'eau ({water_str}):** Micro-hydroélectrique, sports nautiques, corridor écologique, pêche durable")

        landscape = audit_data.get("landscape", [])
        if landscape:
            if any(l.lower() in ["forest", "forêt", "bois"] for l in landscape):
                assets.append("- **Forêt:** Sylviculture durable, biomasse, champignons, biodiversité, séquestration carbone, éco-tourisme")
            if any(l.lower() in ["mountains", "montagnes", "collines", "hills"] for l in landscape):
                assets.append("- **Relief/Collines:** Randonnée, VTT, parapente, points de vue panoramiques")

        # Historical assets from audit and conflicts
        war_periods = audit_data.get("warPeriods", [])
        event_types = audit_data.get("eventTypes", [])

        # Check for WWII conflicts in database using correct attributes
        # LocalConflict has 'date' (Date object) and 'period' (String), not 'year'
        conflicts = db.query(LocalConflict).filter(LocalConflict.village_id == village.id).all()

        # Check for WWII: look at date field (if exists) or period field
        wwii_conflicts = []
        medieval_conflicts = []
        for c in conflicts:
            # Check date if available
            if c.date:
                year = c.date.year
                if 1939 <= year <= 1945:
                    wwii_conflicts.append(c)
            # Check period field
            if c.period:
                period_lower = c.period.lower()
                if any(term in period_lower for term in ["ww2", "wwii", "1939-1945", "seconde guerre", "world war ii"]):
                    wwii_conflicts.append(c)
                if any(term in period_lower for term in ["médiéval", "medieval", "moyen âge", "moyen-âge", "moyen age"]):
                    medieval_conflicts.append(c)

        if wwii_conflicts or "ww2" in str(war_periods).lower() or "1944" in str(event_types):
            assets.append("- **Histoire WWII/Villages Brûlés:** Mémorial, tourisme de mémoire, éducation à la paix, partenariats internationaux, centre de recherche résilience")

        if medieval_conflicts or "medieval" in str(war_periods).lower():
            assets.append("- **Patrimoine médiéval:** Restauration château, reconstitution historique, tourisme patrimonial, recherche archéologique")

        legends = audit_data.get("legends", "")
        monuments = audit_data.get("monuments", "")
        if legends or monuments:
            assets.append("- **Patrimoine culturel:** Légendes locales, monuments historiques, circuits patrimoniaux")

        # Economic/Agricultural assets
        local_products = audit_data.get("localProducts", [])
        agriculture = audit_data.get("agriculture", "")
        if local_products or agriculture:
            products_str = ", ".join(local_products) if local_products else agriculture
            assets.append(f"- **Tradition agricole ({products_str}):** Agriculture de précision, agri-tourisme, circuits courts, innovation alimentaire, label qualité")

        natural_resources = audit_data.get("naturalResources", "")
        if natural_resources:
            assets.append(f"- **Ressources naturelles ({natural_resources}):** Exploitation durable, énergie renouvelable, recherche environnementale")

        # Generic rural advantages (always relevant)
        assets.append("- **Localisation rurale:** Test véhicules autonomes (routes peu fréquentées), hub télétravail, qualité de vie, air pur")
        assets.append("- **Faible pollution lumineuse:** Astro-tourisme, réserve de ciel étoilé")
        assets.append("- **Immobilier abordable:** Attraction nomades numériques, télétravailleurs, résidents étrangers")

        return "\n".join(assets) if assets else "- Combinaison unique d'atouts naturels et historiques adaptée à l'innovation rurale"

    def generate_identity_options(
        self,
        db: Session,
        village_slug: str,
        audit_data: Dict,
        num_options: int = 3
    ) -> Dict:
        """
        Generate identity options for a village based on audit data.

        Args:
            db: Database session
            village_slug: Village identifier
            audit_data: Data from the 5-step audit wizard
            num_options: Number of identity options to generate (default 3)

        Returns:
            Dictionary with identity options, each containing:
            - identity_title
            - identity_narrative
            - confidence
            - themes
            - projects (with funding matches and case study references)
        """
        # Get village
        village = db.query(Village).filter(Village.slug == village_slug).first()
        if not village:
            raise ValueError(f"Village not found: {village_slug}")

        # Extract themes and geography from audit
        themes = self.extract_themes_from_audit(audit_data)
        geography = self.extract_geography_from_audit(audit_data)

        # Find similar case studies
        similar_case_studies = self.find_similar_case_studies(
            db,
            population=village.population,
            themes=themes,
            geography=geography,
            limit=5
        )

        # Find matching funding programs
        matching_funding = self.find_matching_funding(
            db,
            themes=themes,
            budget=100000,  # Default budget estimate
            population=village.population,
            limit=8
        )

        # Build RAG context
        rag_context = self.build_rag_context(similar_case_studies, matching_funding)

        # Analyze village unique assets for breakthrough ideas
        unique_assets = self.analyze_village_unique_assets(db, village, audit_data)

        # Build the main prompt
        prompt = self._build_generation_prompt(
            village=village,
            audit_data=audit_data,
            rag_context=rag_context,
            unique_assets=unique_assets,
            num_options=num_options
        )

        # Call Claude API
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract and parse response
            response_text = message.content[0].text
            response_text = self._clean_json_response(response_text)

            # Check for potential truncation before parsing
            output_tokens = message.usage.output_tokens
            was_truncated = message.stop_reason == "max_tokens"

            try:
                result = json.loads(response_text)
            except json.JSONDecodeError as e:
                # Check if it looks like truncation (incomplete JSON)
                if was_truncated or not response_text.rstrip().endswith("}"):
                    raise ValueError(
                        f"Response was truncated (used {output_tokens} tokens). "
                        f"Try generating fewer identity options (1-2 instead of 3). "
                        f"JSON error: {str(e)}"
                    )
                else:
                    raise ValueError(f"Claude returned invalid JSON: {str(e)}")

            # Add metadata
            result["metadata"] = {
                "village_slug": village_slug,
                "village_name": village.name,
                "generated_at": datetime.now().isoformat(),
                "model": self.model,
                "similar_case_studies_used": len(similar_case_studies),
                "funding_programs_matched": len(matching_funding),
                "input_tokens": message.usage.input_tokens,
                "output_tokens": output_tokens,
                "was_truncated": was_truncated,
                "estimated_cost": self._estimate_cost(
                    message.usage.input_tokens,
                    output_tokens
                )
            }

            return result

        except ValueError:
            # Re-raise ValueError (truncation/JSON errors) as-is
            raise
        except Exception as e:
            raise RuntimeError(f"Error calling Claude API: {str(e)}")

    def _build_generation_prompt(
        self,
        village: Village,
        audit_data: Dict,
        rag_context: str,
        unique_assets: str,
        num_options: int = 3
    ) -> str:
        """Build the full prompt for Claude with 3-tier identity system."""

        # Extract audit sections
        free_description = audit_data.get("freeDescription", "")

        # 3-Tier system instructions
        tier_instructions = f"""
═══════════════════════════════════════════════════════════════
SYSTÈME 3 NIVEAUX D'IDENTITÉ - INSTRUCTIONS CRITIQUES
═══════════════════════════════════════════════════════════════

Vous DEVEZ générer exactement 3 options d'identité représentant 3 NIVEAUX DIFFÉRENTS d'ambition et d'innovation:

───────────────────────────────────────────────────────────────
NIVEAU 1: PARCOURS PROUVÉ (Confiance: 0.75-0.85)
───────────────────────────────────────────────────────────────

**Objectif:** Basé sur des preuves, faible risque, hautement réplicable

**Approche:**
- Référencer fortement 2-3 études de cas spécifiques (ex: "Inspiré par: Oxelaëre, Saint-Saud")
- Utiliser des modèles éprouvés: village bio, services coopératifs, tourisme patrimonial
- Budgets conservateurs (€50k-€200k par projet)
- Délais courts (12-24 mois)
- Risque minimal, validation maximale

**Les projets doivent:**
- Répliquer directement des modèles ayant fait leurs preuves
- Utiliser des sources de financement établies (LEADER, FEADER, Région)
- Nécessiter peu d'innovation
- Être immédiatement réalisables
- Montrer des précédents clairs

**Ton:** Rassurant, pratique, "nous avons vu cela fonctionner"

───────────────────────────────────────────────────────────────
NIVEAU 2: INNOVATION CIBLÉE (Confiance: 0.65-0.75)
───────────────────────────────────────────────────────────────

**Objectif:** Modèles éprouvés + réflexion innovante spécifique au village

**Approche:**
- Prendre des concepts éprouvés, les adapter créativement aux atouts UNIQUES de CE village
- Référencer des études de cas MAIS aller au-delà de la réplication directe
- Budgets moyens (€100k-€500k par projet)
- Délais moyens (24-36 mois)
- Risques calculés, innovation dans des cadres éprouvés

**ATOUTS UNIQUES DE CE VILLAGE à exploiter:**
{unique_assets}

**Les projets doivent:**
- Combiner 2-3 modèles éprouvés de nouvelles façons
- Créer des innovations spécifiques au village
- Montrer un potentiel de développement économique
- Inclure des partenariats recherche/université
- Être ambitieux mais réalisables

**Ton:** Ambitieux, créatif, "adaptons des idées prouvées à NOTRE situation unique"

───────────────────────────────────────────────────────────────
NIVEAU 3: VISION TRANSFORMATRICE (Confiance: 0.50-0.65)
───────────────────────────────────────────────────────────────

**Objectif:** Avant-garde, potentiel de rupture, mais ancré dans la réalité

**Approche:**
- Repousser les limites tout en restant réalisable
- Référencer des tendances émergentes, pas seulement les succès passés
- Budgets plus importants (€200k-€1M+ par projet)
- Délais plus longs (36-60 mois)
- Risque plus élevé, potentiel transformationnel

**Types d'idées de rupture** (exemples pour illustrer le niveau d'ambition):
- Laboratoires de test technologique (véhicules autonomes, drones, 5G rural)
- Partenariats de recherche (réseaux IoT eau/biodiversité, innovation agricole)
- Centres internationaux (recherche sur la paix, institut innovation rurale)
- Industries primaires high-tech (aquaculture avec IA, agriculture de précision)
- Campus d'innovation (chercheurs à distance, incubateurs, hubs nomades numériques)
- Living Labs (pilotes économie circulaire, village zéro déchet, smart village)

**CRITIQUE:** Analysez les atouts UNIQUES de CE village et générez des idées de rupture qui:
1. Exploitent ce que CE village a et que d'autres n'ont pas
2. Pourraient attirer l'attention nationale/internationale
3. Créent des partenariats de recherche ou d'innovation
4. Positionnent le village comme leader/pionnier dans quelque chose de spécifique
5. Montrent un potentiel économique transformationnel

**Ton:** Visionnaire, transformationnel, "faisons l'histoire"

═══════════════════════════════════════════════════════════════
EXIGENCES CRITIQUES:
═══════════════════════════════════════════════════════════════

1. **Diversité radicale:** Les 3 niveaux DOIVENT être DRAMATIQUEMENT différents les uns des autres
2. **Ordre des niveaux:** Toujours générer dans l'ordre: Niveau 1 (prouvé), Niveau 2 (innovation), Niveau 3 (rupture)
3. **Spécifique au village:** Niveaux 2 et 3 doivent exploiter profondément les atouts UNIQUES de CE village
4. **Ancrage dans la faisabilité:** Même le Niveau 3 doit être réalisable, pas de science-fiction
5. **Scores de confiance:** Niveau 1 (0.75-0.85), Niveau 2 (0.65-0.75), Niveau 3 (0.50-0.65)
6. **Références aux études de cas:** Niveau 1 référence 2-3 études, Niveau 2 référence 1-2, Niveau 3 peut référencer des tendances émergentes
7. **Ancrage économique:** TOUS les niveaux doivent montrer la viabilité économique et création d'emplois
8. **Champ tier:** Inclure "tier": 1, 2, ou 3 dans chaque option
9. **Champ tier_label:** Inclure "tier_label": "Parcours Prouvé", "Innovation Ciblée", ou "Vision Transformatrice"

"""

        prompt = f"""LANGUE OBLIGATOIRE - CRITICAL INSTRUCTION:
Vous DEVEZ répondre UNIQUEMENT en français. Tout le contenu DOIT être en langue française:
- identity_title (en français)
- identity_narrative (en français)
- summary_identity (en français)
- live_here_summary (en français)
- project titles (en français)
- project descriptions (en français)
- first_steps (en français)
- ALL text content MUST be in French

This is for a French village audience. French language is MANDATORY and NON-NEGOTIABLE.

---

You are analyzing a French village for identity development and revival projects.

VILLAGE DATA:
Name: {village.name}
Department: {village.department or 'Unknown'}
Region: {village.region or 'Unknown'}
Population: {village.population or 'Unknown'}

AUDIT DATA FROM VILLAGE ADMINISTRATOR:

HISTORY & HERITAGE:
- War periods: {', '.join(audit_data.get('warPeriods', [])) or 'None specified'}
- Event types: {', '.join(audit_data.get('eventTypes', [])) or 'None specified'}
- Monuments: {audit_data.get('monuments', 'Not specified')}
- Legends: {audit_data.get('legends', 'Not specified')}
- Additional history: {audit_data.get('historyNotes', 'Not specified')}

ENVIRONMENT & RESOURCES:
- Water features: {', '.join(audit_data.get('waterFeatures', [])) or 'None'}
- Landscape: {', '.join(audit_data.get('landscape', [])) or 'Not specified'}
- Agriculture: {audit_data.get('agriculture', 'Not specified')}
- Natural resources: {audit_data.get('naturalResources', 'Not specified')}
- Environment notes: {audit_data.get('environmentNotes', 'Not specified')}

ECONOMY, TRADITIONS & LIFE:
- Local products: {', '.join(audit_data.get('localProducts', [])) or 'None'}
- Potential products: {audit_data.get('potentialProducts', 'Not specified')}
- Festivals: {audit_data.get('festivals', 'Not specified')}
- Services: {', '.join(audit_data.get('services', [])) or 'Not specified'}
- Vibe: {audit_data.get('vibe', 'Not specified')}
- Living description: {audit_data.get('livingDescription', 'Not specified')}

FREE DESCRIPTION FROM MAYOR/ADMINISTRATOR:
{free_description or 'Not provided'}

{rag_context}

{tier_instructions}

MODÈLES DE SUCCÈS À UTILISER (surtout pour Niveau 1 et 2):

**Transitions Bio/Organique:**
- Saint-Pierre-de-Frugie: Interdiction pesticides + écocentre → 44% croissance population
- Correns: Village 100% bio → Reconnaissance nationale

**Innovation Services:**
- Oxelaëre: Soutien boulanger + Olympiades + restaurant → 13% croissance
- Saint-Saud: Station-service coopérative (34 actionnaires) + résidents britanniques
- Services mobiles: Bars itinérants, toilettage → Combler les lacunes de services

**Transitions Énergie/Industrie:**
- Loos-en-Gohelle: Charbon → Climat → Patrimoine UNESCO
- Coopératives solaires avec propriété citoyenne

**Infrastructure Sociale:**
- Olympiades villageoises attirant 4× la population
- Bars municipaux dans d'anciennes fermes
- Résidences seniors partagées

**Modèles Coopératifs:**
- Station-service: €169k levés auprès de 34 villageois en 10 jours
- Entreprises détenues par la communauté
- Financement par actionnariat

**Résidents Internationaux:**
- Britanniques en Périgord (15% de la population)
- Nomades numériques en Andalousie
- Qualité de vie + logement abordable

**Technologie/Numérique:**
- Hubs télétravail
- Coworking + coliving
- Initiatives smart village
- FabLabs et makerspaces

═══════════════════════════════════════════════════════════════
TÂCHE DE GÉNÉRATION - EXIGENCES DE QUALITÉ ÉLEVÉE
═══════════════════════════════════════════════════════════════

Générez EXACTEMENT 3 identités de village, une par niveau (tier).

TOUTES les identités doivent avoir le MÊME NIVEAU DE QUALITÉ ET DÉTAIL.
Le niveau 3 n'est PAS une excuse pour des descriptions courtes.

═══════════════════════════════════════════════════════════════
EXIGENCES POUR CHAQUE IDENTITÉ (OBLIGATOIRES):
═══════════════════════════════════════════════════════════════

1. TITRE D'IDENTITÉ (identity_title):
   - Créatif, évocateur, mémorable, UNIQUE
   - 3-6 mots en français
   - Exemples BONS: "Village Laboratoire Vivant", "Vallée des Mémoires et de l'Eau"
   - Exemples MAUVAIS: "Renouveau", "Patrimoine", "Développement" (trop génériques!)

2. RÉSUMÉ COURT (summary_identity):
   - 1-2 phrases complètes (100-150 caractères)
   - Capture l'essence unique de cette identité

3. NARRATION DÉTAILLÉE (identity_narrative):
   - MINIMUM 3 paragraphes complets
   - MINIMUM 800 caractères (idéalement 1000-1500)
   - Explique POURQUOI cette identité pour CE village
   - Ancrage dans l'histoire et les atouts spécifiques
   - Vision concrète pour l'avenir
   - Émotionnelle et inspirante

4. VIE QUOTIDIENNE (live_here_summary):
   - MINIMUM 2 paragraphes complets
   - MINIMUM 400 caractères
   - Décrit la vie future des habitants
   - Concrète, émotionnelle, inspirante

5. PROJETS (4-5 projets par identité):

   CHAQUE projet DOIT inclure:

   a) title: Titre spécifique et descriptif
      - BON: "Circuit Pédagogique des Hameaux de Mémoire 1944"
      - MAUVAIS: "Projet Mémoire"

   b) description: MINIMUM 150 caractères, 3-4 phrases complètes
      - Explique: quoi, comment, pourquoi, pour qui
      - Résultats attendus

   c) inspired_by: OBLIGATOIRE - référence à une étude de cas
      - Format: {{"village_name": "Saint-Saud-la-Coussière", "relevance": "Modèle coopératif ayant généré 34 actionnaires locaux"}}
      - NE JAMAIS laisser vide ou null

   d) potential_funding: 2-3 programmes avec détails
      - Inclure: program_name, match_score, why_relevant, estimated_amount

   e) first_steps: 4-5 étapes CONCRÈTES et DÉTAILLÉES
      - Chaque étape: 1-2 phrases complètes
      - Spécifiques et actionnables
      - Exemple: "Contacter l'Agence de l'Eau Adour-Garonne pour présenter le projet de monitoring des étangs et obtenir un premier avis technique"

   f) budget_min et budget_max: Fourchettes réalistes
      - Tier 1: €50,000-€200,000
      - Tier 2: €100,000-€500,000
      - Tier 3: €200,000-€1,000,000

   g) timeline_months: Durée en mois
      - Tier 1: 12-24 mois
      - Tier 2: 24-36 mois
      - Tier 3: 36-60 mois

   h) difficulty: "easy", "medium", ou "hard"

   i) themes: 3-5 thèmes pertinents

═══════════════════════════════════════════════════════════════
FORMAT JSON STRICT:
═══════════════════════════════════════════════════════════════

Retournez UNIQUEMENT ce JSON (pas de texte avant ou après):

{{
    "options": [
        {{
            "tier": 1,
            "tier_label": "Parcours Prouvé",
            "identity_title": "Village Coopératif des Étangs",
            "identity_narrative": "[MINIMUM 800 caractères, 3+ paragraphes expliquant l'identité en profondeur, pourquoi elle convient à ce village, comment elle s'ancre dans son histoire et ses atouts, quelle vision pour l'avenir...]",
            "confidence": 0.82,
            "themes": ["coopérative", "services", "solidarité", "économie locale"],
            "summary_identity": "Un village qui réinvente la solidarité rurale autour de ses étangs et de son patrimoine",
            "live_here_summary": "[MINIMUM 400 caractères, 2+ paragraphes décrivant la vie quotidienne future des habitants, concrète et inspirante...]",
            "projects": [
                {{
                    "title": "Coopérative Multi-Services Villageoise",
                    "description": "Création d'une coopérative citoyenne regroupant épicerie, dépôt de pain, point relais colis et café associatif. Le modèle s'inspire directement de Saint-Saud-la-Coussière où 34 villageois ont investi €169,000 en 10 jours. La coopérative offrira des parts sociales à €100 accessibles à tous les habitants.",
                    "timeline_months": 18,
                    "budget_min": 80000,
                    "budget_max": 180000,
                    "difficulty": "medium",
                    "inspired_by": {{
                        "village_name": "Saint-Saud-la-Coussière",
                        "relevance": "Modèle coopératif ayant généré 34 actionnaires locaux et levé €169k en 10 jours"
                    }},
                    "potential_funding": [
                        {{
                            "program_name": "LEADER",
                            "match_score": 0.9,
                            "why_relevant": "Programme parfait pour services ruraux innovants",
                            "estimated_amount": "€60,000 (80% du montant éligible)"
                        }},
                        {{
                            "program_name": "Région Nouvelle-Aquitaine - Fonds Territoires",
                            "match_score": 0.85,
                            "why_relevant": "Soutien aux commerces de proximité en zone rurale",
                            "estimated_amount": "€30,000 (50%)"
                        }}
                    ],
                    "first_steps": [
                        "Organiser une réunion publique pour présenter le projet et jauger l'intérêt des habitants (inviter le maire de Saint-Saud comme témoin)",
                        "Constituer un groupe de pilotage de 8-10 personnes motivées représentant différentes générations",
                        "Contacter le GAL (Groupe d'Action Locale) de Haute-Corrèze pour un premier rendez-vous sur les financements LEADER",
                        "Commander une étude de faisabilité auprès de la Chambre de Commerce et d'Industrie (CCI)"
                    ],
                    "themes": ["cooperative", "commerce", "services", "social", "économie_locale"]
                }}
            ]
        }},
        {{
            "tier": 2,
            "tier_label": "Innovation Ciblée",
            "identity_title": "[Titre créatif exploitant les atouts UNIQUES du village]",
            "identity_narrative": "[MINIMUM 800 caractères, même qualité que tier 1]",
            "confidence": 0.72,
            "themes": ["..."],
            "summary_identity": "[100-150 caractères]",
            "live_here_summary": "[MINIMUM 400 caractères]",
            "projects": [
                {{
                    "title": "[Titre spécifique]",
                    "description": "[MINIMUM 150 caractères]",
                    "inspired_by": {{"village_name": "[...]", "relevance": "[...]"}},
                    "potential_funding": [...],
                    "first_steps": ["[Étape détaillée 1]", "[Étape détaillée 2]", "[Étape détaillée 3]", "[Étape détaillée 4]"],
                    "budget_min": 150000,
                    "budget_max": 400000,
                    "timeline_months": 30,
                    "difficulty": "medium",
                    "themes": ["..."]
                }}
            ]
        }},
        {{
            "tier": 3,
            "tier_label": "Vision Transformatrice",
            "identity_title": "[Titre visionnaire mais spécifique]",
            "identity_narrative": "[MINIMUM 800 caractères - MÊME QUALITÉ QUE TIER 1, pas de version courte!]",
            "confidence": 0.58,
            "themes": ["..."],
            "summary_identity": "[100-150 caractères]",
            "live_here_summary": "[MINIMUM 400 caractères]",
            "projects": [...]
        }}
    ]
}}

═══════════════════════════════════════════════════════════════
RAPPELS CRITIQUES:
═══════════════════════════════════════════════════════════════

- EXACTEMENT 3 options (tier 1, 2, 3)
- TOUS les champs sont OBLIGATOIRES
- MINIMUM 800 caractères pour identity_narrative (TOUS les tiers!)
- MINIMUM 150 caractères pour chaque project description
- inspired_by JAMAIS null ou vide
- first_steps avec 4-5 étapes DÉTAILLÉES
- Contenu 100% en FRANÇAIS
- Spécifique à CE village, pas générique
- Les 3 tiers ont la MÊME QUALITÉ de détails
"""
        return prompt

    def _clean_json_response(self, response_text: str) -> str:
        """Clean Claude's response to extract JSON."""
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        return response_text.strip()

    def _estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate API cost in USD.

        Claude Sonnet pricing (as of 2024):
        - Input: $3 per million tokens
        - Output: $15 per million tokens
        """
        input_cost = (input_tokens / 1_000_000) * 3
        output_cost = (output_tokens / 1_000_000) * 15
        return round(input_cost + output_cost, 4)


# Singleton instance for easy import
_engine_instance = None


def get_ai_engine() -> AIIdentityEngine:
    """Get or create the AI identity engine instance."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = AIIdentityEngine()
    return _engine_instance
