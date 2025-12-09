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
            project_instance_id=project_id,
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
