#!/usr/bin/env python3
"""
EXPANDED AI Conflict Scraper: 2,500 Years of History (500 BC - 2024 AD)
Comprehensive historical conflict research across 13 major periods.

Target: 100km radius around Chirac (45.9164°N, 0.6542°E)
Major sites: Cassinomagus (Chassenon), Angoulême, Confolens, Rochechouart, Chabanais

Historical Coverage:
  1. Gallic Tribes Era (500-58 BC)
  2. Gallic Wars (58-50 BC) - Caesar's conquest
  3. Roman Gaul (50 BC - 410 AD) - Cassinomagus era
  4. Late Antiquity/Barbarian Invasions (410-800 AD)
  5. Early Medieval (800-1000) - Viking raids, feudal conflicts
  6. High Medieval (1000-1337) - Castle warfare
  7. Hundred Years War (1337-1453)
  8. Wars of Religion (1562-1598)
  9. 17th Century (1600-1700) - Fronde
  10. French Revolution (1789-1799)
  11. Napoleonic Era (1799-1815)
  12. 19th Century (1815-1914) - Franco-Prussian War
  13. World Wars (1914-1945) + Modern (1945-2024)

Expected output: 90-170 conflicts across 2,500 years
Cost: ~$2-3
Time: 4-8 hours processing
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

# Load environment variables
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


class AIConflictScraperExpanded:
    """
    EXPANDED AI Conflict Scraper covering 2,500 years (500 BC - 2024 AD).
    """

    # Expanded period templates covering 2,500 years
    PERIOD_TEMPLATES = {
        'gallic_tribes': {
            'years': '500-58 BC',
            'bc': True,
            'keywords': ['peuples gaulois', 'oppida', 'Lemovices', 'Pictons', 'Santons',
                        'celtes', 'tribu gauloise', 'guerre tribale'],
            'sites': ['oppidum', 'fortification gauloise', 'camp retranché'],
            'search_queries': [
                '{location} peuples gaulois Charente',
                '{location} oppida Lemovices Pictons',
                '{location} conflits celtes Aquitaine',
                'Lemovices territoire guerre',
                'Pictons Santons conflit tribal',
                'oppida fortifiés Charente',
                'guerre tribale gauloise Aquitaine'
            ]
        },
        'gallic_wars': {
            'years': '58-50 BC',
            'bc': True,
            'keywords': ['guerre des Gaules', 'César', 'Julius Caesar', 'Vercingetorix',
                        'légion romaine', 'résistance gauloise', 'Lemovices'],
            'sites': ['bataille', 'siège', 'oppidum'],
            'search_queries': [
                '{location} guerre des Gaules Charente',
                '{location} César Aquitaine bataille',
                '{location} Lemovices résistance romaine',
                'César conquête Aquitaine 56 BC',
                'Vercingetorix Lemovices',
                'légion romaine Charente bataille',
                'résistance gauloise Aquitaine',
                'guerre Gaules Angoulême région'
            ]
        },
        'roman_gaul': {
            'years': '50 BC - 410 AD',
            'bc_ad_mixed': True,
            'keywords': ['Cassinomagus', 'Chassenon', 'thermes romains', 'voie romaine',
                        'légion', 'camp militaire romain', 'villa romaine', 'civitas'],
            'sites': ['Cassinomagus', 'Chassenon', 'Angoulême antique', 'Confolens romain'],
            'search_queries': [
                'Cassinomagus Chassenon bataille',
                'Cassinomagus fonction militaire',
                '{location} légion romaine Charente',
                '{location} voie romaine Aquitaine conflit',
                '{location} thermes Chassenon militaire',
                'camp militaire romain Charente',
                'Angoulême antique bataille',
                'voie Saintes Bourges conflit',
                'raids barbares Aquitaine romaine',
                'révoltes gauloises empire romain Charente'
            ]
        },
        'late_antiquity': {
            'years': '410-800 AD',
            'keywords': ['Wisigoths', 'Francs', 'invasion barbare', 'royaume wisigoth',
                        'Clovis', 'royaume franc', 'migration'],
            'sites': ['bataille', 'invasion', 'établissement'],
            'search_queries': [
                '{location} invasion wisigoths Charente',
                '{location} Francs Aquitaine bataille',
                '{location} barbares Angoulême',
                'Wisigoths royaume Aquitaine conflit',
                'Clovis conquête Aquitaine',
                'bataille Francs Wisigoths Charente',
                'invasions barbares Angoulême 5e siècle',
                'chute empire romain Aquitaine'
            ]
        },
        'early_medieval': {
            'years': '800-1000 AD',
            'keywords': ['Vikings', 'Normands', 'raids vikings', 'Loire', 'château',
                        'féodal', 'comté Angoulême', 'seigneur'],
            'sites': ['château', 'forteresse', 'abbaye'],
            'search_queries': [
                '{location} raids normands Charente',
                '{location} Vikings Loire Charente',
                '{location} conflits féodaux Angoumois',
                'Vikings remontée Loire Charente',
                'raids normands Angoulême 9e siècle',
                'comté Angoulême guerre féodale',
                'châteaux forts Charente médiéval',
                'seigneurs Angoumois conflits'
            ]
        },
        'high_medieval': {
            'years': '1000-1337 AD',
            'keywords': ['château', 'siège médiéval', 'seigneur', 'Plantagenêt',
                        'Aquitaine anglaise', 'féodal', 'comté Angoulême'],
            'sites': ['château', 'forteresse', 'ville fortifiée'],
            'search_queries': [
                '{location} siège château Charente médiéval',
                '{location} guerre seigneurs Angoumois',
                '{location} Plantagenêt Aquitaine',
                'château Charente bataille médiévale',
                'comté Angoulême conflit seigneurial',
                'Aquitaine anglaise 12e siècle Charente',
                'guerre féodale Angoumois 13e siècle',
                'fortifications médiévales Charente'
            ]
        },
        'hundred_years_war': {
            'years': '1337-1453 AD',
            'keywords': ['Guerre Cent Ans', 'anglais', 'Plantagenêt', 'siège',
                        'occupation anglaise', 'bataille', 'Jean le Bon', 'Charles VII'],
            'sites': ['château', 'ville fortifiée', 'bataille'],
            'search_queries': [
                '{location} Guerre Cent Ans Charente',
                '{location} bataille Angoulême anglais',
                '{location} siège Confolens 14e siècle',
                'occupation anglaise Charente 14e',
                'Angoulême Guerre Cent Ans',
                'bataille Charente 1350-1400',
                'siège Chabanais Guerre Cent Ans',
                'Jean le Bon Aquitaine bataille'
            ]
        },
        'wars_of_religion': {
            'years': '1562-1598 AD',
            'keywords': ['guerres religion', 'protestants', 'catholiques', 'huguenots',
                        'massacre', 'siège', 'Henri IV', 'bataille'],
            'sites': ['ville assiégée', 'massacre', 'bataille'],
            'search_queries': [
                '{location} guerres religion Charente',
                '{location} bataille protestants Angoulême',
                '{location} massacre Confolens',
                'huguenots Charente 16e siècle',
                'Angoulême protestants siège',
                'guerres religion Angoumois 1570-1590',
                'bataille catholiques protestants Charente',
                'Henri IV passage Charente'
            ]
        },
        '17th_century': {
            'years': '1600-1700 AD',
            'keywords': ['Fronde', 'révolte', 'Richelieu', 'Louis XIV', 'armée royale',
                        'siège', 'troubles'],
            'sites': ['révolte', 'siège', 'bataille'],
            'search_queries': [
                '{location} Fronde Charente',
                '{location} révoltes Angoumois 17e siècle',
                'Fronde Angoulême 1650',
                'révolte paysans Charente 17e',
                'Richelieu Charente',
                'troubles Angoumois Louis XIV',
                'armée royale Charente 17e siècle'
            ]
        },
        'revolution': {
            'years': '1789-1799 AD',
            'keywords': ['Révolution française', 'guillotine', 'Terreur', 'vendéens',
                        'chouannerie', 'armée révolutionnaire', 'exécution'],
            'sites': ['guillotine', 'bataille', 'réquisition'],
            'search_queries': [
                '{location} révolution française Charente',
                '{location} guillotine Angoulême',
                '{location} Terreur Confolens',
                'Révolution Charente 1793',
                'exécutions Terreur Angoulême',
                'vendéens Charente',
                'armée révolutionnaire Angoumois',
                'réquisitions 1793 Charente'
            ]
        },
        'napoleonic': {
            'years': '1799-1815 AD',
            'keywords': ['Napoléon', 'Empire', 'Grande Armée', 'conscription',
                        'campagne', 'passage troupe'],
            'sites': ['garnison', 'passage troupe', 'cantonnement'],
            'search_queries': [
                '{location} Napoléon Charente',
                '{location} conscription Angoulême',
                'Grande Armée passage Charente',
                'Napoléon campagne Espagne Charente',
                'Empire garnison Angoulême',
                'conscrits Charente 1805-1815',
                'cantonnement troupes Angoumois Empire'
            ]
        },
        '19th_century': {
            'years': '1815-1914 AD',
            'keywords': ['guerre 1870', 'prussiens', 'Commune', 'insurrection',
                        'occupation prussienne'],
            'sites': ['bataille', 'occupation', 'garnison'],
            'search_queries': [
                '{location} guerre 1870 Charente',
                '{location} prussiens Angoulême',
                'guerre Franco-Prussienne Charente',
                'occupation prussienne Angoulême 1870',
                'bataille 1870-1871 Charente',
                'Commune Angoulême 1871',
                'mobilisation 1870 Charente'
            ]
        },
        'ww1': {
            'years': '1914-1918 AD',
            'keywords': ['Première Guerre mondiale', 'Grande Guerre', '14-18',
                        'mobilisation', 'poilus', 'monument morts'],
            'sites': ['mobilisation', 'garnison', 'hôpital militaire'],
            'search_queries': [
                '{location} 14-18 Charente',
                '{location} Grande Guerre Angoulême',
                'mobilisation 1914 Charente',
                'poilus Charente monuments',
                'hôpital militaire Angoulême 1914-1918',
                'victimes Grande Guerre Charente',
                'régiment Charente 1914-1918'
            ]
        },
        'ww2': {
            'years': '1939-1945 AD',
            'keywords': ['Seconde Guerre mondiale', 'Résistance', 'maquis', 'libération',
                        'occupation', 'bataille', 'Gestapo', 'FFI', 'FTP'],
            'sites': ['bataille', 'maquis', 'libération', 'massacre'],
            'search_queries': [
                '{location} résistance Charente maquis',
                '{location} libération Angoulême 1944',
                '{location} bataille maquis Confolens',
                '{location} occupation allemande Charente',
                'maquis FTP Charente',
                'bataille libération Charente 1944',
                'Résistance Angoumois FFI',
                'massacre Charente 1944 SS',
                'Gestapo Angoulême',
                'maquis AS Foch Charente'
            ]
        },
        'modern': {
            'years': '1945-2024 AD',
            'keywords': ['guerre Algérie', 'conflit moderne', 'commémoration'],
            'sites': ['monument', 'commémoration'],
            'search_queries': [
                '{location} guerre Algérie Charente',
                'conflit moderne Charente après-guerre'
            ]
        }
    }

    # Roman-specific sites for special focus
    ROMAN_SITES = {
        'Cassinomagus': {
            'modern_name': 'Chassenon',
            'coordinates': {'lat': 45.8528, 'lng': 0.7528},
            'type': 'thermal complex with potential military function',
            'searches': [
                'Cassinomagus bataille',
                'Cassinomagus camp militaire',
                'Chassenon thermes romains fonction militaire',
                'Cassinomagus légion romaine',
                'Chassenon voie romaine garnison',
                'Cassinomagus Lemovices conflit'
            ]
        },
        'Angoulême_Roman': {
            'modern_name': 'Angoulême',
            'ancient_name': 'Iculisma',
            'coordinates': {'lat': 45.6500, 'lng': 0.1500},
            'type': 'Roman town',
            'searches': [
                'Iculisma bataille romaine',
                'Angoulême antique conflit',
                'Angoulême romain siège',
                'Iculisma invasion barbare'
            ]
        }
    }

    def __init__(self, google_api_key: str = None, google_cse_id: str = None,
                 anthropic_api_key: str = None, delay: float = 2.0):
        """Initialize expanded AI conflict scraper."""
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (historical research bot - 2500 years coverage)'
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

        # EXPANDED limits for 2,500 years
        self.max_total_searches = 150  # Increased from 60
        self.max_iterations = 3  # Increased from 2
        self.max_processing_time = 3600  # 1 hour (from 15 min)

    def scrape_conflicts_2500_years(self, location_name: str, latitude: float = None,
                                   longitude: float = None, department: str = None,
                                   region: str = None, radius_km: float = 100) -> Dict:
        """
        Scrape conflicts across 2,500 years (500 BC - 2024 AD).

        Args:
            location_name: Central location (e.g., "Chirac")
            latitude: GPS latitude
            longitude: GPS longitude
            department: Department name
            region: Region name
            radius_km: Search radius (default 100km)

        Returns:
            Comprehensive conflict data across 2,500 years
        """
        self.start_time = time.time()
        self.search_count = 0
        self.url_count = 0
        self.claude_calls = 0
        self.all_text = []
        self.phase_results = {}

        print(f"\n{'='*80}")
        print(f"⚔️  EXPANDED CONFLICT SCRAPING: 2,500 YEARS OF HISTORY")
        print(f"📍 Location: {location_name}, {department or ''}")
        print(f"📏 Radius: {radius_km}km")
        print(f"📅 Period: 500 BC - 2024 AD")
        print(f"{'='*80}\n")

        result = {
            'location_name': location_name,
            'department': department,
            'region': region,
            'latitude': latitude,
            'longitude': longitude,
            'radius_km': radius_km,
            'time_span': '500 BC - 2024 AD',
            'scraping_timestamp': datetime.utcnow().isoformat(),
            'scraping_method': 'AI-led expanded scraper (2500 years)',
            'phases': {},
            'stats': {},
            'conflicts': []
        }

        # ================================================================
        # PHASE 1: COMPREHENSIVE PERIOD-BY-PERIOD SEARCH
        # ================================================================
        print(f"{'='*80}")
        print("PHASE 1: COMPREHENSIVE HISTORICAL PERIOD SEARCHES")
        print(f"{'='*80}\n")

        period_data = self._phase1_comprehensive_period_search(
            location_name, department, region, latitude, longitude, radius_km
        )
        self.phase_results['phase1'] = period_data
        result['phases']['phase1_period_search'] = {
            'periods_searched': len(period_data.get('periods', [])),
            'total_searches': period_data.get('total_searches', 0),
            'text_collected': sum(len(t) for t in period_data.get('texts', []))
        }

        if not self.claude_available:
            print("\n⚠️  Claude API not available. Cannot proceed with AI extraction.")
            result['status'] = 'claude_unavailable'
            return result

        # ================================================================
        # PHASE 2: AI CONFLICT EXTRACTION
        # ================================================================
        print(f"\n{'='*80}")
        print("PHASE 2: AI CONFLICT EVENT EXTRACTION (2,500 YEARS)")
        print(f"{'='*80}\n")

        final_text = self._compile_all_text()
        print(f"   Total text collected: {len(final_text):,} chars")

        conflicts = self._phase2_extract_conflicts_2500_years(
            location_name,
            department,
            region,
            latitude,
            longitude,
            radius_km,
            final_text
        )

        result['conflicts'] = conflicts
        result['conflict_count'] = len(conflicts)

        result['phases']['phase2_extraction'] = {
            'total_text_chars': len(final_text),
            'conflicts_extracted': len(conflicts)
        }

        # Final stats
        result['stats'] = {
            'total_searches': self.search_count,
            'urls_fetched': self.url_count,
            'claude_api_calls': self.claude_calls,
            'total_text_chars': len(final_text),
            'processing_time_seconds': int(time.time() - self.start_time),
            'conflicts_by_period': self._count_by_period(conflicts)
        }

        print(f"\n{'='*80}")
        print("✅ 2,500-YEAR CONFLICT SCRAPING COMPLETE")
        print(f"{'='*80}")
        print(f"Searches: {self.search_count}")
        print(f"Claude calls: {self.claude_calls}")
        print(f"Text: {len(final_text):,} chars")
        print(f"Conflicts found: {len(conflicts)}")
        print(f"\nConflicts by period:")
        for period, count in result['stats']['conflicts_by_period'].items():
            print(f"  {period}: {count}")

        return result

    # ========================================================================
    # PHASE 1: COMPREHENSIVE PERIOD SEARCH
    # ========================================================================

    def _phase1_comprehensive_period_search(self, location: str, department: str,
                                           region: str, latitude: float,
                                           longitude: float, radius_km: float) -> Dict:
        """Phase 1: Comprehensive search across all 14 historical periods."""
        print("🔍 Phase 1: Comprehensive Historical Period Search...")
        print(f"   Covering 14 periods from 500 BC to 2024 AD\n")

        all_searches = []
        all_texts = []
        periods_searched = []

        # Get nearby sites for context
        nearby_sites = self._get_nearby_major_sites(location, latitude, longitude, radius_km)
        print(f"   Major sites in {radius_km}km radius: {', '.join(nearby_sites)}\n")

        # Search each historical period
        for period_key, period_data in self.PERIOD_TEMPLATES.items():
            if self.search_count >= self.max_total_searches:
                print(f"   ⚠️  Reached search limit ({self.max_total_searches})")
                break

            print(f"\n   {'─'*70}")
            print(f"   📅 Period: {period_data['years']} ({period_key.replace('_', ' ').title()})")
            print(f"   {'─'*70}")

            # Execute search queries for this period
            queries = period_data.get('search_queries', [])
            for query_template in queries[:6]:  # Limit queries per period
                if self.search_count >= self.max_total_searches:
                    break

                # Format query with location
                query = query_template.format(location=location)
                print(f"      → {query}")

                search_results = self._google_search(query, num_results=5)
                all_searches.append({
                    'period': period_key,
                    'query': query,
                    'results': search_results
                })

                # Extract texts
                for res in search_results:
                    if res.get('content'):
                        all_texts.append(res['content'])

                time.sleep(self.delay)

            periods_searched.append(period_key)

        # Special Roman site searches
        print(f"\n   {'─'*70}")
        print(f"   🏛️  Special Roman Site Searches (Cassinomagus, etc.)")
        print(f"   {'─'*70}")

        for site_key, site_data in self.ROMAN_SITES.items():
            if self.search_count >= self.max_total_searches:
                break

            for query in site_data.get('searches', [])[:3]:
                print(f"      → {query}")
                search_results = self._google_search(query, num_results=5)
                all_searches.append({
                    'period': 'roman_gaul',
                    'site': site_key,
                    'query': query,
                    'results': search_results
                })

                for res in search_results:
                    if res.get('content'):
                        all_texts.append(res['content'])

                time.sleep(self.delay)

        self.all_text.extend(all_texts)

        return {
            'periods': periods_searched,
            'searches': all_searches,
            'texts': all_texts,
            'total_searches': len(all_searches)
        }

    # ========================================================================
    # PHASE 2: AI EXTRACTION
    # ========================================================================

    def _phase2_extract_conflicts_2500_years(self, location: str, department: str,
                                            region: str, latitude: float,
                                            longitude: float, radius_km: float,
                                            all_text: str) -> List[Dict]:
        """Phase 2: Extract conflicts across 2,500 years using Claude."""
        print("🤖 Phase 2: AI Extraction of Conflicts (500 BC - 2024 AD)...")

        # Split into chunks if needed (Claude context limit)
        text_chunks = self._split_text_chunks(all_text, max_chunk_size=150000)
        print(f"   Processing {len(text_chunks)} text chunks...")

        all_conflicts = []

        for i, chunk in enumerate(text_chunks, 1):
            print(f"\n   Processing chunk {i}/{len(text_chunks)}...")

            prompt = f"""You are a French military historian analyzing 2,500 years of conflict history.

