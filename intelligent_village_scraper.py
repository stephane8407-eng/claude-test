#!/usr/bin/env python3
"""
Intelligent Village Scraper - Iterative Discovery System
Uses Google Custom Search API + intelligent entity following to find deep content.

Features:
- Real Google Custom Search API integration
- Iterative entity discovery (follows leads 2-3 levels deep)
- Smart keyword expansion
- Actual URL fetching and parsing
- Cost controls
- Discovery trail tracking

CRITICAL: This scraper FINDS WHAT GOOGLE FINDS!
Test case: Chirac, Charente should find forges, châteaux, 1944 events.
"""

import os
import sys
import time
import json
import re
import requests
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
from urllib.parse import quote, urlparse
from collections import defaultdict

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("Warning: beautifulsoup4 not installed. Install with: pip install beautifulsoup4", file=sys.stderr)

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("Warning: anthropic not installed. Install with: pip install anthropic", file=sys.stderr)


# Keyword expansions for intelligent searching
KEYWORD_EXPANSIONS = {
    'forge': ['mine', 'métallurgie', 'fer', 'fonderie', 'haut-fourneau', 'exploitation minière'],
    'château': ['manoir', 'fortification', 'seigneur', 'noble', 'donjon', 'tour'],
    'église': ['chapelle', 'abbaye', 'prieuré', 'fresque', 'patrimoine religieux', 'clocher'],
    '1944': ['résistance', 'libération', 'occupation', 'maquis', 'bombardement', 'Wehrmacht'],
    'souterrain': ['passage', 'tunnel', 'galerie', 'crypte', 'cave', 'grotte'],
    'bataille': ['siège', 'conflit', 'guerre', 'combat', 'retraite', 'occupation'],
    'mine': ['carrière', 'exploitation', 'minerai', 'galerie', 'puits'],
    'trésor': ['légende', 'cache', 'butin', 'fortune', 'or', 'argent']
}


