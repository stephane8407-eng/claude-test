"""
Claude API Integration Service
Phase E Week 2: AI-Powered Grant Application Assistant
"""

import os
import httpx
from typing import Optional

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = "claude-sonnet-4-20250514"
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"


async def call_claude_api(prompt: str, max_tokens: int = 4000) -> str:
    """
    Call Claude API with a prompt and return the response.

    Args:
        prompt: The prompt to send to Claude
        max_tokens: Maximum tokens in response (default 4000)

    Returns:
        The text response from Claude

    Raises:
        Exception: If API call fails
    """
    if not ANTHROPIC_API_KEY:
        raise Exception("ANTHROPIC_API_KEY not configured")

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    payload = {
        "model": CLAUDE_MODEL,
        "max_tokens": max_tokens,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            CLAUDE_API_URL,
            headers=headers,
            json=payload
        )

        if response.status_code != 200:
            error_detail = response.text
            raise Exception(f"Claude API error ({response.status_code}): {error_detail}")

        data = response.json()

        # Extract text from response
        if "content" in data and len(data["content"]) > 0:
            return data["content"][0]["text"]

        raise Exception("No content in Claude API response")


def build_research_prompt(
    village_name: str,
    village_population: Optional[int],
    village_region: str,
    project_name: str,
    project_description: str,
    budget_min: Optional[int],
    budget_max: Optional[int],
    timeline_months: Optional[int],
    program_name: str,
    program_organization: str,
    amount_min: Optional[int],
    amount_max: Optional[int],
    funding_percentage_min: Optional[int],
    funding_percentage_max: Optional[int],
    requirements: Optional[str],
    eligible_themes: Optional[list],
    eligible_population_bands: Optional[list],
    required_documents: Optional[list]
) -> str:
    """Build the research phase prompt."""

    budget_str = ""
    if budget_min and budget_max:
        budget_str = f"{budget_min:,} - {budget_max:,}".replace(",", " ")
    elif budget_min:
        budget_str = f"min {budget_min:,}".replace(",", " ")
    elif budget_max:
        budget_str = f"max {budget_max:,}".replace(",", " ")
    else:
        budget_str = "Non défini"

    amount_str = ""
    if amount_min and amount_max:
        amount_str = f"{amount_min:,} - {amount_max:,}".replace(",", " ")
    elif amount_max:
        amount_str = f"jusqu'à {amount_max:,}".replace(",", " ")
    else:
        amount_str = "Variable"

    funding_str = ""
    if funding_percentage_min and funding_percentage_max:
        funding_str = f"{funding_percentage_min}% - {funding_percentage_max}%"
    elif funding_percentage_max:
        funding_str = f"jusqu'à {funding_percentage_max}%"
    else:
        funding_str = "Variable"

    themes_str = ", ".join(eligible_themes) if eligible_themes else "Non spécifié"
    pop_bands_str = ", ".join(eligible_population_bands) if eligible_population_bands else "Toutes populations"
    docs_str = "\n".join([f"- {doc}" for doc in required_documents]) if required_documents else "Non spécifié"

    return f"""Tu es un expert en demandes de subventions pour les villages français. Tu aides la commune de {village_name} à analyser une opportunité de financement.

═══════════════════════════════════════════════════════════════
CONTEXTE DU VILLAGE
═══════════════════════════════════════════════════════════════

Village: {village_name}
Population: {village_population if village_population else "Non renseignée"} habitants
Région: {village_region}
Caractéristiques: Village rural de Charente, Nouvelle-Aquitaine

═══════════════════════════════════════════════════════════════
PROJET À FINANCER
═══════════════════════════════════════════════════════════════

Nom du projet: {project_name}
Description: {project_description}
Budget estimé: {budget_str} €
Durée prévue: {timeline_months if timeline_months else "Non définie"} mois

═══════════════════════════════════════════════════════════════
PROGRAMME DE FINANCEMENT
═══════════════════════════════════════════════════════════════

Programme: {program_name}
Organisme: {program_organization}
Montant: {amount_str} €
Taux de financement: {funding_str}
Thématiques éligibles: {themes_str}
Tranches de population: {pop_bands_str}
Conditions: {requirements if requirements else "Non spécifiées"}

Documents requis:
{docs_str}

═══════════════════════════════════════════════════════════════
MISSION
═══════════════════════════════════════════════════════════════

Génère un RÉSUMÉ DE RECHERCHE complet en français avec les sections suivantes:

## ✅ Analyse d'Éligibilité
Vérifie si {village_name} remplit tous les critères d'éligibilité. Sois précis sur les critères remplis et ceux à vérifier.

## 📋 Exigences du Programme
Détaille chaque exigence du programme - ce qui est exactement demandé.

## 💡 Points Forts de {village_name}
Pourquoi CE village est idéal pour CETTE subvention - avantages spécifiques.

## ⚠️ Points d'Attention
Défis potentiels et comment les anticiper.

## 🎯 Stratégie Recommandée
Étapes concrètes pour maximiser les chances de succès.

## 📞 Contacts Clés
Qui contacter: GAL, préfecture, gestionnaires du programme.

## 📚 Conseils Pratiques
Exemples de projets similaires réussis et bonnes pratiques.

Sois spécifique, actionnable et encourageant. Écris en français clair et professionnel."""