LOCATION: {location}, {department or ''} ({radius_km}km radius)
COORDINATES: {latitude}°N, {longitude}°E
TIME SPAN: 500 BC - 2024 AD

MAJOR SITES IN REGION:
- Cassinomagus (Chassenon) - Roman thermal/military complex
- Angoulême (ancient Iculisma) - Roman & medieval town
- Confolens - Medieval fortified town
- Rochechouart - Crater site, medieval castle
- Chabanais - Medieval & WW2 site

COLLECTED HISTORICAL DATA:
{chunk}

TASK: Extract ALL distinct conflict events from 500 BC to 2024 AD found in the data.

HISTORICAL PERIODS TO COVER:
1. Gallic Tribes Era (500-58 BC) - inter-tribal warfare
2. Gallic Wars (58-50 BC) - Caesar's conquest
3. Roman Gaul (50 BC - 410 AD) - Cassinomagus era, legions, barbarian raids
4. Late Antiquity (410-800 AD) - Visigoths, Franks invasions
5. Early Medieval (800-1000) - Viking raids, feudal conflicts
6. High Medieval (1000-1337) - Castle warfare, seigneurial conflicts
7. Hundred Years War (1337-1453) - English occupation, sieges
8. Wars of Religion (1562-1598) - Catholic-Protestant battles
9. 17th Century (1600-1700) - Fronde, royal army
10. French Revolution (1789-1799) - Terror, executions
11. Napoleonic Era (1799-1815) - Grande Armée, conscription
12. 19th Century (1815-1914) - Franco-Prussian War
13. World War I (1914-1918) - mobilization, casualties
14. World War II (1939-1945) - Resistance, liberation, battles
15. Modern (1945-2024) - post-war conflicts

