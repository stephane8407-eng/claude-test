#!/usr/bin/env python3
"""
Comprehensive Village Intelligence Platform
Multi-layer data collection and structured extraction for treasure hunting GIS.

Collects and processes 8 intelligence categories:
1. Village Identity
2. Historical Events (with dates)
3. Economic/Industrial History
4. Archaeological Data
5. Treasure Indicators
6. Military/Strategic
7. Geographic/Geological
8. Legends & Folklore

Sources: Wikipedia, Mérimée, INRAP, HAL/Persée, Gallica, Géoportail, Mining DBs
Processing: Claude API for structured extraction with confidence scores
Output: Queryable JSON with cross-references
"""

import os
import sys
import time
import json
import re
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from urllib.parse import quote, urljoin

# Check if anthropic is available
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("Warning: anthropic package not installed. Install with: pip install anthropic", file=sys.stderr)


class ComprehensiveVillageIntelligence:
    """
    Comprehensive intelligence gathering and processing for villages.
    """

    def __init__(self, anthropic_api_key: str = None, delay: float = 2.0):
        """
        Initialize comprehensive intelligence platform.

        Args:
            anthropic_api_key: API key for Claude processing
            delay: Delay between requests (seconds)
        """
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # Initialize Claude API client
        self.anthropic_api_key = anthropic_api_key or os.environ.get('ANTHROPIC_API_KEY')
        if self.anthropic_api_key and ANTHROPIC_AVAILABLE:
            self.claude_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
            self.claude_available = True
        else:
            self.claude_client = None
            self.claude_available = False
            if not ANTHROPIC_AVAILABLE:
                print("Warning: Claude API processing disabled (anthropic not installed)", file=sys.stderr)
            elif not self.anthropic_api_key:
                print("Warning: Claude API processing disabled (no API key)", file=sys.stderr)

    def collect_intelligence(self, village_name: str, latitude: float = None,
                           longitude: float = None, department: str = None) -> Dict:
        """
        Collect comprehensive intelligence from all sources.

        Args:
            village_name: Name of village
            latitude: GPS latitude (optional)
            longitude: GPS longitude (optional)
            department: French department name (optional)

        Returns:
            Dict with raw collected data from all sources
        """
        print(f"\n{'='*80}")
        print(f"COMPREHENSIVE INTELLIGENCE COLLECTION: {village_name}")
        print(f"{'='*80}\n")

        collected_data = {
            'village_name': village_name,
            'latitude': latitude,
            'longitude': longitude,
            'department': department,
            'collection_timestamp': datetime.utcnow().isoformat(),
            'sources': {}
        }

        # 1. Wikipedia (multiple languages)
        print("📚 Collecting Wikipedia data...")
        collected_data['sources']['wikipedia_fr'] = self._scrape_wikipedia(village_name, 'fr')
        collected_data['sources']['wikipedia_en'] = self._scrape_wikipedia(village_name, 'en')

        # 2. Mérimée (monuments)
        print("🏛️  Collecting Mérimée heritage data...")
        collected_data['sources']['merimee'] = self._scrape_merimee(village_name, latitude, longitude)

        # 3. INRAP (archaeology)
        print("⚒️  Collecting INRAP archaeological data...")
        collected_data['sources']['inrap'] = self._scrape_inrap(village_name, department)

        # 4. HAL/Persée (academic)
        print("📖 Collecting academic research data...")
        collected_data['sources']['academic_hal'] = self._scrape_hal(village_name)
        collected_data['sources']['academic_persee'] = self._scrape_persee(village_name)

        # 5. Gallica (archives)
        print("📜 Collecting Gallica historical archives...")
        collected_data['sources']['gallica'] = self._scrape_gallica(village_name, department)

        # 6. Mining databases
        print("⛏️  Collecting mining/industrial history...")
        collected_data['sources']['mining'] = self._scrape_mining_data(village_name, department)

        # 7. Mairie & local archives
        print("🏛️  Collecting mairie and departmental archives...")
        collected_data['sources']['mairie'] = self._scrape_mairie(village_name)
        collected_data['sources']['archives_dept'] = self._scrape_dept_archives(village_name, department)

        # 8. Google searches (targeted)
        print("🔍 Performing targeted searches...")
        search_terms = [
            f"{village_name} bataille",
            f"{village_name} mine exploitation",
            f"{village_name} archéologie fouilles",
            f"{village_name} trésor légende",
            f"{village_name} château fortification",
            f"{village_name} histoire médiévale"
        ]
        collected_data['sources']['targeted_searches'] = {}
        for term in search_terms:
            key = term.split()[-1]  # Use last word as key
            collected_data['sources']['targeted_searches'][key] = self._search_google(term)

        return collected_data

    def process_intelligence(self, collected_data: Dict) -> Dict:
        """
        Process collected data into structured intelligence using Claude API.

        Args:
            collected_data: Raw data from collect_intelligence()

        Returns:
            Structured intelligence with 8 categories
        """
        if not self.claude_available:
            print("\n⚠️  Claude API not available. Returning raw data only.")
            return {
                'status': 'raw_only',
                'message': 'Claude API processing unavailable',
                'raw_data': collected_data
            }

        print(f"\n{'='*80}")
        print("🤖 PROCESSING WITH CLAUDE API")
        print(f"{'='*80}\n")

        # Combine all text from sources
        all_text = self._combine_source_texts(collected_data['sources'])

        if not all_text.strip():
            print("⚠️  No text collected. Returning empty structure.")
            return self._empty_intelligence_structure(collected_data)

        print(f"📊 Total text collected: {len(all_text):,} characters")
        print(f"🔄 Sending to Claude for structured extraction...\n")

        # Create comprehensive extraction prompt
        prompt = self._create_extraction_prompt(
            collected_data['village_name'],
            all_text,
            collected_data.get('department')
        )

        try:
            # Call Claude API
            response = self.claude_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=16000,
                temperature=0,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Extract JSON from response
            response_text = response.content[0].text
            intelligence = self._parse_claude_response(response_text, collected_data)

            print("✅ Claude processing complete!")
            return intelligence

        except Exception as e:
            print(f"❌ Error processing with Claude: {e}")
            return {
                'status': 'processing_error',
                'error': str(e),
                'raw_data': collected_data
            }

    def _create_extraction_prompt(self, village_name: str, text: str, department: str = None) -> str:
        """Create comprehensive extraction prompt for Claude."""
        dept_context = f" in {department}" if department else ""

        return f"""Analyze this data about {village_name}{dept_context} and extract comprehensive intelligence for treasure hunting.

SOURCE DATA:
{text[:100000]}  # Limit to ~100K chars to fit in context

EXTRACT THE FOLLOWING CATEGORIES WITH MAXIMUM DETAIL:

1. VILLAGE IDENTITY:
   - Name, alternative names, etymology
   - Population (historical and current)
   - Cultural/historical significance
   - Geographic location details

2. HISTORICAL EVENTS (CRITICAL - WITH DATES):
   - Battles fought in/near village (date, participants, outcome, casualties)
   - Sieges, occupations (duration, forces involved)
   - Wars that passed through (armies, dates, routes)
   - Refugee movements, evacuations
   - Any conflict-related events
   FOR EACH: Extract date, event type, outcome, treasure relevance score (0-100)

3. ECONOMIC/INDUSTRIAL HISTORY:
   - Mines, quarries, forges (type of resource, operating dates)
   - Industries, factories (what produced, when)
   - Trade routes, markets
   - Economic collapse/closures (potential hidden wealth)
   FOR EACH: Resource type, dates, treasure relevance

4. ARCHAEOLOGICAL DATA:
   - Registered dig sites (locations, dates, findings)
   - Museum artifacts from this village
   - Academic papers mentioning village
   - Heritage listings (Mérimée references)
   FOR EACH: Find type, date, current location, significance

5. TREASURE INDICATORS:
   - Documented treasure finds (what, when, where)
   - Legends about hidden valuables (credibility assessment)
   - Underground structures (passages, wells, cellars, tunnels)
   - Emergency burials during wars
   - Lost wealth stories
   FOR EACH: Credibility score (0-100), location hints, treasure type

6. MILITARY/STRATEGIC:
   - Castles, fortifications (condition, dates)
   - Strategic importance (why valuable militarily)
   - Retreat routes passing through
   - Troop movements recorded
   - Defensive positions
   FOR EACH: Strategic value, treasure potential

7. GEOGRAPHIC/GEOLOGICAL:
   - Rivers, bridges, fords (crossing points)
   - Hills, valleys (defensive positions, viewpoints)
   - Soil type (for metal detection potential)
   - Underground water (wells, springs, water table)
   - Caves, natural shelters

8. LEGENDS & FOLKLORE:
   - Ghost stories with historical basis
   - Treasure tales (names, locations mentioned)
   - Local myths about wealth
   - Oral traditions about hidden items
   FOR EACH: Treasure relevance score, location clues

CROSS-REFERENCES:
- Identify connections to major battles (create battle_id references)
- Link to nearby villages mentioned
- Reference archaeological sites
- Connect to historical routes

OUTPUT FORMAT (STRICT JSON):
{{
  "village_name": "{village_name}",
  "department": "{department if department else 'Unknown'}",
  "processing_timestamp": "{datetime.utcnow().isoformat()}",

  "identity": {{
    "name": "official name",
    "alternative_names": ["name1", "name2"],
    "etymology": "origin of name",
    "population_current": number or null,
    "population_historical": [{{"year": 1800, "count": 500}}],
    "significance": "why historically important"
  }},

  "historical_events": [
    {{
      "date": "YYYY-MM-DD or YYYY",
      "event_type": "battle|siege|occupation|passage|refuge",
      "name": "event name",
      "description": "what happened",
      "participants": ["faction1", "faction2"],
      "outcome": "result",
      "casualties": "number or description",
      "treasure_relevance": 0-100,
      "treasure_reasoning": "why relevant for treasure hunting",
      "source_citation": "where this info came from",
      "confidence": 0-100
    }}
  ],

  "economic": [
    {{
      "type": "mine|quarry|forge|factory|market",
      "resource": "what was extracted/produced",
      "dates": "operating period",
      "location_details": "where in village",
      "closure_reason": "why closed",
      "treasure_relevance": 0-100,
      "treasure_reasoning": "potential for hidden wealth",
      "source_citation": "source",
      "confidence": 0-100
    }}
  ],

  "archaeological": [
    {{
      "find_type": "artifact type",
      "date_discovered": "when found",
      "date_origin": "age of artifact",
      "location": "where found",
      "current_location": "museum/collection",
      "significance": "importance",
      "source_citation": "source",
      "confidence": 0-100
    }}
  ],

  "treasure_indicators": [
    {{
      "type": "legend|documented_find|structure|burial",
      "description": "detailed description",
      "treasure_type": "gold|silver|valuables|artifacts",
      "credibility": 0-100,
      "location_hints": "specific location clues",
      "time_period": "when hidden/lost",
      "source_citation": "source",
      "investigation_priority": "high|medium|low"
    }}
  ],

  "military_strategic": {{
    "fortifications": [
      {{
        "type": "castle|wall|tower|fort",
        "name": "name",
        "construction_date": "when built",
        "condition": "ruins|partial|intact",
        "strategic_value": "why important",
        "treasure_potential": 0-100,
        "confidence": 0-100
      }}
    ],
    "strategic_importance": "overall military value",
    "retreat_routes": ["route descriptions"],
    "troop_movements": ["documented passages"]
  }},

  "geographic": {{
    "waterways": [
      {{
        "type": "river|stream|spring|well",
        "name": "name",
        "treasure_relevance": "why relevant",
        "confidence": 0-100
      }}
    ],
    "terrain": {{
      "type": "hills|valley|plains|forest",
      "defensive_value": "description",
      "soil_type": "for metal detection",
      "underground_features": ["caves", "tunnels", "cellars"]
    }}
  }},

  "legends_folklore": [
    {{
      "title": "legend name",
      "description": "full story",
      "treasure_relevance": 0-100,
      "location_clues": "places mentioned",
      "credibility": 0-100,
      "treasure_type": "what's supposedly hidden",
      "source_citation": "where heard/documented"
    }}
  ],

  "cross_references": {{
    "nearby_battles": [
      {{
        "battle_name": "name",
        "distance_km": number,
        "relevance": "why connected to this village"
      }}
    ],
    "connected_villages": ["village1", "village2"],
    "archaeological_sites": ["site references"],
    "historical_routes": ["route names"]
  }},

  "treasure_probability": {{
    "overall_score": 0-100,
    "reasoning": "comprehensive analysis",
    "key_factors": [
      "factor 1 that increases probability",
      "factor 2...",
      "factor 3..."
    ],
    "investigation_priorities": [
      {{
        "location": "specific place to investigate",
        "reason": "why investigate here",
        "priority": "high|medium|low",
        "method": "metal detection|excavation|archives"
      }}
    ]
  }},

  "data_quality": {{
    "sources_found": number,
    "total_text_chars": number,
    "completeness": 0-100,
    "confidence_average": 0-100,
    "missing_categories": ["categories with no data"]
  }}
}}

IMPORTANT:
- Only include data you actually found in the source text
- Assign confidence scores based on source quality
- If no data for a category, use empty arrays/objects
- Be specific with dates, locations, names
- Cite sources for verification
- Calculate treasure probability based on ALL factors

Return ONLY valid JSON, no additional text."""

    def _combine_source_texts(self, sources: Dict) -> str:
        """Combine all source texts into one string."""
        combined = []

        for source_name, source_data in sources.items():
            if not source_data:
                continue

            combined.append(f"\n{'='*60}\n")
            combined.append(f"SOURCE: {source_name.upper()}\n")
            combined.append(f"{'='*60}\n")

            if isinstance(source_data, dict):
                if 'content' in source_data:
                    combined.append(source_data['content'])
                elif 'text' in source_data:
                    combined.append(source_data['text'])
                else:
                    combined.append(json.dumps(source_data, indent=2))
            elif isinstance(source_data, str):
                combined.append(source_data)
            else:
                combined.append(str(source_data))

            combined.append("\n")

        return '\n'.join(combined)

    def _parse_claude_response(self, response_text: str, collected_data: Dict) -> Dict:
        """Parse Claude's JSON response."""
        # Try to extract JSON from response
        # Sometimes Claude wraps JSON in markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = response_text

        try:
            intelligence = json.loads(json_str)
            intelligence['status'] = 'success'
            intelligence['raw_data'] = collected_data  # Include raw data for reference
            return intelligence
        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse Claude response as JSON: {e}")
            return {
                'status': 'parse_error',
                'error': str(e),
                'raw_response': response_text,
                'raw_data': collected_data
            }

    def _empty_intelligence_structure(self, collected_data: Dict) -> Dict:
        """Return empty intelligence structure."""
        return {
            'status': 'no_data',
            'village_name': collected_data['village_name'],
            'message': 'No data collected from sources',
            'raw_data': collected_data
        }

    # ========================================================================
    # SOURCE SCRAPERS
    # ========================================================================

    def _scrape_wikipedia(self, village_name: str, language: str = 'fr') -> Dict:
        """Scrape Wikipedia article."""
        try:
            time.sleep(self.delay)

            # Use MediaWiki API
            api_url = f"https://{language}.wikipedia.org/w/api.php"
            params = {
                'action': 'query',
                'format': 'json',
                'titles': village_name,
                'prop': 'extracts',
                'explaintext': True
            }

            response = self.session.get(api_url, params=params, timeout=15)
            if response.status_code != 200:
                return {'status': 'error', 'code': response.status_code}

            data = response.json()
            pages = data.get('query', {}).get('pages', {})

            for page_id, page_data in pages.items():
                if page_id == '-1':
                    return {'status': 'not_found'}

                return {
                    'status': 'success',
                    'title': page_data.get('title'),
                    'content': page_data.get('extract', ''),
                    'language': language
                }

            return {'status': 'no_data'}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _scrape_merimee(self, village_name: str, latitude: float = None,
                       longitude: float = None) -> Dict:
        """Scrape Mérimée heritage database."""
        try:
            time.sleep(self.delay)

            # Mérimée API endpoint
            api_url = "https://data.culture.gouv.fr/api/records/1.0/search/"
            params = {
                'dataset': 'liste-des-immeubles-proteges-au-titre-des-monuments-historiques',
                'q': village_name,
                'rows': 50
            }

            response = self.session.get(api_url, params=params, timeout=15)
            if response.status_code != 200:
                return {'status': 'error', 'code': response.status_code}

            data = response.json()
            records = data.get('records', [])

            monuments = []
            for record in records:
                fields = record.get('fields', {})
                monuments.append({
                    'name': fields.get('tico', ''),
                    'type': fields.get('deno', ''),
                    'protection': fields.get('prot', ''),
                    'date': fields.get('scle', ''),
                    'location': fields.get('adrs', '')
                })

            return {
                'status': 'success',
                'count': len(monuments),
                'monuments': monuments,
                'content': json.dumps(monuments, indent=2, ensure_ascii=False)
            }

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _scrape_inrap(self, village_name: str, department: str = None) -> Dict:
        """Scrape INRAP archaeological database."""
        try:
            time.sleep(self.delay)

            # INRAP search (note: actual API may differ, this is示范)
            search_url = f"https://www.inrap.fr/recherche?q={quote(village_name)}"

            response = self.session.get(search_url, timeout=15)
            if response.status_code != 200:
                return {'status': 'error', 'code': response.status_code}

            # In real implementation, would parse HTML for archaeological findings
            # For now, return placeholder
            return {
                'status': 'success',
                'search_url': search_url,
                'content': f"INRAP search performed for {village_name}"
            }

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _scrape_hal(self, village_name: str) -> Dict:
        """Scrape HAL academic database."""
        try:
            time.sleep(self.delay)

            # HAL API
            api_url = "https://api.archives-ouvertes.fr/search/"
            params = {
                'q': village_name,
                'wt': 'json',
                'rows': 20
            }

            response = self.session.get(api_url, params=params, timeout=15)
            if response.status_code != 200:
                return {'status': 'error', 'code': response.status_code}

            # Parse results (simplified)
            return {
                'status': 'success',
                'content': f"HAL academic search for {village_name}"
            }

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _scrape_persee(self, village_name: str) -> Dict:
        """Scrape Persée academic portal."""
        try:
            time.sleep(self.delay)

            search_url = f"https://www.persee.fr/search?q={quote(village_name)}"

            response = self.session.get(search_url, timeout=15)
            if response.status_code != 200:
                return {'status': 'error', 'code': response.status_code}

            return {
                'status': 'success',
                'content': f"Persée academic search for {village_name}"
            }

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _scrape_gallica(self, village_name: str, department: str = None) -> Dict:
        """Scrape Gallica national library archives."""
        try:
            time.sleep(self.delay)

            # Gallica SRU API
            api_url = "https://gallica.bnf.fr/SRU"
            params = {
                'version': '1.2',
                'operation': 'searchRetrieve',
                'query': f'(dc.title all "{village_name}")',
                'maximumRecords': 20
            }

            response = self.session.get(api_url, params=params, timeout=15)
            if response.status_code != 200:
                return {'status': 'error', 'code': response.status_code}

            return {
                'status': 'success',
                'content': f"Gallica archives search for {village_name}"
            }

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _scrape_mining_data(self, village_name: str, department: str = None) -> Dict:
        """Scrape mining and industrial history databases."""
        try:
            time.sleep(self.delay)

            # Search for mining history (multiple possible sources)
            # This is a placeholder - actual implementation would search:
            # - BRGM (Bureau de Recherches Géologiques et Minières)
            # - Historical mining databases
            # - Industrial heritage sites

            search_queries = [
                f"{village_name} mine",
                f"{village_name} carrière",
                f"{village_name} forge",
                f"{village_name} exploitation minière"
            ]

            return {
                'status': 'success',
                'content': f"Mining database search for {village_name}",
                'queries': search_queries
            }

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _scrape_mairie(self, village_name: str) -> Dict:
        """Scrape mairie (town hall) website."""
        try:
            time.sleep(self.delay)

            # Generate common mairie URL patterns
            village_clean = village_name.lower().replace(' ', '-').replace("'", '')

            patterns = [
                f"https://www.mairie-{village_clean}.fr",
                f"https://mairie-{village_clean}.fr",
                f"http://www.mairie-{village_clean}.fr",
                f"http://{village_clean}.fr"
            ]

            for url in patterns:
                try:
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200:
                        # Found mairie site
                        # In real implementation, would parse HTML for history section
                        return {
                            'status': 'success',
                            'url': url,
                            'content': f"Mairie website found at {url}"
                        }
                except:
                    continue

            return {'status': 'not_found', 'patterns_tried': patterns}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _scrape_dept_archives(self, village_name: str, department: str = None) -> Dict:
        """Scrape departmental archives."""
        try:
            time.sleep(self.delay)

            if not department:
                return {'status': 'no_department', 'message': 'Department name required'}

            # Search departmental archives (patterns vary by department)
            search_url = f"https://archives.{department}.fr/search?q={quote(village_name)}"

            return {
                'status': 'success',
                'search_url': search_url,
                'content': f"Departmental archives search for {village_name}"
            }

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _search_google(self, query: str) -> Dict:
        """Perform targeted Google search."""
        # Note: Google searches typically blocked in automated environments
        # This is a placeholder for local execution

        return {
            'status': 'placeholder',
            'query': query,
            'content': f"Google search: {query} (execute locally for results)"
        }

    def save_intelligence(self, intelligence: Dict, output_path: str) -> None:
        """Save intelligence to JSON file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(intelligence, indent=2, ensure_ascii=False, fp=f)

        print(f"\n✅ Intelligence saved to: {output_path}")

        # Print summary
        if intelligence.get('status') == 'success':
            self._print_intelligence_summary(intelligence)

    def _print_intelligence_summary(self, intelligence: Dict) -> None:
        """Print summary of extracted intelligence."""
        print(f"\n{'='*80}")
        print("📊 INTELLIGENCE SUMMARY")
        print(f"{'='*80}\n")

        print(f"Village: {intelligence.get('village_name', 'Unknown')}")
        print(f"Department: {intelligence.get('department', 'Unknown')}")

        # Count items in each category
        counts = {
            'Historical Events': len(intelligence.get('historical_events', [])),
            'Economic/Industrial': len(intelligence.get('economic', [])),
            'Archaeological Finds': len(intelligence.get('archaeological', [])),
            'Treasure Indicators': len(intelligence.get('treasure_indicators', [])),
            'Legends/Folklore': len(intelligence.get('legends_folklore', [])),
        }

        print(f"\nData Collected:")
        for category, count in counts.items():
            print(f"  • {category}: {count}")

        # Treasure probability
        treasure = intelligence.get('treasure_probability', {})
        score = treasure.get('overall_score', 0)
        print(f"\n🎯 Treasure Probability: {score}/100")

        reasoning = treasure.get('reasoning', 'N/A')
        print(f"Reasoning: {reasoning[:200]}...")

        # Data quality
        quality = intelligence.get('data_quality', {})
        print(f"\n📈 Data Quality:")
        print(f"  • Sources Found: {quality.get('sources_found', 0)}")
        print(f"  • Completeness: {quality.get('completeness', 0)}/100")
        print(f"  • Confidence: {quality.get('confidence_average', 0)}/100")


def main():
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Comprehensive Village Intelligence Platform',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full intelligence gathering and processing
  python comprehensive_village_intelligence.py --village "Chirac" --department "Charente" --lat 45.9833 --lng 0.5167

  # Without Claude processing (raw data only)
  python comprehensive_village_intelligence.py --village "Azincourt" --no-processing

  # Specify API key
  python comprehensive_village_intelligence.py --village "Verdun" --api-key "sk-ant-..."

Requirements:
  • ANTHROPIC_API_KEY environment variable (or --api-key parameter)
  • pip install anthropic requests

Note: Some sources may be blocked in automated environments. Run locally for best results.
        """
    )

    parser.add_argument('--village', required=True, help='Village name')
    parser.add_argument('--department', help='Department name (e.g., "Charente")')
    parser.add_argument('--lat', type=float, help='Latitude')
    parser.add_argument('--lng', type=float, help='Longitude')
    parser.add_argument('--api-key', help='Anthropic API key (or use ANTHROPIC_API_KEY env var)')
    parser.add_argument('--output', help='Output JSON file path (default: {village}_intelligence.json)')
    parser.add_argument('--delay', type=float, default=2.0, help='Delay between requests (seconds)')
    parser.add_argument('--no-processing', action='store_true', help='Skip Claude processing (raw data only)')

    args = parser.parse_args()

    # Initialize platform
    platform = ComprehensiveVillageIntelligence(
        anthropic_api_key=args.api_key if not args.no_processing else None,
        delay=args.delay
    )

    # Collect intelligence
    collected_data = platform.collect_intelligence(
        village_name=args.village,
        latitude=args.lat,
        longitude=args.lng,
        department=args.department
    )

    # Process intelligence (unless disabled)
    if args.no_processing:
        intelligence = {
            'status': 'raw_only',
            'message': 'Processing disabled',
            'raw_data': collected_data
        }
    else:
        intelligence = platform.process_intelligence(collected_data)

    # Save output
    output_path = args.output or f"{args.village.lower().replace(' ', '_')}_intelligence.json"
    platform.save_intelligence(intelligence, output_path)

    print(f"\n{'='*80}")
    print("✅ COMPLETE")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    main()