def build_draft_prompt(
    village_name: str,
    village_population: Optional[int],
    village_region: str,
    project_name: str,
    project_description: str,
    budget_min: Optional[int],
    budget_max: Optional[int],
    timeline_months: Optional[int],
    program_name: str,
    program_organization: str,
    amount_min: Optional[int],
    amount_max: Optional[int],
    funding_percentage_min: Optional[int],
    funding_percentage_max: Optional[int],
    requirements: Optional[str],
    eligible_themes: Optional[list],
    required_documents: Optional[list],
    research_notes: Optional[str] = None
) -> str:
    """Build the application draft prompt."""

    budget_str = ""
    if budget_min and budget_max:
        budget_str = f"{budget_min:,} - {budget_max:,}".replace(",", " ")
    elif budget_min:
        budget_str = f"min {budget_min:,}".replace(",", " ")
    elif budget_max:
        budget_str = f"max {budget_max:,}".replace(",", " ")
    else:
        budget_str = "À définir"

    amount_str = ""
    if amount_min and amount_max:
        amount_str = f"{amount_min:,} - {amount_max:,}".replace(",", " ")
    elif amount_max:
        amount_str = f"jusqu'à {amount_max:,}".replace(",", " ")
    else:
        amount_str = "Variable"

    funding_str = ""
    if funding_percentage_min and funding_percentage_max:
        funding_str = f"{funding_percentage_min}% - {funding_percentage_max}%"
    elif funding_percentage_max:
        funding_str = f"jusqu'à {funding_percentage_max}%"
    else:
        funding_str = "Variable"

    themes_str = ", ".join(eligible_themes) if eligible_themes else "Non spécifié"
    docs_str = "\n".join([f"- {doc}" for doc in required_documents]) if required_documents else "Non spécifié"

    research_section = ""
    if research_notes:
        research_section = f"""
═══════════════════════════════════════════════════════════════
NOTES DE LA PHASE DE RECHERCHE
═══════════════════════════════════════════════════════════════

{research_notes}
"""

    return f"""Tu es un rédacteur expert en demandes de subventions pour les villages français. Tu aides {village_name} à rédiger sa candidature pour le programme "{program_name}".

═══════════════════════════════════════════════════════════════
CONTEXTE DU VILLAGE
═══════════════════════════════════════════════════════════════

Village: {village_name}
Population: {village_population if village_population else "Non renseignée"} habitants
Région: {village_region}
Caractéristiques: Village rural de Charente, Nouvelle-Aquitaine

═══════════════════════════════════════════════════════════════
PROJET À FINANCER
═══════════════════════════════════════════════════════════════

Nom du projet: {project_name}
Description: {project_description}
Budget estimé: {budget_str} €
Durée prévue: {timeline_months if timeline_months else "Non définie"} mois

═══════════════════════════════════════════════════════════════
PROGRAMME CIBLÉ
═══════════════════════════════════════════════════════════════

Programme: {program_name}
Organisme: {program_organization}
Montant: {amount_str} €
Taux de financement: {funding_str}
Thématiques: {themes_str}
Conditions: {requirements if requirements else "Non spécifiées"}

Documents requis:
{docs_str}
{research_section}
═══════════════════════════════════════════════════════════════
MISSION
═══════════════════════════════════════════════════════════════

Génère un BROUILLON DE CANDIDATURE complet en français avec:

## 📖 Présentation du Projet
Récit convaincant - pourquoi ce projet est important pour {village_name}.

## 💰 Budget Détaillé
Justifie chaque poste de dépense majeur - pourquoi c'est nécessaire.
Propose une répartition réaliste basée sur le budget estimé.

## 📅 Calendrier et Jalons
Planning mois par mois avec les étapes clés.

## 🎯 Impact sur le Village
Bénéfices spécifiques et mesurables pour la communauté.
- Impact social
- Impact économique
- Impact environnemental (si applicable)

## 📎 Documents à Préparer
Pour chaque document requis:
- Nom du document
- Où l'obtenir
- Détails spécifiques à inclure
- Délais à respecter

## ✍️ Conseils de Rédaction
Astuces spécifiques pour CE programme - ce que les évaluateurs recherchent.

## 📋 Checklist Avant Soumission
Tout ce qu'il faut vérifier avant d'envoyer.

## 📞 Plan de Suivi
Comment et quand relancer après la soumission.

Rédige de façon persuasive mais honnête. Sois spécifique à {village_name} et au programme {program_name}."""