For EACH conflict found, extract:

{{
  "name": "Official name in French",
  "date": "Best available date (negative year for BC, e.g., -52 for 52 BC, or YYYY-MM-DD for AD)",
  "date_str": "Human-readable date (e.g., '52 BC', '1944-07-31')",
  "date_precision": "day|month|year|decade|century|circa",
  "location": "Specific location",
  "latitude": float or null,
  "longitude": float or null,
  "conflict_type": "battle|siege|skirmish|raid|occupation|massacre|bombardment|tribal_warfare|invasion|other",
  "period": "gallic_tribes|gallic_wars|roman_gaul|late_antiquity|early_medieval|high_medieval|hundred_years_war|wars_of_religion|17th_century|revolution|napoleonic|19th_century|ww1|ww2|modern",
  "duration": "string or null",
  "participants": [
    {{"name": "unit/army/tribe name", "side": "attacker/defender/side1/side2", "role": "string"}},
    ...
  ],
  "casualties": {{"side1": int, "side2": int, "civilians": int}} or "unknown",
  "outcome": "detailed outcome description",
  "strategic_importance": "why this location mattered",
  "preceding_events": "what led to this" or null,
  "consequences": "what resulted",
  "sources": ["source1", "source2", ...],
  "confidence_score": 0-100,
  "impact_today": {{
    "infrastructure": "physical remains, monuments, archaeological sites",
    "economy": "economic impact then, tourism revenue now",
    "tourism": "museums, commemorative sites, annual ceremonies",
    "identity": "role in local/regional/national identity",
    "demographics": "population impacts, migrations",
    "governance": "political/administrative changes"
  }}
}}

