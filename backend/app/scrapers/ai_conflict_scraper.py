#!/usr/bin/env python3
"""
AI-Led Conflict Event Scraper
Claude AI directs search strategy for comprehensive conflict research.

Architecture:
  Phase 1: Initial Discovery (broad conflict searches)
  Phase 2: AI Query Generation (Claude analyzes & generates period-specific queries)
  Phase 3: Execute AI-Generated Queries
  Phase 4: AI Validation (Claude checks if data sufficient)
  Phase 5: Iterative Refinement (follow-up queries if needed)
  Phase 6: Final Processing (structured ConflictEvent extraction)

Conflict Types: battles, sieges, skirmishes, raids, occupations, bombardments
Time Periods: Ancient, Medieval, Renaissance, Revolutionary, Napoleonic, WW1, WW2, Modern

Output: Structured ConflictEvent objects with:
  - Basic info (name, date, location, coordinates)
  - Details (conflict_type, participants, casualties, outcome)
  - Metadata (sources, confidence_score)
  - Impact (6-category framework: infrastructure, economy, identity, demographics, governance, tourism)

Cost: ~$1.50-2.00 per region
Quality: 85-90% completeness with AI-directed search
"""

import os
import sys
import time
import json
import re
import requests
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
from urllib.parse import quote
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("Warning: beautifulsoup4 not installed", file=sys.stderr)

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("Warning: anthropic not installed", file=sys.stderr)