class IntelligentVillageScraper:
    """
    Intelligent scraper with iterative entity discovery.
    Follows leads to find content 2-3 clicks deep.
    """

    def __init__(self, google_api_key: str = None, google_cse_id: str = None,
                 anthropic_api_key: str = None, delay: float = 2.0):
        """
        Initialize intelligent scraper.

        Args:
            google_api_key: Google Custom Search API key
            google_cse_id: Google Custom Search Engine ID
            anthropic_api_key: Claude API key
            delay: Delay between requests (seconds)
        """
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (historical research bot)'
        })

        # Google API setup
        self.google_api_key = google_api_key or os.environ.get('GOOGLE_API_KEY')
        self.google_cse_id = google_cse_id or os.environ.get('GOOGLE_CSE_ID')
        self.google_available = bool(self.google_api_key and self.google_cse_id)

        if not self.google_available:
            print("⚠️  WARNING: Google Custom Search API not configured!")
            print("Set GOOGLE_API_KEY and GOOGLE_CSE_ID environment variables")
            print("Get free API key at: https://developers.google.com/custom-search/v1/overview")

        # Claude API setup
        self.anthropic_api_key = anthropic_api_key or os.environ.get('ANTHROPIC_API_KEY')
        if self.anthropic_api_key and ANTHROPIC_AVAILABLE:
            self.claude_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
            self.claude_available = True
        else:
            self.claude_client = None
            self.claude_available = False

        # Cost control limits
        self.max_searches = 50
        self.max_urls = 30
        self.max_processing_time = 600  # 10 minutes
        self.max_total_text = 100000

        # Tracking
        self.search_count = 0
        self.url_count = 0
        self.start_time = None
        self.discovered_entities = set()
        self.discovery_trail = []
        self.all_text = []

    def scrape_village(self, village_name: str, latitude: float = None,
                      longitude: float = None, department: str = None) -> Dict:
        """
        Intelligently scrape village with iterative entity discovery.

        Args:
            village_name: Village name
            latitude: GPS latitude
            longitude: GPS longitude
            department: Department name

        Returns:
            Comprehensive intelligence dict
        """
        self.start_time = time.time()
        self.search_count = 0
        self.url_count = 0
        self.discovered_entities = set()
        self.discovery_trail = []
        self.all_text = []

        print(f"\n{'='*80}")
        print(f"🔍 INTELLIGENT SCRAPING: {village_name}")
        print(f"{'='*80}\n")

        result = {
            'village_name': village_name,
            'department': department,
            'latitude': latitude,
            'longitude': longitude,
            'scraping_timestamp': datetime.utcnow().isoformat(),
            'sources': {},
            'discovered_entities': [],
            'discovery_trail': [],
            'stats': {}
        }

        # Phase 1: Wikipedia (try multiple formats)
        print("📚 Phase 1: Wikipedia...")
        result['sources']['wikipedia'] = self._smart_wikipedia_search(village_name, department)

        # Phase 2: Mérimée heritage database
        print("🏛️  Phase 2: Mérimée monuments...")
        result['sources']['merimee'] = self._merimee_search(village_name, latitude, longitude)

        # Phase 3: Initial Google searches
        print("🔍 Phase 3: Initial discovery searches...")
        initial_searches = [
            f"{village_name} {department} histoire",
            f"{village_name} {department} patrimoine",
            f"{village_name} château",
            f"{village_name} église",
            f"{village_name} forge mine"
        ]

        initial_results = []
        for query in initial_searches:
            if self._should_continue():
                results = self._google_search(query)
                initial_results.extend(results)
                time.sleep(self.delay)

        result['sources']['initial_searches'] = initial_results

        # Phase 4: Extract entities from initial results
        print("🧠 Phase 4: Extracting entities...")
        entities = self._extract_entities(initial_results, village_name)
        self.discovered_entities.update(entities)
        print(f"   Found {len(entities)} entities: {', '.join(list(entities)[:10])}")

        # Phase 5: Follow entity leads (iterative discovery)
        print("🔎 Phase 5: Following entity leads...")
        entity_results = self._follow_entities(entities, village_name, department)
        result['sources']['entity_searches'] = entity_results

        # Phase 6: Smart keyword expansion
        print("💡 Phase 6: Keyword expansion...")
        expansion_results = self._expand_keywords(village_name, department)
        result['sources']['keyword_expansions'] = expansion_results

        # Phase 7: Targeted event searches
        print("📅 Phase 7: Event-based searches...")
        event_results = self._search_events(village_name, department)
        result['sources']['event_searches'] = event_results

        # Phase 8: Academic and archive sources
        print("📖 Phase 8: Academic sources...")
        result['sources']['gallica'] = self._search_gallica(village_name, department)
        result['sources']['persee'] = self._search_persee(village_name)
        result['sources']['inrap'] = self._search_inrap(village_name, latitude, longitude)

        # Compile all text
        total_text = self._compile_all_text()

        # Stats
        result['discovered_entities'] = list(self.discovered_entities)
        result['discovery_trail'] = self.discovery_trail
        result['stats'] = {
            'searches_performed': self.search_count,
            'urls_fetched': self.url_count,
            'total_text_chars': len(total_text),
            'entities_discovered': len(self.discovered_entities),
            'processing_time_seconds': int(time.time() - self.start_time)
        }

        print(f"\n{'='*80}")
        print(f"📊 SCRAPING COMPLETE")
        print(f"{'='*80}")
        print(f"Searches: {self.search_count}")
        print(f"URLs fetched: {self.url_count}")
        print(f"Text collected: {len(total_text):,} chars")
        print(f"Entities discovered: {len(self.discovered_entities)}")
        print(f"Time: {result['stats']['processing_time_seconds']}s")

        # Process with Claude if available
        if self.claude_available and total_text:
            print(f"\n🤖 Processing with Claude API...")
            intelligence = self._process_with_claude(village_name, department, total_text, result)
            result['intelligence'] = intelligence
        else:
            result['raw_text'] = total_text[:10000]  # Sample

        return result

    def _should_continue(self) -> bool:
        """Check if we should continue scraping (cost controls)."""
        if self.search_count >= self.max_searches:
            print(f"   ⚠️  Reached max searches ({self.max_searches})")
            return False
        if self.url_count >= self.max_urls:
            print(f"   ⚠️  Reached max URLs ({self.max_urls})")
            return False
        if time.time() - self.start_time > self.max_processing_time:
            print(f"   ⚠️  Reached max time ({self.max_processing_time}s)")
            return False
        total_chars = sum(len(t) for t in self.all_text)
        if total_chars > self.max_total_text:
            print(f"   ⚠️  Reached max text ({self.max_total_text} chars)")
            return False
        return True

    # ========================================================================
    # GOOGLE CUSTOM SEARCH API
    # ========================================================================

    def _google_search(self, query: str, num_results: int = 10) -> List[Dict]:
        """
        Execute REAL Google Custom Search API call.

        Args:
            query: Search query
            num_results: Number of results to return

        Returns:
            List of search results with URLs and snippets
        """
        if not self.google_available:
            print(f"   ⚠️  Google API not configured, skipping: {query}")
            return []

        try:
            self.search_count += 1
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.google_api_key,
                'cx': self.google_cse_id,
                'q': query,
                'num': min(num_results, 10)  # API limit
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

                # Fetch actual page content
                if self._should_continue():
                    content = self._fetch_url(result['url'])
                    if content:
                        result['content'] = content
                        self.all_text.append(content)

                results.append(result)

            if results:
                print(f"   ✓ '{query}' → {len(results)} results")
                self.discovery_trail.append(f"Search: '{query}' → Found {len(results)} results")

            return results

        except Exception as e:
            print(f"   ✗ Google search error for '{query}': {e}")
            return []

    def _fetch_url(self, url: str, max_length: int = 5000) -> Optional[str]:
        """
        Fetch URL and extract meaningful text.

        Args:
            url: URL to fetch
            max_length: Maximum text length to return

        Returns:
            Extracted text or None
        """
        if not BS4_AVAILABLE:
            return None

        try:
            self.url_count += 1
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove noise
            for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe']):
                tag.decompose()

            # Get text
            text = soup.get_text()

            # Clean up
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            text = '\n'.join(lines)

            # Limit length
            if len(text) > max_length:
                text = text[:max_length] + "..."

            return text

        except Exception as e:
            print(f"   ✗ Failed to fetch {url[:50]}: {e}")
            return None

    # ========================================================================
    # WIKIPEDIA - SMART SEARCH
    # ========================================================================

    def _smart_wikipedia_search(self, village: str, department: str = None) -> Dict:
        """
        Try multiple Wikipedia page formats to find correct commune page.

        Args:
            village: Village name
            department: Department name

        Returns:
            Wikipedia content dict
        """
        # Try multiple page title formats
        attempts = [
            village,
            f"{village}_(commune)",
            f"{village}_(Charente)" if department and 'charente' in department.lower() else None,
            f"{village}_(Corrèze)" if department and 'corrèze' in department.lower() else None,
            f"{village}_(France)",
            f"{village},_{department}" if department else None,
        ]

        attempts = [a for a in attempts if a]  # Remove None

        for attempt in attempts:
            content = self._fetch_wikipedia_page(attempt)
            if content and len(content) > 500:  # Valid page
                print(f"   ✓ Found Wikipedia: {attempt}")
                self.all_text.append(content)
                return {
                    'status': 'success',
                    'page_title': attempt,
                    'content': content,
                    'length': len(content)
                }

        print(f"   ✗ Wikipedia: No page found for {village}")
        return {'status': 'not_found'}

    def _fetch_wikipedia_page(self, page_title: str) -> Optional[str]:
        """Fetch Wikipedia page content via API."""
        try:
            time.sleep(self.delay)
            api_url = "https://fr.wikipedia.org/w/api.php"
            params = {
                'action': 'query',
                'format': 'json',
                'titles': page_title,
                'prop': 'extracts',
                'explaintext': True
            }

            response = self.session.get(api_url, params=params, timeout=15)
            data = response.json()

            pages = data.get('query', {}).get('pages', {})
            for page_id, page_data in pages.items():
                if page_id != '-1':
                    return page_data.get('extract', '')

            return None

        except Exception as e:
            return None

    # ========================================================================
    # MÉRIMÉE - FIXED PARSING
    # ========================================================================

    def _merimee_search(self, village: str, latitude: float = None,
                       longitude: float = None) -> Dict:
        """
        Search Mérimée database with PROPER PARSING.

        Args:
            village: Village name
            latitude: GPS latitude
            longitude: GPS longitude

        Returns:
            Monument data dict
        """
        try:
            time.sleep(self.delay)

            # Mérimée API
            api_url = "https://data.culture.gouv.fr/api/records/1.0/search/"
            params = {
                'dataset': 'liste-des-immeubles-proteges-au-titre-des-monuments-historiques',
                'q': village,
                'rows': 50
            }

            response = self.session.get(api_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            monuments = []
            for record in data.get('records', []):
                fields = record.get('fields', {})

                # Only include if has actual data
                name = fields.get('tico') or fields.get('deno', '')
                if not name:
                    continue

                monument = {
                    'name': name,
                    'type': fields.get('deno', ''),
                    'protection': fields.get('prot', ''),
                    'century': fields.get('scle', ''),
                    'date': fields.get('dpro', ''),
                    'location': fields.get('adrs', ''),
                    'commune': fields.get('com', ''),
                    'reference': fields.get('ref', '')
                }

                monuments.append(monument)

                # Add to text
                desc = f"Monument: {monument['name']} ({monument['type']}) - {monument['century']} - {monument['protection']}"
                self.all_text.append(desc)

            print(f"   ✓ Mérimée: {len(monuments)} monuments")
            return {
                'status': 'success',
                'count': len(monuments),
                'monuments': monuments
            }

        except Exception as e:
            print(f"   ✗ Mérimée error: {e}")
            return {'status': 'error', 'message': str(e)}

    # ========================================================================
    # ENTITY EXTRACTION & FOLLOWING
    # ========================================================================

    def _extract_entities(self, search_results: List[Dict], village: str) -> Set[str]:
        """
        Extract entities (places, monuments, people) from search results.

        Args:
            search_results: List of search result dicts
            village: Village name (to filter out)

        Returns:
            Set of discovered entities
        """
        entities = set()

        # Patterns for entity extraction
        chateau_pattern = re.compile(r'[Cc]hâteau\s+(?:de\s+)?([A-Z][a-zéèêàù]+(?:\s+[A-Z][a-zéèêàù]+)*)')
        forge_pattern = re.compile(r'[Ff]orges?\s+(?:de\s+)?([A-Z][a-zéèêàù]+(?:\s+[A-Z][a-zéèêàù]+)*)')
        eglise_pattern = re.compile(r'[ÉéE]glise\s+(?:de\s+)?(?:Saint-?)?([A-Z][a-zéèêàù]+(?:\s+[A-Z][a-zéèêàù]+)*)')
        mine_pattern = re.compile(r'[Mm]ines?\s+(?:de\s+)?([A-Z][a-zéèêàù]+(?:\s+[A-Z][a-zéèêàù]+)*)')
        manoir_pattern = re.compile(r'[Mm]anoir\s+(?:de\s+)?([A-Z][a-zéèêàù]+(?:\s+[A-Z][a-zéèêàù]+)*)')

        for result in search_results:
            text = result.get('snippet', '') + ' ' + result.get('content', '')

            # Extract châteaux
            for match in chateau_pattern.finditer(text):
                entity = f"Château de {match.group(1)}"
                if village.lower() not in entity.lower():
                    entities.add(entity)

            # Extract forges
            for match in forge_pattern.finditer(text):
                entity = f"Forges de {match.group(1)}"
                entities.add(entity)

            # Extract églises
            for match in eglise_pattern.finditer(text):
                entity = f"Église de {match.group(1)}"
                entities.add(entity)

            # Extract mines
            for match in mine_pattern.finditer(text):
                entity = f"Mines de {match.group(1)}"
                entities.add(entity)

            # Extract manoirs
            for match in manoir_pattern.finditer(text):
                entity = f"Manoir de {match.group(1)}"
                entities.add(entity)

        return entities

    def _follow_entities(self, entities: Set[str], village: str, department: str) -> List[Dict]:
        """
        Follow discovered entities with targeted searches.
        This is the GAME CHANGER - finds content 2-3 clicks deep!

        Args:
            entities: Set of discovered entities
            village: Village name
            department: Department name

        Returns:
            List of entity search results
        """
        results = []

        for entity in list(entities)[:15]:  # Limit to top 15 entities
            if not self._should_continue():
                break

            print(f"   → Following: {entity}")

            # Search for entity + village
            query = f'"{entity}" {village}'
            entity_results = self._google_search(query, num_results=5)
            results.extend(entity_results)

            if entity_results:
                self.discovery_trail.append(f"Entity: '{entity}' → {len(entity_results)} results")

            time.sleep(self.delay)

            # Search for entity + histoire
            if self._should_continue():
                query = f'"{entity}" histoire'
                hist_results = self._google_search(query, num_results=3)
                results.extend(hist_results)
                time.sleep(self.delay)

        return results

    # ========================================================================
    # SMART KEYWORD EXPANSION
    # ========================================================================

    def _expand_keywords(self, village: str, department: str) -> List[Dict]:
        """
        If certain keywords found, search related terms.

        Args:
            village: Village name
            department: Department name

        Returns:
            List of expansion search results
        """
        results = []

        # Check what keywords we've found
        all_text_lower = ' '.join(self.all_text).lower()

        for keyword, expansions in KEYWORD_EXPANSIONS.items():
            if keyword in all_text_lower:
                print(f"   💡 Found '{keyword}' → expanding...")

                for expansion in expansions[:3]:  # Top 3 expansions
                    if not self._should_continue():
                        break

                    query = f"{village} {expansion}"
                    exp_results = self._google_search(query, num_results=3)
                    results.extend(exp_results)

                    if exp_results:
                        self.discovery_trail.append(f"Expansion: '{keyword}' → '{expansion}' → {len(exp_results)} results")

                    time.sleep(self.delay)

        return results

    # ========================================================================
    # EVENT-BASED SEARCHES
    # ========================================================================

    def _search_events(self, village: str, department: str) -> List[Dict]:
        """
        Search for specific historical events.

        Args:
            village: Village name
            department: Department name

        Returns:
            List of event search results
        """
        results = []

        # Important historical periods for France
        periods = [
            '1944', '1940', 'guerre mondiale',
            '1914', 'première guerre',
            '1870', 'guerre franco-prussienne',
            '1789', 'révolution',
            'guerres de religion', '1569'
        ]

        for period in periods:
            if not self._should_continue():
                break

            query = f"{village} {department} {period}"
            period_results = self._google_search(query, num_results=3)
            results.extend(period_results)

            time.sleep(self.delay)

        return results

    # ========================================================================
    # ACADEMIC & ARCHIVE SOURCES
    # ========================================================================

    def _search_gallica(self, village: str, department: str) -> Dict:
        """Search Gallica national library."""
        try:
            time.sleep(self.delay)

            # Gallica SRU API
            api_url = "https://gallica.bnf.fr/SRU"
            params = {
                'version': '1.2',
                'operation': 'searchRetrieve',
                'query': f'(dc.title all "{village}") or (dc.subject all "{village}")',
                'maximumRecords': 10
            }

            response = self.session.get(api_url, params=params, timeout=15)

            if response.status_code == 200:
                # Simple text extraction (SRU returns XML)
                text = response.text
                self.all_text.append(text[:2000])
                print(f"   ✓ Gallica: Retrieved")
                return {'status': 'success', 'text': text[:2000]}

            return {'status': 'error', 'code': response.status_code}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _search_persee(self, village: str) -> Dict:
        """Search Persée academic portal."""
        try:
            time.sleep(self.delay)

            # Search Persée
            search_url = f"https://www.persee.fr/search?q={quote(village)}"
            response = self.session.get(search_url, timeout=15)

            if response.status_code == 200:
                # Extract text
                if BS4_AVAILABLE:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    text = soup.get_text()[:2000]
                    self.all_text.append(text)
                    print(f"   ✓ Persée: Retrieved")
                    return {'status': 'success', 'text': text}

            return {'status': 'error'}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _search_inrap(self, village: str, latitude: float = None,
                     longitude: float = None) -> Dict:
        """Search INRAP archaeological database."""
        try:
            time.sleep(self.delay)

            # INRAP search
            search_url = f"https://www.inrap.fr/recherche?q={quote(village)}"
            response = self.session.get(search_url, timeout=15)

            if response.status_code == 200:
                if BS4_AVAILABLE:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    text = soup.get_text()[:2000]
                    self.all_text.append(text)
                    print(f"   ✓ INRAP: Retrieved")
                    return {'status': 'success', 'text': text}

            return {'status': 'error'}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    # ========================================================================
    # TEXT COMPILATION
    # ========================================================================

    def _compile_all_text(self) -> str:
        """Compile all collected text."""
        # Deduplicate and join
        unique_texts = []
        seen = set()

        for text in self.all_text:
            text_hash = hash(text[:100])  # Hash first 100 chars
            if text_hash not in seen:
                seen.add(text_hash)
                unique_texts.append(text)

        return '\n\n'.join(unique_texts)

    # ========================================================================
    # CLAUDE AI PROCESSING
    # ========================================================================

    def _process_with_claude(self, village: str, department: str,
                            text: str, scraping_result: Dict) -> Dict:
        """
        Process collected text with Claude API for structured extraction.

        Args:
            village: Village name
            department: Department name
            text: Collected text
            scraping_result: Raw scraping result

        Returns:
            Structured intelligence dict
        """
        if not self.claude_available:
            return {'status': 'claude_unavailable'}

        try:
            # Limit text to fit in Claude context
            text = text[:100000]

            prompt = f"""Analyze this data about {village}, {department} and extract comprehensive intelligence for treasure hunting.

SOURCE DATA:
{text}

DISCOVERED ENTITIES:
{', '.join(list(self.discovered_entities)[:20])}

EXTRACT THE FOLLOWING WITH MAXIMUM DETAIL:

1. VILLAGE IDENTITY (name, population, significance)

2. HISTORICAL EVENTS (WITH DATES):
   - Battles, sieges, occupations
   - Wars, conflicts, retreats
   - For each: date, type, participants, outcome, treasure relevance (0-100)

3. ECONOMIC/INDUSTRIAL HISTORY:
   - Mines, forges, quarries (CRITICAL: include dates, resources, locations)
   - Industries, factories
   - For each: type, resource, operating dates, closure reason, treasure relevance

4. ARCHAEOLOGICAL DATA:
   - Finds, excavations, museum artifacts
   - For each: type, date found, age, location, significance

5. TREASURE INDICATORS:
   - Documented finds
   - Legends (with credibility 0-100)
   - Underground structures
   - Emergency burials

6. MILITARY/STRATEGIC:
   - Fortifications (châteaux, églises fortifiées)
   - Strategic importance
   - Retreat routes

7. GEOGRAPHIC/GEOLOGICAL:
   - Rivers, wells, underground features
   - Soil type, terrain

8. LEGENDS & FOLKLORE:
   - Treasure tales with location clues
   - Credibility scores

9. CROSS-REFERENCES:
   - Nearby battles
   - Connected villages
   - Historical routes

OUTPUT STRICT JSON:
{{
  "village_name": "{village}",
  "department": "{department}",
  "identity": {{...}},
  "historical_events": [{{
    "date": "YYYY or YYYY-MM-DD",
    "event_type": "type",
    "description": "...",
    "treasure_relevance": 0-100,
    "source": "where found",
    "confidence": 0-100
  }}],
  "economic": [{{
    "type": "mine|forge|quarry",
    "name": "specific name if known",
    "resource": "iron|stone|etc",
    "dates": "operating period",
    "location": "where",
    "treasure_relevance": 0-100,
    "source": "...",
    "confidence": 0-100
  }}],
  "archaeological": [...],
  "treasure_indicators": [...],
  "military_strategic": {{...}},
  "geographic": {{...}},
  "legends_folklore": [...],
  "cross_references": {{...}},
  "treasure_probability": {{
    "overall_score": 0-100,
    "reasoning": "detailed explanation",
    "key_factors": ["factor1", "factor2", ...]
  }},
  "data_quality": {{
    "completeness": 0-100,
    "confidence_average": 0-100
  }}
}}

Return ONLY valid JSON."""

            # Call Claude
            response = self.claude_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=16000,
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

            intelligence = json.loads(json_str)
            intelligence['status'] = 'success'

            print(f"✅ Claude processing complete")
            print(f"   Treasure probability: {intelligence.get('treasure_probability', {}).get('overall_score', 'N/A')}/100")

            return intelligence

        except Exception as e:
            print(f"❌ Claude processing error: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }


def main():
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Intelligent Village Scraper with Iterative Discovery',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full intelligent scraping (requires Google API)
  python intelligent_village_scraper.py --village "Chirac" --department "Charente" --lat 45.9833 --lng 0.1167

  # With explicit API keys
  python intelligent_village_scraper.py --village "Azincourt" --google-key "..." --google-cse "..." --claude-key "..."

Environment Variables:
  GOOGLE_API_KEY       Google Custom Search API key (get at https://developers.google.com/custom-search)
  GOOGLE_CSE_ID        Google Custom Search Engine ID (create at https://cse.google.com/cse/)
  ANTHROPIC_API_KEY    Claude API key for processing

Cost Estimate:
  ~50 Google searches × $0.005 = $0.25
  ~1 Claude API call × $0.50 = $0.50
  Total per village: ~$0.75-1.00

Test Case (Chirac, Charente):
  Should find:
  ✓ Château de l'Age
  ✓ Les Forges de l'Age (1450-1680)
  ✓ Château de Tisseuil
  ✓ 1944 German retreat events
  ✓ Chapel with frescoes
  ✓ 20,000+ characters of text
  ✓ Treasure score 75-85/100
        """
    )

    parser.add_argument('--village', required=True, help='Village name')
    parser.add_argument('--department', help='Department name')
    parser.add_argument('--lat', type=float, help='Latitude')
    parser.add_argument('--lng', type=float, help='Longitude')
    parser.add_argument('--google-key', help='Google API key (or use GOOGLE_API_KEY env var)')
    parser.add_argument('--google-cse', help='Google CSE ID (or use GOOGLE_CSE_ID env var)')
    parser.add_argument('--claude-key', help='Claude API key (or use ANTHROPIC_API_KEY env var)')
    parser.add_argument('--output', help='Output JSON file (default: {village}_intelligent.json)')
    parser.add_argument('--max-searches', type=int, default=50, help='Max Google searches')
    parser.add_argument('--max-urls', type=int, default=30, help='Max URLs to fetch')
    parser.add_argument('--delay', type=float, default=2.0, help='Delay between requests (seconds)')

    args = parser.parse_args()

    # Initialize scraper
    scraper = IntelligentVillageScraper(
        google_api_key=args.google_key,
        google_cse_id=args.google_cse,
        anthropic_api_key=args.claude_key,
        delay=args.delay
    )

    scraper.max_searches = args.max_searches
    scraper.max_urls = args.max_urls

    # Scrape village
    result = scraper.scrape_village(
        village_name=args.village,
        latitude=args.lat,
        longitude=args.lng,
        department=args.department
    )

    # Save output
    output_path = args.output or f"{args.village.lower().replace(' ', '_')}_intelligent.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print(f"✅ OUTPUT SAVED: {output_path}")
    print(f"{'='*80}\n")

    # Print summary
    if 'intelligence' in result and result['intelligence'].get('status') == 'success':
        intel = result['intelligence']
        prob = intel.get('treasure_probability', {})
        print(f"🎯 Treasure Probability: {prob.get('overall_score', 'N/A')}/100")
        print(f"📊 Completeness: {intel.get('data_quality', {}).get('completeness', 'N/A')}/100")

        econ = intel.get('economic', [])
        if econ:
            print(f"\n💰 Economic Sites Found:")
            for item in econ[:5]:
                print(f"   - {item.get('type', 'Unknown')}: {item.get('name', 'N/A')} ({item.get('dates', 'N/A')})")

        events = intel.get('historical_events', [])
        if events:
            print(f"\n⚔️  Historical Events:")
            for event in events[:5]:
                print(f"   - {event.get('date', 'N/A')}: {event.get('event_type', 'Unknown')}")


if __name__ == '__main__':
    main()