SPECIAL INSTRUCTIONS FOR ANCIENT/ROMAN CONFLICTS:
- Use negative years for BC dates (e.g., -58 for 58 BC)
- Look for mentions of: oppida, Caesar, legions, Lemovices, Cassinomagus, Visigoths, Franks
- Archaeological evidence counts as valid source
- Even vague references to "tribal conflicts" or "barbarian raids" should be included with lower confidence

Return ONLY valid JSON array:
[
  {{conflict 1}},
  {{conflict 2}},
  ...
]

Include ALL conflicts found, even those with limited information. Use confidence_score to indicate reliability."""

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
                    json_str = response_text.strip()

                conflicts = json.loads(json_str)
                all_conflicts.extend(conflicts)

                print(f"      ✅ Extracted {len(conflicts)} conflicts from chunk {i}")

            except Exception as e:
                print(f"      ❌ Error extracting from chunk {i}: {e}")
                continue

        print(f"\n   ✅ Total conflicts extracted: {len(all_conflicts)}")

        # Deduplicate by name
        unique_conflicts = self._deduplicate_conflicts(all_conflicts)
        print(f"   ✅ Unique conflicts after deduplication: {len(unique_conflicts)}")

        return unique_conflicts

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _get_nearby_major_sites(self, location: str, lat: float, lng: float,
                               radius_km: float) -> List[str]:
        """Get list of major historical sites within radius."""
        # For now, return known major sites in Charente region
        sites = [
            'Chassenon (Cassinomagus)',
            'Angoulême',
            'Confolens',
            'Rochechouart',
            'Chabanais'
        ]
        return sites

    def _split_text_chunks(self, text: str, max_chunk_size: int = 150000) -> List[str]:
        """Split large text into chunks for Claude processing."""
        if len(text) <= max_chunk_size:
            return [text]

        chunks = []
        current_pos = 0
        while current_pos < len(text):
            chunk_end = current_pos + max_chunk_size
            chunks.append(text[current_pos:chunk_end])
            current_pos = chunk_end

        return chunks

    def _deduplicate_conflicts(self, conflicts: List[Dict]) -> List[Dict]:
        """Remove duplicate conflicts based on name similarity."""
        unique = []
        seen_names = set()

        for conflict in conflicts:
            name = conflict.get('name', '').lower()
            if name and name not in seen_names:
                seen_names.add(name)
                unique.append(conflict)

        return unique

    def _count_by_period(self, conflicts: List[Dict]) -> Dict[str, int]:
        """Count conflicts by historical period."""
        counts = {}
        for conflict in conflicts:
            period = conflict.get('period', 'unknown')
            counts[period] = counts.get(period, 0) + 1
        return dict(sorted(counts.items()))

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
                if self.url_count < 300:  # Higher limit for expanded search
                    content = self._fetch_url(result['url'])
                    if content:
                        result['content'] = content
                        self.url_count += 1

                results.append(result)

            return results

        except Exception as e:
            print(f"         ✗ Search error: {e}")
            return []

    def _fetch_url(self, url: str, max_length: int = 8000) -> Optional[str]:
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

    def _compile_all_text(self) -> str:
        """Compile all text with deduplication."""
        unique_texts = []
        seen = set()

        for text in self.all_text:
            text_hash = hash(text[:200])
            if text_hash not in seen:
                seen.add(text_hash)
                unique_texts.append(text)

        return '\n\n'.join(unique_texts)


def main():
    """Main execution for 2,500-year conflict scraping."""
    import argparse

    parser = argparse.ArgumentParser(
        description='EXPANDED AI Conflict Scraper: 2,500 Years (500 BC - 2024 AD)',
        epilog="""