class AIConflictScraper:
    """
    AI-Led Conflict Event Scraper.
    Claude AI directs search strategy for comprehensive conflict research.
    """

    # Conflict type templates for different periods
    CONFLICT_TYPES = [
        'bataille', 'battle', 'battaglie',
        'siège', 'siege', 'assedio',
        'escarmouche', 'skirmish', 'scaramuccia',
        'raid', 'incursion', 'razzia',
        'occupation', 'occupazione',
        'bombardement', 'bombardment', 'bombardamento'
    ]

    PERIOD_TEMPLATES = {
        'ancient': {
            'years': 'avant 500',
            'keywords': ['romain', 'gaulois', 'celte', 'antiquité', 'légion'],
            'example_queries': [
                '{location} bataille romaine',
                '{location} siège gaulois',
                '{location} voie romaine conflit'
            ]
        },
        'medieval': {
            'years': '500-1500',
            'keywords': ['médiéval', 'château', 'croisade', 'guerre cent ans', 'féodal'],
            'example_queries': [
                '{location} bataille médiévale',
                '{location} siège château',
                '{location} Guerre de Cent Ans',
                '{location} croisade cathare'
            ]
        },
        'renaissance': {
            'years': '1500-1700',
            'keywords': ['Renaissance', 'guerres religion', 'huguenot', 'catholique'],
            'example_queries': [
                '{location} guerres de religion',
                '{location} bataille huguenots',
                '{location} siège 16e siècle'
            ]
        },
        'revolutionary': {
            'years': '1789-1799',
            'keywords': ['Révolution', 'vendéen', 'chouannerie', 'Terreur'],
            'example_queries': [
                '{location} bataille Révolution française',
                '{location} guerre de Vendée',
                '{location} chouannerie',
                '{location} Terreur 1793'
            ]
        },
        'napoleonic': {
            'years': '1799-1815',
            'keywords': ['Napoléon', 'Empire', 'Grande Armée', 'campagne'],
            'example_queries': [
                '{location} bataille napoléonienne',
                '{location} campagne Napoléon',
                '{location} Grande Armée'
            ]
        },
        'ww1': {
            'years': '1914-1918',
            'keywords': ['Première Guerre mondiale', 'Grande Guerre', 'tranchées', 'Verdun'],
            'example_queries': [
                '{location} Première Guerre mondiale',
                '{location} bataille 1914-1918',
                '{location} front 1916',
                '{location} tranchées Grande Guerre'
            ]
        },
        'ww2': {
            'years': '1939-1945',
            'keywords': ['Seconde Guerre mondiale', 'Résistance', 'occupation', 'libération', 'débarquement'],
            'example_queries': [
                '{location} Seconde Guerre mondiale',
                '{location} bataille 1944',
                '{location} occupation allemande',
                '{location} Résistance',
                '{location} libération 1944'
            ]
        },
        'modern': {
            'years': '1945-présent',
            'keywords': ['guerre d\'Algérie', 'guerre froide', 'conflit moderne'],
            'example_queries': [
                '{location} guerre d\'Algérie',
                '{location} conflit après-guerre'
            ]
        }
    }

    IMPACT_CATEGORIES = {
        'infrastructure': [
            'détruit', 'ruine', 'reconstruction', 'pont', 'route', 'bâtiment',
            'destroyed', 'ruins', 'rebuilt', 'bridge', 'road', 'building'
        ],
        'economy': [
            'économie', 'commerce', 'industrie', 'agriculture', 'pauvreté', 'richesse',
            'economy', 'trade', 'industry', 'agriculture', 'poverty', 'wealth'
        ],
        'identity': [
            'mémoire', 'monument', 'commémorat', 'identité', 'héritage', 'culture',
            'memory', 'monument', 'commemoration', 'identity', 'heritage', 'culture'
        ],
        'demographics': [
            'population', 'migration', 'exode', 'déportation', 'réfugié', 'victime',
            'population', 'migration', 'exodus', 'deportation', 'refugee', 'victim'
        ],
        'governance': [
            'gouvernement', 'administration', 'frontière', 'territoire', 'politique',
            'government', 'administration', 'border', 'territory', 'political'
        ],
        'tourism': [
            'tourisme', 'musée', 'visiteur', 'site historique', 'patrimoine',
            'tourism', 'museum', 'visitor', 'historical site', 'heritage'
        ]
    }

    def __init__(self, google_api_key: str = None, google_cse_id: str = None,
                 anthropic_api_key: str = None, delay: float = 2.0):
        """Initialize AI-led conflict scraper."""
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (historical research bot)'
        })

        # Google API
        self.google_api_key = google_api_key or os.environ.get('GOOGLE_API_KEY')
        self.google_cse_id = google_cse_id or os.environ.get('GOOGLE_CSE_ID')
        self.google_available = bool(self.google_api_key and self.google_cse_id)

        if not self.google_available:
            print("⚠️  WARNING: Google API not configured!")
            print("Set GOOGLE_API_KEY and GOOGLE_CSE_ID")

        # Claude API
        self.anthropic_api_key = anthropic_api_key or os.environ.get('ANTHROPIC_API_KEY')
        if self.anthropic_api_key and ANTHROPIC_AVAILABLE:
            self.claude_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
            self.claude_available = True
        else:
            self.claude_client = None
            self.claude_available = False
            print("⚠️  WARNING: Claude API not configured!")

        # Tracking
        self.search_count = 0
        self.url_count = 0
        self.claude_calls = 0
        self.start_time = None
        self.all_text = []
        self.phase_results = {}
        self.ai_generated_queries = []
        self.follow_up_queries = []

        # Limits
        self.max_total_searches = 60
        self.max_iterations = 2
        self.max_processing_time = 900  # 15 minutes

    def scrape_conflicts_ai_led(self, location_name: str, latitude: float = None,
                               longitude: float = None, department: str = None,
                               region: str = None, radius_km: float = 50) -> Dict:
        """
        AI-Led conflict scraping with iterative refinement.

        Args:
            location_name: Location name (town, city, region)
            latitude: GPS latitude
            longitude: GPS longitude
            department: Department name
            region: Region name
            radius_km: Search radius in kilometers

        Returns:
            Comprehensive conflict intelligence with structured ConflictEvent objects
        """
        self.start_time = time.time()
        self.search_count = 0
        self.url_count = 0
        self.claude_calls = 0
        self.all_text = []
        self.phase_results = {}
        self.ai_generated_queries = []
        self.follow_up_queries = []

        print(f"\n{'='*80}")
        print(f"⚔️  AI-LED CONFLICT SCRAPING: {location_name}")
        print(f"{'='*80}\n")

        result = {
            'location_name': location_name,
            'department': department,
            'region': region,
            'latitude': latitude,
            'longitude': longitude,
            'radius_km': radius_km,
            'scraping_timestamp': datetime.utcnow().isoformat(),
            'scraping_method': 'AI-led conflict scraper',
            'phases': {},
            'stats': {},
            'conflicts': []
        }

        # ================================================================
        # PHASE 1: INITIAL DISCOVERY
        # ================================================================
        print(f"{'='*80}")
        print("PHASE 1: INITIAL CONFLICT DISCOVERY")
        print(f"{'='*80}\n")

        initial_data = self._phase1_initial_discovery(location_name, department, region)
        self.phase_results['phase1'] = initial_data
        result['phases']['phase1_initial_discovery'] = {
            'searches': len(initial_data.get('searches', [])),
            'text_collected': sum(len(t) for t in initial_data.get('texts', []))
        }

        if not self.claude_available:
            print("\n⚠️  Claude API not available. Cannot proceed with AI-led search.")
            result['status'] = 'claude_unavailable'
            return result

        # ================================================================
        # PHASE 2: AI QUERY GENERATION
        # ================================================================
        print(f"\n{'='*80}")
        print("PHASE 2: AI CONFLICT QUERY GENERATION")
        print(f"{'='*80}\n")

        query_generation = self._phase2_ai_query_generation(
            location_name,
            department,
            region,
            initial_data
        )
        self.phase_results['phase2'] = query_generation
        self.ai_generated_queries = query_generation.get('search_queries', [])

        result['phases']['phase2_ai_query_generation'] = {
            'analysis': query_generation.get('analysis', ''),
            'periods_identified': query_generation.get('periods_identified', []),
            'queries_generated': len(self.ai_generated_queries),
            'queries': self.ai_generated_queries
        }

        print(f"   Generated {len(self.ai_generated_queries)} AI-targeted conflict queries")

        # ================================================================
        # PHASE 3: EXECUTE AI-GENERATED QUERIES
        # ================================================================
        print(f"\n{'='*80}")
        print("PHASE 3: EXECUTE AI-GENERATED CONFLICT QUERIES")
        print(f"{'='*80}\n")

        targeted_data = self._phase3_execute_ai_queries(self.ai_generated_queries)
        self.phase_results['phase3'] = targeted_data

        result['phases']['phase3_targeted_search'] = {
            'queries_executed': len(targeted_data.get('results', [])),
            'text_collected': sum(len(t) for t in targeted_data.get('texts', []))
        }

        # ================================================================
        # PHASE 4 & 5: AI VALIDATION & ITERATIVE REFINEMENT
        # ================================================================
        iteration = 0
        while iteration < self.max_iterations and self.search_count < self.max_total_searches:
            print(f"\n{'='*80}")
            print(f"PHASE 4: AI VALIDATION (Iteration {iteration + 1})")
            print(f"{'='*80}\n")

            # Combine all data collected so far
            all_collected_data = self._compile_all_data()

            validation = self._phase4_ai_validation(
                location_name,
                department,
                region,
                all_collected_data
            )

            self.phase_results[f'phase4_iteration_{iteration + 1}'] = validation

            result['phases'][f'phase4_validation_iter_{iteration + 1}'] = {
                'sufficient': validation.get('sufficient', False),
                'missing_aspects': validation.get('missing_aspects', []),
                'follow_up_queries': validation.get('follow_up_queries', [])
            }

            if validation.get('sufficient', False):
                print(f"   ✅ Conflict data sufficient! Proceeding to final processing.")
                break

            # Phase 5: Execute follow-up queries
            follow_ups = validation.get('follow_up_queries', [])
            if not follow_ups:
                print(f"   ⚠️  Data insufficient but no follow-up queries generated. Stopping.")
                break

            print(f"\n{'='*80}")
            print(f"PHASE 5: ITERATIVE REFINEMENT (Iteration {iteration + 1})")
            print(f"{'='*80}\n")
            print(f"   Executing {len(follow_ups)} follow-up queries...")

            follow_up_data = self._phase3_execute_ai_queries(follow_ups)
            self.phase_results[f'phase5_iteration_{iteration + 1}'] = follow_up_data

            result['phases'][f'phase5_refinement_iter_{iteration + 1}'] = {
                'queries_executed': len(follow_up_data.get('results', [])),
                'text_collected': sum(len(t) for t in follow_up_data.get('texts', []))
            }

            iteration += 1

        # ================================================================
        # PHASE 6: FINAL PROCESSING
        # ================================================================
        print(f"\n{'='*80}")
        print("PHASE 6: FINAL CONFLICT EVENT EXTRACTION")
        print(f"{'='*80}\n")

        final_text = self._compile_all_text()
        print(f"   Total text collected: {len(final_text):,} chars")

        conflicts = self._phase6_final_processing(
            location_name,
            department,
            region,
            latitude,
            longitude,
            final_text
        )

        result['conflicts'] = conflicts
        result['conflict_count'] = len(conflicts)

        result['phases']['phase6_final_processing'] = {
            'total_text_chars': len(final_text),
            'conflicts_extracted': len(conflicts)
        }

        # Final stats
        result['stats'] = {
            'total_searches': self.search_count,
            'urls_fetched': self.url_count,
            'claude_api_calls': self.claude_calls,
            'total_text_chars': len(final_text),
            'iterations': iteration,
            'processing_time_seconds': int(time.time() - self.start_time)
        }

        print(f"\n{'='*80}")
        print("✅ AI-LED CONFLICT SCRAPING COMPLETE")
        print(f"{'='*80}")
        print(f"Searches: {self.search_count}")
        print(f"Claude calls: {self.claude_calls}")
        print(f"Text: {len(final_text):,} chars")
        print(f"Iterations: {iteration}")
        print(f"Conflicts found: {len(conflicts)}")

        return result

    # ========================================================================
    # PHASE 1: INITIAL DISCOVERY
    # ========================================================================

    def _phase1_initial_discovery(self, location: str, department: str = None,
                                  region: str = None) -> Dict:
        """Phase 1: Initial broad conflict searches."""
        print("⚔️  Phase 1: Initial Conflict Discovery...")

        # Build location context
        location_parts = [location]
        if department:
            location_parts.append(department)
        location_str = ', '.join(location_parts)

        searches = [
            f"bataille {location_str}",
            f"siège {location_str}",
            f"{location_str} guerre",
            f"{location_str} conflit historique",
            f"{location_str} Seconde Guerre mondiale",
            f"{location_str} Révolution française",
            f"bataille près de {location}",
            f"{location_str} histoire militaire"
        ]

        results = []
        texts = []

        for query in searches:
            if self.search_count >= self.max_total_searches:
                break

            print(f"   → {query}")
            search_results = self._google_search(query, num_results=4)
            results.append({
                'query': query,
                'results': search_results
            })

            # Extract texts
            for res in search_results:
                if res.get('content'):
                    texts.append(res['content'])

            time.sleep(self.delay)

        # Wikipedia
        wiki = self._fetch_wikipedia_conflicts(location, department)
        if wiki.get('content'):
            texts.append(wiki['content'])

        self.all_text.extend(texts)

        return {
            'searches': results,
            'wikipedia': wiki,
            'texts': texts
        }

    # ========================================================================
    # PHASE 2: AI QUERY GENERATION
    # ========================================================================

    def _phase2_ai_query_generation(self, location: str, department: str = None,
                                   region: str = None, initial_data: Dict = None) -> Dict:
        """Phase 2: Claude generates conflict-specific targeted queries."""
        print("🤖 Phase 2: AI Conflict Query Generation...")

        # Combine initial texts
        preliminary_text = '\n\n'.join(initial_data.get('texts', []))[:25000]

        prompt = f"""You are a French military history expert specializing in conflict research.

Task: Analyze preliminary data about conflicts near {location}, {department or ''} and generate targeted search queries.

Preliminary Data:
{preliminary_text}

CONFLICT TYPES TO SEARCH:
- Battles (batailles)
- Sieges (sièges)
- Skirmishes (escarmouches)
- Raids (raids, incursions)
- Occupations (occupations)
- Bombardments (bombardements)

HISTORICAL PERIODS TO COVER:
- Ancient (Roman, Gallic conflicts)
- Medieval (feudal wars, Hundred Years War, crusades)
- Renaissance (Wars of Religion, 16th-17th century)
- Revolutionary (1789-1799)
- Napoleonic (1799-1815)
- WW1 (1914-1918)
- WW2 (1939-1945, especially Resistance, occupation, liberation)
- Modern (post-1945)

Your job:
1. Identify conflicts already mentioned in preliminary data
2. Identify which historical periods are relevant to this location
3. Generate 12-16 SPECIFIC search queries to find:
   - Specific battle/siege names with dates
   - Military units involved (regiments, divisions, armies)
   - Key commanders and participants
   - Strategic importance of location
   - Casualties and outcomes
   - Impact on surrounding area
   - Modern commemoration (monuments, museums)

Requirements:
- Use PROPER NOUNS from preliminary text (battle names, commander names, unit names)
- Be SPECIFIC not generic (e.g., "bataille Chirac 1944 libération" NOT "bataille Chirac")
- Include dates when relevant (e.g., "Charente Révolution 1793")
- Use French military terms (régiment, division, front, ligne Maginot, débarquement)
- Target each major conflict type and period relevant to this location

Return ONLY valid JSON:
{{
  "analysis": "Brief 2-3 sentence analysis of conflicts mentioned in preliminary data and which periods/types need more research",
  "periods_identified": ["period1", "period2", ...],
  "search_queries": [
    "specific query 1",
    "specific query 2",
    ...12-16 queries total
  ]
}}

Example for location "Charente" if preliminary data mentions:
- WW2 liberation but no specifics
- Revolutionary period activity
- Medieval fortifications

Good queries would be:
"bataille Charente juin 1944 libération"
"Charente Révolution française 1793 vendéens"
"siège châteaux Charente guerre Cent Ans"
"Charente Résistance maquis"
"bombardement Angoulême 1944"
"Charente passage Grande Armée 1808"

Return ONLY the JSON, no other text."""

        try:
            self.claude_calls += 1
            response = self.claude_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=3000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text

            # Parse JSON
            json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response_text

            result = json.loads(json_str)

            print(f"   ✅ Claude analysis: {result.get('analysis', 'N/A')[:150]}...")
            print(f"   ✅ Periods identified: {', '.join(result.get('periods_identified', []))}")
            print(f"   ✅ Generated {len(result.get('search_queries', []))} conflict queries")

            for i, query in enumerate(result.get('search_queries', [])[:5], 1):
                print(f"      {i}. {query}")

            if len(result.get('search_queries', [])) > 5:
                print(f"      ... and {len(result.get('search_queries', [])) - 5} more")

            return result

        except Exception as e:
            print(f"   ❌ Error in AI query generation: {e}")
            return {
                'analysis': 'Error in query generation',
                'periods_identified': [],
                'search_queries': [],
                'error': str(e)
            }

    # ========================================================================
    # PHASE 3: EXECUTE AI-GENERATED QUERIES
    # ========================================================================

    def _phase3_execute_ai_queries(self, queries: List[str]) -> Dict:
        """Phase 3: Execute AI-generated conflict queries."""
        print(f"🔍 Phase 3: Executing {len(queries)} AI-generated conflict queries...")

        results = []
        texts = []

        for query in queries:
            if self.search_count >= self.max_total_searches:
                print(f"   ⚠️  Reached search limit ({self.max_total_searches})")
                break

            print(f"   → {query}")
            search_results = self._google_search(query, num_results=5)

            results.append({
                'query': query,
                'results': search_results
            })

            # Extract texts
            for res in search_results:
                if res.get('content'):
                    texts.append(res['content'])

            time.sleep(self.delay)

        self.all_text.extend(texts)

        return {
            'results': results,
            'texts': texts
        }

    # ========================================================================
    # PHASE 4: AI VALIDATION
    # ========================================================================

    def _phase4_ai_validation(self, location: str, department: str = None,
                             region: str = None, all_data: str = None) -> Dict:
        """Phase 4: Claude validates conflict data completeness."""
        print("🔍 Phase 4: AI Conflict Validation...")

        # Limit text for validation
        validation_text = all_data[:60000]

        prompt = f"""You are validating conflict research completeness for {location}, {department or ''}.

All Data Collected:
{validation_text}

Questions:
1. Have we found sufficient conflict data across all major historical periods?
2. Are there specific conflicts mentioned but lacking critical details (dates, participants, casualties, outcomes)?
3. Are there historical periods that should have conflicts but we haven't found any data?

Requirements for data sufficiency:
- Multiple conflict types identified (battles, sieges, raids, occupations, etc.) OR confirmed peaceful history
- Key conflicts have: name, date (at least year), location, participants, basic outcome
- Coverage of major periods relevant to this location:
  * Medieval conflicts (if fortifications/châteaux mentioned)
  * Wars of Religion (if 16th-17th century activity)
  * Revolutionary period (1789-1799)
  * Napoleonic era (1799-1815)
  * WW1 (1914-1918, if near front lines)
  * WW2 (1939-1945, especially occupation/liberation)
- Modern impact identified (monuments, commemoration, tourism, local identity)

If data sufficient for comprehensive conflict analysis: Return {{"sufficient": true, "follow_up_queries": null}}
If critical information missing: Return {{"sufficient": false, "follow_up_queries": ["query1", "query2", "query3"]}}

Return ONLY valid JSON:
{{
  "sufficient": true or false,
  "missing_aspects": ["aspect1", "aspect2"] or null,
  "follow_up_queries": ["specific query 1", "specific query 2"] or null,
  "reasoning": "Explain why data is sufficient OR what critical gaps remain"
}}

IMPORTANT:
- If sufficient=false, provide 2-5 SPECIFIC follow-up queries
- Use proper nouns from the data (battle names, commander names, dates)
- Focus on filling the most critical gaps

Return ONLY the JSON."""

        try:
            self.claude_calls += 1
            response = self.claude_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text

            # Parse JSON
            json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response_text

            result = json.loads(json_str)

            print(f"   Sufficient: {result.get('sufficient', False)}")
            print(f"   Reasoning: {result.get('reasoning', 'N/A')[:200]}...")

            if not result.get('sufficient', False):
                follow_ups = result.get('follow_up_queries', [])
                print(f"   Follow-up queries: {len(follow_ups)}")
                for i, q in enumerate(follow_ups, 1):
                    print(f"      {i}. {q}")

            return result

        except Exception as e:
            print(f"   ❌ Error in AI validation: {e}")
            return {
                'sufficient': True,  # Assume sufficient on error
                'missing_aspects': None,
                'follow_up_queries': None,
                'reasoning': f'Error in validation: {e}',
                'error': str(e)
            }

    # ========================================================================
    # PHASE 6: FINAL PROCESSING
    # ========================================================================

    def _phase6_final_processing(self, location: str, department: str = None,
                                 region: str = None, latitude: float = None,
                                 longitude: float = None, all_text: str = None) -> List[Dict]:
        """Phase 6: Extract structured ConflictEvent objects."""
        print("📊 Phase 6: Final Conflict Event Extraction...")

        # Limit text
        final_text = all_text[:120000]

        prompt = f"""Analyze ALL collected data about conflicts near {location}, {department or ''} and extract structured ConflictEvent objects.

ALL COLLECTED DATA:
{final_text}

EXTRACT structured ConflictEvent objects with MAXIMUM DETAIL:

For EACH distinct conflict event found:
1. Basic Information:
   - name: Official or commonly used name (e.g., "Bataille de Chirac", "Libération d'Angoulême")
   - date: Best available date (YYYY-MM-DD, YYYY-MM, or YYYY)
   - date_precision: "day", "month", "year", or "circa"
   - location: Specific location name
   - coordinates: {{lat, lng}} if mentioned or can be inferred

2. Conflict Details:
   - conflict_type: "battle", "siege", "skirmish", "raid", "occupation", "bombardment", or "other"
   - period: "ancient", "medieval", "renaissance", "revolutionary", "napoleonic", "ww1", "ww2", "modern"
   - participants: Array of {{name, side, role}} for armies, units, commanders
   - casualties: {{side1: number, side2: number, civilians: number}} or "unknown"
   - outcome: "victory_side1", "victory_side2", "stalemate", "unknown" with brief description
   - duration: "1 day", "2 weeks", "3 months", etc. if known

3. Context:
   - strategic_importance: Why this location? (crossroads, fortification, resources, etc.)
   - preceding_events: What led to this conflict?
   - consequences: Immediate and long-term results

4. Sources & Confidence:
   - sources: Array of source descriptions (books, websites, archives mentioned)
   - confidence_score: 0-100 based on source quality and detail level
     * 90-100: Multiple reliable sources, specific details, dates, commanders
     * 70-89: Good sources, most key details present
     * 50-69: Limited sources or missing key details
     * Below 50: Vague mentions, folklore, unverified

5. Impact Today (6-category framework):
   - infrastructure: Current physical remains, destroyed buildings, reconstruction
   - economy: Economic effects then and now, tourism revenue, commemorations
   - identity: Role in local/national identity, memory, education
   - demographics: Population changes, migrations, deportations, casualties
   - governance: Political boundaries, administrative changes, territory control
   - tourism: Museums, monuments, commemorative sites, visitor numbers

Return STRICT JSON array format:
[
  {{
    "name": "string",
    "date": "YYYY-MM-DD or YYYY-MM or YYYY",
    "date_precision": "day|month|year|circa",
    "location": "string",
    "coordinates": {{"lat": float, "lng": float}} or null,
    "conflict_type": "battle|siege|skirmish|raid|occupation|bombardment|other",
    "period": "ancient|medieval|renaissance|revolutionary|napoleonic|ww1|ww2|modern",
    "participants": [
      {{"name": "string", "side": "string", "role": "string"}},
      ...
    ],
    "casualties": {{"side1": int, "side2": int, "civilians": int}} or "unknown",
    "outcome": "string",
    "duration": "string" or null,
    "strategic_importance": "string",
    "preceding_events": "string" or null,
    "consequences": "string",
    "sources": ["source1", "source2", ...],
    "confidence_score": int (0-100),
    "impact_today": {{
      "infrastructure": "string describing physical remains, destruction, reconstruction",
      "economy": "string describing economic impacts then and tourism now",
      "identity": "string describing role in collective memory and identity",
      "demographics": "string describing population impacts",
      "governance": "string describing political/administrative impacts",
      "tourism": "string describing current commemorative tourism"
    }}
  }},
  ... more conflicts
]

IMPORTANT:
- Extract ALL distinct conflict events mentioned
- Use proper nouns (commander names, unit names, specific dates)
- Be specific in impact_today descriptions (mention specific monuments, museums, annual commemorations)
- If a detail is not mentioned, use null or "unknown" rather than inventing
- Confidence score should reflect source quality and completeness

Return ONLY the JSON array, no other text."""

        try:
            self.claude_calls += 1
            response = self.claude_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=16000,
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text

            # Parse JSON
            json_match = re.search(r'```(?:json)?\s*(\[.*\])\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find array without code blocks
                json_str = response_text.strip()

            conflicts = json.loads(json_str)

            print(f"   ✅ Extracted {len(conflicts)} conflict events")

            # Print summary
            for i, conflict in enumerate(conflicts[:5], 1):
                print(f"      {i}. {conflict.get('name', 'Unknown')} ({conflict.get('date', 'Unknown date')}) - Confidence: {conflict.get('confidence_score', 0)}/100")

            if len(conflicts) > 5:
                print(f"      ... and {len(conflicts) - 5} more")

            return conflicts

        except json.JSONDecodeError as e:
            print(f"   ❌ JSON parsing error: {e}")
            print(f"   Response preview: {response_text[:500]}...")
            return []
        except Exception as e:
            print(f"   ❌ Error in final processing: {e}")
            return []

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _google_search(self, query: str, num_results: int = 5) -> List[Dict]:
        """Execute Google Custom Search API call."""
        if not self.google_available:
            return []

        try:
            self.search_count += 1
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.google_api_key,
                'cx': self.google_cse_id,
                'q': query,
                'num': min(num_results, 10)
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get('items', []):
                result = {
                    'title': item.get('title', ''),
                    'url': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'query': query
                }

                # Fetch content
                if self.url_count < 150:  # Hard limit
                    content = self._fetch_url(result['url'])
                    if content:
                        result['content'] = content
                        self.url_count += 1

                results.append(result)

            return results

        except Exception as e:
            print(f"      ✗ Search error: {e}")
            return []

    def _fetch_url(self, url: str, max_length: int = 6000) -> Optional[str]:
        """Fetch and extract text from URL."""
        if not BS4_AVAILABLE:
            return None

        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove noise
            for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                tag.decompose()

            text = soup.get_text()
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            text = '\n'.join(lines)

            return text[:max_length]

        except:
            return None

    def _fetch_wikipedia_conflicts(self, location: str, department: str = None) -> Dict:
        """Fetch Wikipedia page about location (may contain conflict info)."""
        attempts = [
            location,
            f"{location}_(commune)",
            f"{location}_(bataille)",
            f"Bataille_de_{location}",
            f"Siège_de_{location}",
        ]

        if department:
            attempts.extend([
                f"{location}_({department})",
                f"Bataille_de_{location}_{department}"
            ])

        for attempt in attempts:
            try:
                time.sleep(self.delay)
                api_url = "https://fr.wikipedia.org/w/api.php"
                params = {
                    'action': 'query',
                    'format': 'json',
                    'titles': attempt,
                    'prop': 'extracts',
                    'explaintext': True
                }

                response = self.session.get(api_url, params=params, timeout=15)
                data = response.json()

                pages = data.get('query', {}).get('pages', {})
                for page_id, page_data in pages.items():
                    if page_id != '-1':
                        content = page_data.get('extract', '')
                        if len(content) > 500:
                            return {
                                'status': 'success',
                                'page_title': attempt,
                                'content': content
                            }

            except:
                continue

        return {'status': 'not_found'}

    def _compile_all_data(self) -> str:
        """Compile all collected text for validation."""
        return '\n\n'.join(self.all_text)

    def _compile_all_text(self) -> str:
        """Compile all text with deduplication."""
        unique_texts = []
        seen = set()

        for text in self.all_text:
            text_hash = hash(text[:150])
            if text_hash not in seen:
                seen.add(text_hash)
                unique_texts.append(text)

        return '\n\n'.join(unique_texts)


def main():
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser(
        description='AI-Led Conflict Event Scraper with Iterative Refinement',
        epilog="""
Example:
  python ai_conflict_scraper.py --location "Chirac" --department "Charente" --region "Nouvelle-Aquitaine" --lat 45.75 --lng 0.8

Expected output:
  - Structured ConflictEvent objects with complete metadata
  - 6-category impact_today framework
  - Confidence scores based on source quality
  - Coverage across all relevant historical periods

Cost: ~$1.50-2.00/region
Quality: 85-90% completeness with AI-directed search
        """
    )

    parser.add_argument('--location', required=True, help='Location name (town, city, region)')
    parser.add_argument('--department', help='Department name')
    parser.add_argument('--region', help='Region name')
    parser.add_argument('--lat', type=float, help='Latitude')
    parser.add_argument('--lng', type=float, help='Longitude')
    parser.add_argument('--radius', type=float, default=50, help='Search radius in km (default: 50)')
    parser.add_argument('--google-key', help='Google API key')
    parser.add_argument('--google-cse', help='Google CSE ID')
    parser.add_argument('--claude-key', help='Claude API key')
    parser.add_argument('--output', help='Output JSON file')
    parser.add_argument('--delay', type=float, default=2.0, help='Delay between searches (default: 2.0s)')

    args = parser.parse_args()

    scraper = AIConflictScraper(
        google_api_key=args.google_key,
        google_cse_id=args.google_cse,
        anthropic_api_key=args.claude_key,
        delay=args.delay
    )

    result = scraper.scrape_conflicts_ai_led(
        location_name=args.location,
        latitude=args.lat,
        longitude=args.lng,
        department=args.department,
        region=args.region,
        radius_km=args.radius
    )

    output_path = args.output or f"{args.location.lower()}_conflicts_ai_led.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print(f"✅ OUTPUT: {output_path}")
    print(f"{'='*80}\n")

    print(f"⚔️  Conflicts Found: {result.get('conflict_count', 0)}")
    if 'stats' in result:
        print(f"📊 Claude API calls: {result['stats'].get('claude_api_calls', 0)}")
        print(f"🔍 Total searches: {result['stats'].get('total_searches', 0)}")
        print(f"📝 Text collected: {result['stats'].get('total_text_chars', 0):,} chars")

    if result.get('conflicts'):
        print(f"\n{'='*80}")
        print("TOP CONFLICTS:")
        print(f"{'='*80}")
        for i, conflict in enumerate(result['conflicts'][:5], 1):
            print(f"{i}. {conflict.get('name', 'Unknown')}")
            print(f"   Date: {conflict.get('date', 'Unknown')}")
            print(f"   Type: {conflict.get('conflict_type', 'Unknown')}")
            print(f"   Confidence: {conflict.get('confidence_score', 0)}/100")
            print()


if __name__ == '__main__':
    main()
