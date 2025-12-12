"""
Phase E Week 2: Grant Application Generator

Uses Claude API to generate professional French grant applications.
Creates comprehensive administrative documents for small communes.
"""
import os
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.project_instance import ProjectInstance
from app.models.funding_program import FundingProgram
from app.models.grant_application import GrantApplication
from app.models.village import Village


class ApplicationGenerator:
    """Generates French grant applications using Claude API"""

    def __init__(self):
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        # Lazy import anthropic to avoid issues if not installed
        import anthropic
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def generate_application(
        self,
        db: Session,
        project_id: int,
        program_id: int,
        village_name: str,
        village_population: int,
        village_region: Optional[str] = None,
        village_department: Optional[str] = None,
        maire_name: Optional[str] = None,
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate complete French grant application using Claude API
        
        Returns:
            Dict with application_id, text, program_name, status
        """
        # Get project and program
        project = db.query(ProjectInstance).filter(ProjectInstance.id == project_id).first()
        program = db.query(FundingProgram).filter(FundingProgram.id == program_id).first()

        if not project:
            raise ValueError(f"Project {project_id} not found")
        if not program:
            raise ValueError(f"Funding program {program_id} not found")

        # Build the prompt
        prompt = self._build_application_prompt(
            project=project,
            program=program,
            village_name=village_name,
            village_population=village_population,
            village_region=village_region,
            village_department=village_department,
            maire_name=maire_name,
            additional_context=additional_context
        )

        # Call Claude API
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract generated text
        generated_text = message.content[0].text

        # Calculate requested amount (average of budget range)
        budget_min = project.budget_estimated_min or 0
        budget_max = project.budget_estimated_max or budget_min
        average_budget = (budget_min + budget_max) // 2 if budget_min or budget_max else 0
        
        # Calculate max fundable amount based on program percentage
        funding_pct = program.funding_percentage_max or 50
        amount_requested = int(average_budget * funding_pct / 100)

        # Save to database
        application = GrantApplication(
            project_id=project_id,
            funding_program_id=program_id,
            status='draft',
            generated_content=generated_text,
            amount_requested=amount_requested
        )
        db.add(application)
        db.commit()
        db.refresh(application)

        return {
            'application_id': application.id,
            'text': generated_text,
            'program_name': program.name,
            'program_id': program.id,
            'amount_requested': amount_requested,
            'status': 'draft',
            'created_at': application.created_at.isoformat() if application.created_at else None
        }

    def _build_application_prompt(
        self,
        project: ProjectInstance,
        program: FundingProgram,
        village_name: str,
        village_population: int,
        village_region: Optional[str],
        village_department: Optional[str],
        maire_name: Optional[str],
        additional_context: Optional[str]
    ) -> str:
        """Build detailed prompt for Claude to generate French administrative application"""

        # Extract project data
        project_data = project.project_data or {}
        project_title = project_data.get('title') or project_data.get('name') or 'Projet à définir'
        project_description = project_data.get('description') or ''
        project_tier = project_data.get('tier') or 'standard'
        project_difficulty = project_data.get('difficulty') or 'moyenne'
        first_steps = project_data.get('first_steps') or project_data.get('firstSteps') or []
        funding_sources = project_data.get('funding_sources') or project_data.get('fundingSources') or []
        inspired_by = project_data.get('inspired_by') or project_data.get('inspiredBy') or ''
        case_study = project_data.get('case_study') or project_data.get('caseStudy') or ''

        # Phase E Week 2.5: Enhanced project data fields
        location_address = project_data.get('location_address') or ''
        project_area_m2 = project_data.get('project_area_m2')
        beneficiaries_count = project_data.get('beneficiaries_count')

        # Budget breakdown
        budget_breakdown = project_data.get('budget_breakdown') or {}
        budget_infrastructure = budget_breakdown.get('infrastructure', 0)
        budget_equipment = budget_breakdown.get('equipment', 0)
        budget_studies = budget_breakdown.get('studies', 0)
        budget_communication = budget_breakdown.get('communication', 0)
        budget_other = budget_breakdown.get('other', 0)

        # Secured funding
        secured_funding = project_data.get('secured_funding') or []

        # Planning details
        planned_start_date = project_data.get('planned_start_date') or ''
        planned_end_date = project_data.get('planned_end_date') or ''
        milestones = project_data.get('milestones') or []
        required_permits = project_data.get('required_permits') or []
        partners = project_data.get('partners') or []
        stakeholders = project_data.get('stakeholders') or ''

        # Context details
        village_area_km2 = project_data.get('village_area_km2')
        challenges_addressed = project_data.get('challenges_addressed') or []
        past_similar_projects = project_data.get('past_similar_projects') or ''
        available_resources = project_data.get('available_resources') or ''

        # Budget
        budget_min = project.budget_estimated_min or project_data.get('budget_min') or project_data.get('budgetMin') or 0
        budget_max = project.budget_estimated_max or project_data.get('budget_max') or project_data.get('budgetMax') or 0
        timeline = project.timeline_months or project_data.get('timeline_months') or project_data.get('timelineMonths') or 12

        # Location info
        location_str = village_name
        if village_department:
            location_str += f" ({village_department})"
        if village_region:
            location_str += f", {village_region}"

        # Format first steps
        first_steps_str = '\n'.join([f"  - {step}" for step in first_steps]) if first_steps else "À définir"

        # Format funding sources
        funding_str = '\n'.join([f"  - {source}" for source in funding_sources]) if funding_sources else "À identifier"

        # Format budget breakdown if provided
        budget_breakdown_str = ""
        if any([budget_infrastructure, budget_equipment, budget_studies, budget_communication, budget_other]):
            budget_breakdown_str = f"""
• Répartition du budget :
  - Travaux / Infrastructure : {budget_infrastructure:,}€
  - Équipements : {budget_equipment:,}€
  - Études et ingénierie : {budget_studies:,}€
  - Communication : {budget_communication:,}€
  - Autres dépenses : {budget_other:,}€"""

        # Format secured funding
        secured_funding_str = ""
        if secured_funding:
            secured_items = [f"  - {f.get('source', 'Source')}: {f.get('amount', 0):,}€ ({f.get('status', 'En cours')})" for f in secured_funding]
            secured_funding_str = f"\n• Financements déjà sécurisés :\n" + '\n'.join(secured_items)

        # Format milestones
        milestones_str = ""
        if milestones:
            milestone_items = [f"  - {m.get('name', 'Étape')}: {m.get('date', 'À définir')}" for m in milestones]
            milestones_str = f"\n• Jalons clés :\n" + '\n'.join(milestone_items)

        # Format partners
        partners_str = ""
        if partners:
            partners_str = f"\n• Partenaires identifiés : {', '.join(partners)}"

        # Format permits
        permits_str = ""
        if required_permits:
            permits_str = f"\n• Autorisations requises : {', '.join(required_permits)}"

        # Format challenges
        challenges_str = ""
        if challenges_addressed:
            challenge_labels = {
                'depopulation': 'Dépopulation rurale',
                'aging_population': 'Vieillissement de la population',
                'lack_of_services': 'Manque de services',
                'digital_divide': 'Fracture numérique',
                'economic_decline': 'Déclin économique',
                'environmental': 'Enjeux environnementaux',
                'mobility': 'Problèmes de mobilité',
                'heritage_preservation': 'Préservation du patrimoine'
            }
            formatted_challenges = [challenge_labels.get(c, c) for c in challenges_addressed]
            challenges_str = f"\n• Défis territoriaux adressés : {', '.join(formatted_challenges)}"

        return f"""Tu es un expert en rédaction de dossiers de demande de subvention pour les petites communes françaises rurales.
Tu maîtrises parfaitement le français administratif et les codes des collectivités territoriales.

═══════════════════════════════════════════════════════════════
COMMUNE DEMANDEUSE
═══════════════════════════════════════════════════════════════
• Nom : {village_name}
• Population : {village_population:,} habitants
• Localisation : {location_str}
{f"• Superficie : {village_area_km2} km²" if village_area_km2 else ""}
• Maire : {maire_name or "[Nom du Maire à compléter]"}
• Type : Commune rurale de petite taille
{challenges_str}
{f"• Projets similaires passés : {past_similar_projects}" if past_similar_projects else ""}
{f"• Ressources disponibles : {available_resources}" if available_resources else ""}

═══════════════════════════════════════════════════════════════
PROJET À FINANCER
═══════════════════════════════════════════════════════════════
• Titre : {project_title}
• Description : {project_description or "À développer selon le contexte"}
{f"• Adresse / Localisation précise : {location_address}" if location_address else ""}
{f"• Surface concernée : {project_area_m2:,} m²" if project_area_m2 else ""}
{f"• Nombre de bénéficiaires estimé : {beneficiaries_count:,} personnes" if beneficiaries_count else ""}
• Catégorie : {project_tier}
• Difficulté estimée : {project_difficulty}
• Budget prévisionnel : {budget_min:,}€ à {budget_max:,}€{budget_breakdown_str}{secured_funding_str}
• Durée estimée : {timeline} mois
{f"• Date de début prévue : {planned_start_date}" if planned_start_date else ""}
{f"• Date de fin prévue : {planned_end_date}" if planned_end_date else ""}{milestones_str}
• Premières étapes envisagées :
{first_steps_str}{partners_str}
{f"• Parties prenantes : {stakeholders}" if stakeholders else ""}{permits_str}
• Sources de financement potentielles :
{funding_str}
{f"• Inspiré par : {inspired_by}" if inspired_by else ""}
{f"• Étude de cas similaire : {case_study}" if case_study else ""}

═══════════════════════════════════════════════════════════════
PROGRAMME DE FINANCEMENT CIBLÉ
═══════════════════════════════════════════════════════════════
• Nom : {program.name}
• Organisme : {program.organization}
• Niveau : {program.level or 'National'}
• Montant : {program.amount_min:,}€ à {program.amount_max:,}€
• Taux de financement : {program.funding_percentage_min or '?'}% à {program.funding_percentage_max or '?'}%
• Description : {program.description or 'Non précisée'}
• Exigences : {program.requirements or 'Voir règlement du programme'}
• Documents requis : {program.required_documents or 'Voir règlement du programme'}

{f"═══════════════════════════════════════════════════════════════{chr(10)}CONTEXTE ADDITIONNEL{chr(10)}═══════════════════════════════════════════════════════════════{chr(10)}{additional_context}" if additional_context else ""}

═══════════════════════════════════════════════════════════════
MISSION
═══════════════════════════════════════════════════════════════
Rédige un dossier de demande de subvention COMPLET et PROFESSIONNEL en français administratif.
UTILISE TOUTES LES DONNÉES FOURNIES CI-DESSUS - ne pas inventer de chiffres si des données réelles sont disponibles.

STRUCTURE OBLIGATOIRE DU DOSSIER :

1. LETTRE D'ACCOMPAGNEMENT (1 page)
   - En-tête avec coordonnées de la mairie
   - Objet précis
   - Corps de lettre formel
   - Formule de politesse administrative

2. NOTE DE PRÉSENTATION DE LA COMMUNE (1-2 pages)
   - Situation géographique et administrative
   - Données démographiques et évolution
   - Caractéristiques du territoire
   - Enjeux et défis actuels (utilise les défis mentionnés ci-dessus)

3. PRÉSENTATION DÉTAILLÉE DU PROJET (3-4 pages)
   - Contexte et genèse du projet
   - Objectifs généraux et spécifiques
   - Description technique détaillée
   - Public bénéficiaire (utilise le nombre fourni si disponible)
   - Résultats attendus et indicateurs

4. COHÉRENCE AVEC LE PROGRAMME {program.name.upper()} (1-2 pages)
   - Alignement avec les priorités du programme
   - Réponse aux critères d'éligibilité
   - Plus-value territoriale

5. PLAN DE FINANCEMENT PRÉVISIONNEL (tableau)
   - Dépenses détaillées par poste (utilise la répartition fournie)
   - Recettes et co-financements (intègre les financements sécurisés)
   - Part d'autofinancement
   - Montant sollicité

6. CALENDRIER DE RÉALISATION (tableau)
   - Phases du projet (utilise les jalons fournis)
   - Échéances clés (dates de début/fin)
   - Livrables

7. PARTENARIATS ET GOUVERNANCE
   - Présentation des partenaires (si mentionnés)
   - Modalités de pilotage
   - Implication des parties prenantes

8. ANNEXES À JOINDRE (liste)
   - Documents administratifs requis
   - Pièces justificatives
   - Autorisations nécessaires (mentionner les permis requis)

═══════════════════════════════════════════════════════════════
CONSIGNES DE RÉDACTION
═══════════════════════════════════════════════════════════════
• Utilise un français administratif formel et professionnel
• Emploie le "nous" institutionnel pour la commune
• UTILISE LES DONNÉES RÉELLES fournies (budget, dates, partenaires, etc.)
• Argumente solidement avec des données concrètes
• Mets en valeur les enjeux territoriaux ruraux
• Démontre l'impact positif sur la vie locale
• Justifie le besoin de financement externe
• Montre la capacité de la commune à mener le projet
• Aligne le projet avec les objectifs du programme
• Utilise des formulations administratives courantes :
  - "La commune de {village_name} a l'honneur de..."
  - "Le présent projet s'inscrit dans..."
  - "Ce projet permettra de..."
  - "Nous sollicitons votre bienveillant soutien..."

Commence directement par la LETTRE D'ACCOMPAGNEMENT, sans préambule ni explication."""

    def regenerate_section(
        self,
        db: Session,
        application_id: int,
        section_name: str,
        instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """Regenerate a specific section of an application"""
        
        application = db.query(GrantApplication).filter(
            GrantApplication.id == application_id
        ).first()
        
        if not application:
            raise ValueError(f"Application {application_id} not found")

        prompt = f"""Voici un dossier de demande de subvention existant :

{application.generated_content}

═══════════════════════════════════════════════════════════════
MISSION : Réécris UNIQUEMENT la section "{section_name}"
═══════════════════════════════════════════════════════════════
{f"Instructions supplémentaires : {instructions}" if instructions else ""}

Améliore cette section en la rendant plus percutante et professionnelle.
Conserve le même format et le même niveau de détail.
Retourne UNIQUEMENT la nouvelle version de cette section."""

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return {
            'section': section_name,
            'new_content': message.content[0].text
        }

    def research_eligibility(
        self,
        db: Session,
        project_id: int,
        program_id: int
    ) -> Dict[str, Any]:
        """
        Generate AI-powered eligibility research for a grant application.

        Analyzes the project against funding program requirements to produce:
        - Eligibility assessment
        - Key requirements summary
        - Recommended approach
        - Potential challenges
        """
        # Get project and program
        project = db.query(ProjectInstance).filter(ProjectInstance.id == project_id).first()
        program = db.query(FundingProgram).filter(FundingProgram.id == program_id).first()

        if not project:
            raise ValueError(f"Project {project_id} not found")
        if not program:
            raise ValueError(f"Funding program {program_id} not found")

        # Extract project data
        project_data = project.project_data or {}
        project_title = project_data.get('title') or project_data.get('name') or 'Projet à définir'
        project_description = project_data.get('description') or ''
        project_themes = project_data.get('themes') or []
        budget_min = project.budget_estimated_min or project_data.get('budget_min') or 0
        budget_max = project.budget_estimated_max or project_data.get('budget_max') or 0
        timeline = project.timeline_months or project_data.get('timeline_months') or 12

        # Get village info if available
        village = None
        if project.village_id:
            village = db.query(Village).filter(Village.id == project.village_id).first()

        village_name = village.name if village else project_data.get('village_name', 'Commune')
        village_population = village.population if village else project_data.get('village_population', 0)

        prompt = f"""Tu es un expert en subventions publiques françaises pour les petites communes rurales.
Analyse l'éligibilité de ce projet au programme de financement ci-dessous.

═══════════════════════════════════════════════════════════════
PROJET À ANALYSER
═══════════════════════════════════════════════════════════════
• Titre : {project_title}
• Description : {project_description or "Non précisée"}
• Thématiques : {', '.join(project_themes) if project_themes else "Non définies"}
• Budget estimé : {budget_min:,}€ à {budget_max:,}€
• Durée : {timeline} mois
• Commune : {village_name} ({village_population:,} habitants)

═══════════════════════════════════════════════════════════════
PROGRAMME DE FINANCEMENT
═══════════════════════════════════════════════════════════════
• Nom : {program.name}
• Organisme : {program.organization}
• Niveau : {program.level or 'National'}
• Montant finançable : {program.amount_min or 0:,}€ à {program.amount_max or 0:,}€
• Taux de financement : {program.funding_percentage_min or '?'}% à {program.funding_percentage_max or '?'}%
• Type d'appel : {program.deadline_type or 'Non précisé'}
• Description : {program.description or 'Non précisée'}
• Exigences : {program.requirements or 'Non précisées'}
• Documents requis : {program.required_documents or 'Non précisés'}
• Thématiques éligibles : {', '.join(program.eligible_themes) if program.eligible_themes else 'Non précisées'}
• Populations éligibles : {', '.join(program.eligible_population_bands) if program.eligible_population_bands else 'Toutes'}

═══════════════════════════════════════════════════════════════
MISSION
═══════════════════════════════════════════════════════════════
Produis une analyse d'éligibilité DÉTAILLÉE et PROFESSIONNELLE en français.

STRUCTURE OBLIGATOIRE :

## 1. Score d'éligibilité
Donne un score de 0 à 100% et justifie-le.

## 2. Points forts du dossier
Liste les éléments qui jouent en faveur de la candidature.

## 3. Points de vigilance
Liste les risques ou faiblesses potentiels.

## 4. Analyse des critères
Pour chaque critère du programme, indique si le projet répond :
- ✅ Critère rempli
- ⚠️ Critère partiellement rempli
- ❌ Critère non rempli

## 5. Recommandations stratégiques
Conseils pour maximiser les chances de succès.

## 6. Documents à préparer
Liste priorisée des pièces à rassembler.

## 7. Prochaines étapes
Actions concrètes à mener dans l'ordre.

Sois précis, factuel et utile. Ne survends pas si l'éligibilité est faible."""

        # Call Claude API
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return {
            'research_content': message.content[0].text,
            'project_id': project_id,
            'program_id': program_id,
            'project_title': project_title,
            'program_name': program.name
        }

    def generate_draft(
        self,
        db: Session,
        project_id: int,
        program_id: int,
        research_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate an AI-powered draft for a grant application.

        Creates a structured, professional application draft based on:
        - Project information
        - Funding program requirements
        - Optional research notes from previous analysis
        """
        # Get project and program
        project = db.query(ProjectInstance).filter(ProjectInstance.id == project_id).first()
        program = db.query(FundingProgram).filter(FundingProgram.id == program_id).first()

        if not project:
            raise ValueError(f"Project {project_id} not found")
        if not program:
            raise ValueError(f"Funding program {program_id} not found")

        # Extract project data
        project_data = project.project_data or {}
        project_title = project_data.get('title') or project_data.get('name') or 'Projet à définir'
        project_description = project_data.get('description') or ''
        project_themes = project_data.get('themes') or []
        first_steps = project_data.get('first_steps') or project_data.get('firstSteps') or []
        budget_min = project.budget_estimated_min or project_data.get('budget_min') or 0
        budget_max = project.budget_estimated_max or project_data.get('budget_max') or 0
        timeline = project.timeline_months or project_data.get('timeline_months') or 12

        # Get village info
        village = None
        if project.village_id:
            village = db.query(Village).filter(Village.id == project.village_id).first()

        village_name = village.name if village else project_data.get('village_name', '[Commune]')
        village_population = village.population if village else project_data.get('village_population', 0)
        village_region = village.region if village else project_data.get('village_region', '')

        # Calculate funding amount
        average_budget = (budget_min + budget_max) // 2 if budget_min or budget_max else 0
        funding_pct = program.funding_percentage_max or 50
        amount_requested = int(average_budget * funding_pct / 100)

        prompt = f"""Tu es un expert en rédaction de dossiers de demande de subvention pour les petites communes françaises rurales.
Tu dois générer un DOSSIER DE CANDIDATURE COMPLET et PERSUASIF, pas un simple template.

═══════════════════════════════════════════════════════════════
PROJET
═══════════════════════════════════════════════════════════════
• Titre : {project_title}
• Description : {project_description or "Projet de développement local"}
• Thématiques : {', '.join(project_themes) if project_themes else "Développement rural"}
• Budget : {budget_min:,}€ à {budget_max:,}€
• Durée : {timeline} mois
• Premières étapes : {', '.join(first_steps) if first_steps else "Études préalables, consultation entreprises"}

═══════════════════════════════════════════════════════════════
COMMUNE
═══════════════════════════════════════════════════════════════
• Nom : {village_name}
• Population : {village_population:,} habitants
• Région : {village_region or "France rurale"}

═══════════════════════════════════════════════════════════════
PROGRAMME DE FINANCEMENT
═══════════════════════════════════════════════════════════════
• Nom : {program.name}
• Organisme : {program.organization}
• Montant finançable : {program.amount_min or 0:,}€ à {program.amount_max or 0:,}€
• Taux : {program.funding_percentage_min or '?'}% à {program.funding_percentage_max or '?'}%
• Exigences : {program.requirements or "Voir règlement"}
• Documents requis : {program.required_documents or "Délibération, devis, RIB"}

• Montant demandé estimé : {amount_requested:,}€

{f'''═══════════════════════════════════════════════════════════════
NOTES DE RECHERCHE PRÉALABLE
═══════════════════════════════════════════════════════════════
{research_notes}
''' if research_notes else ''}

═══════════════════════════════════════════════════════════════
MISSION CRITIQUE
═══════════════════════════════════════════════════════════════

GÉNÈRE UN DOSSIER COMPLET ET CONVAINCANT avec du contenu réel, pas des placeholders.

RÈGLES STRICTES :
1. ÉCRIS DES PARAGRAPHES NARRATIFS COMPLETS - pas de listes à puces vides
2. INVENTE des détails réalistes et cohérents basés sur le contexte
3. UTILISE "[À COMPLÉTER]" UNIQUEMENT pour : numéros SIRET, téléphone, email, adresses précises, noms de personnes
4. RÉDIGE des arguments persuasifs pour justifier le financement
5. INCLUS des chiffres réalistes estimés (bénéficiaires, emplois, visiteurs)

STRUCTURE OBLIGATOIRE avec CONTENU RÉDIGÉ :

# 1. EN-TÊTE DU DOSSIER
Rédige avec : nom commune, "Demande de subvention {program.name}", date

# 2. OBJET DE LA DEMANDE (2 paragraphes minimum)
- Présentation claire du projet
- Montant sollicité et justification

# 3. PRÉSENTATION DE LA COMMUNE (3-4 paragraphes)
- Écris une vraie description géographique et historique (invente des détails plausibles)
- Contexte démographique avec tendances réalistes
- Enjeux économiques et sociaux de la commune rurale

# 4. DESCRIPTION DÉTAILLÉE DU PROJET (5-6 paragraphes)
- Contexte et genèse : RACONTE une histoire, pourquoi ce projet est né
- Objectifs précis avec indicateurs chiffrés
- Description technique des travaux/actions
- Public bénéficiaire avec estimations chiffrées
- Impact attendu sur le territoire

# 5. PLAN DE FINANCEMENT (tableaux avec chiffres)
- Tableau des dépenses AVEC montants estimés réalistes
- Tableau des recettes incluant la subvention demandée
- Justification de la capacité d'autofinancement

# 6. CALENDRIER DE RÉALISATION (tableau avec dates)
- Phases précises avec durées estimées
- Points de contrôle et livrables

# 7. INDICATEURS DE RÉSULTATS
- Indicateurs quantitatifs CHIFFRÉS
- Modalités d'évaluation concrètes

# 8. PIÈCES À JOINDRE
- Liste cochée des documents requis

IMPORTANT : Le dossier doit être prêt à l'emploi, persuasif, et nécessiter uniquement de remplir les données administratives (SIRET, contacts). Le reste doit être du contenu rédigé et argumenté."""

        # Call Claude API
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=6000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return {
            'draft_content': message.content[0].text,
            'project_id': project_id,
            'program_id': program_id,
            'project_title': project_title,
            'program_name': program.name,
            'amount_requested': amount_requested
        }