Example:
  python ai_conflict_scraper_expanded.py --location "Chirac" --department "Charente" --region "Nouvelle-Aquitaine" --lat 45.9164 --lng 0.6542 --radius 100

Coverage:
  - 14 historical periods from 500 BC to 2024 AD
  - 100km radius search
  - Special focus on Roman sites (Cassinomagus/Chassenon)
  - Expected output: 90-170 conflicts

Cost: ~$2-3 (Claude API)
Time: 4-8 hours
        """
    )

    parser.add_argument('--location', required=True, help='Central location (e.g., Chirac)')
    parser.add_argument('--department', help='Department name (e.g., Charente)')
    parser.add_argument('--region', help='Region name')
    parser.add_argument('--lat', type=float, help='Latitude')
    parser.add_argument('--lng', type=float, help='Longitude')
    parser.add_argument('--radius', type=float, default=100, help='Search radius in km (default: 100)')
    parser.add_argument('--google-key', help='Google API key')
    parser.add_argument('--google-cse', help='Google CSE ID')
    parser.add_argument('--claude-key', help='Claude API key')
    parser.add_argument('--output', help='Output JSON file')
    parser.add_argument('--delay', type=float, default=2.0, help='Delay between searches')

    args = parser.parse_args()

    scraper = AIConflictScraperExpanded(
        google_api_key=args.google_key,
        google_cse_id=args.google_cse,
        anthropic_api_key=args.claude_key,
        delay=args.delay
    )

    result = scraper.scrape_conflicts_2500_years(
        location_name=args.location,
        latitude=args.lat,
        longitude=args.lng,
        department=args.department,
        region=args.region,
        radius_km=args.radius
    )

    output_path = args.output or f"{args.location.lower()}_2500years.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print(f"✅ OUTPUT: {output_path}")
    print(f"{'='*80}\n")

    print(f"⚔️  Total Conflicts: {result.get('conflict_count', 0)}")
    print(f"📊 By Period:")
    for period, count in result['stats'].get('conflicts_by_period', {}).items():
        print(f"   {period}: {count}")
    print(f"\n🔍 Searches: {result['stats'].get('total_searches', 0)}")
    print(f"🤖 Claude calls: {result['stats'].get('claude_api_calls', 0)}")
    print(f"📝 Text collected: {result['stats'].get('total_text_chars', 0):,} chars")
    print(f"⏱️  Time: {result['stats'].get('processing_time_seconds', 0)}s")


if __name__ == '__main__':
    main()
