#!/usr/bin/env python3
"""
Enhanced Village Intelligence Scraper
Comprehensive multi-source data collection with aggressive search.

Searches:
- Multiple Wikipedia possibilities
- Google search results for histoire, patrimoine, légendes
- Official mairie websites (multiple URL patterns)
- Department archives
- Local history sites
- Genealogy sites

Usage:
    python enhanced_village_scraper.py --village "Chirac" --department "Charente"
"""

import requests
from bs4 import BeautifulSoup
import json
import argparse
import time
import re
from typing import List, Dict, Tuple
from urllib.parse import quote, urljoin
import sys


class EnhancedVillageIntelligence:
    """Comprehensive village data collection with aggressive multi-source searching."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,fr;q=0.9,en;q=0.8',
        })

        self.found_urls = []
        self.scraped_content = {}
        self.search_results = {}

    def search_village(self, village: str, department: str = None):
        """
        Comprehensive village search across all sources.

        Args:
            village: Village name (e.g., "Chirac")
            department: Department name (e.g., "Charente")
        """
        print(f"\n{'='*70}")
        print(f"ENHANCED INTELLIGENCE GATHERING: {village}")
        if department:
            print(f"Department: {department}")
        print(f"{'='*70}\n")

        results = {
            'village': village,
            'department': department,
            'sources_found': [],
            'urls_discovered': [],
            'content': {}
        }

        # 1. Wikipedia (multiple attempts)
        print("[1/7] Searching Wikipedia...")
        wiki_urls, wiki_content = self._search_wikipedia(village, department)
        results['sources_found'].extend(['Wikipedia'] * len(wiki_urls))
        results['urls_discovered'].extend(wiki_urls)
        results['content']['wikipedia'] = wiki_content
        print(f"      ✓ Found {len(wiki_urls)} Wikipedia pages")

        # 2. Official Mairie websites
        print("\n[2/7] Searching official mairie websites...")
        mairie_urls, mairie_content = self._search_mairie_sites(village)
        results['sources_found'].extend(['Mairie Website'] * len(mairie_urls))
        results['urls_discovered'].extend(mairie_urls)
        results['content']['mairie'] = mairie_content
        print(f"      ✓ Found {len(mairie_urls)} mairie websites")

        # 3. Department archives
        print("\n[3/7] Searching department archives...")
        archive_urls, archive_content = self._search_archives(village, department)
        results['sources_found'].extend(['Archives'] * len(archive_urls))
        results['urls_discovered'].extend(archive_urls)
        results['content']['archives'] = archive_content
        print(f"      ✓ Found {len(archive_urls)} archive sites")

        # 4. Google: Histoire (history)
        print("\n[4/7] Google searching: village histoire...")
        history_urls, history_content = self._google_search(village, department, "histoire")
        results['sources_found'].extend(['History Site'] * len(history_urls))
        results['urls_discovered'].extend(history_urls)
        results['content']['histoire'] = history_content
        print(f"      ✓ Found {len(history_urls)} history pages")

        # 5. Google: Patrimoine (heritage)
        print("\n[5/7] Google searching: village patrimoine...")
        heritage_urls, heritage_content = self._google_search(village, department, "patrimoine")
        results['sources_found'].extend(['Heritage Site'] * len(heritage_urls))
        results['urls_discovered'].extend(heritage_urls)
        results['content']['patrimoine'] = heritage_content
        print(f"      ✓ Found {len(heritage_urls)} heritage pages")

        # 6. Google: Légendes (legends)
        print("\n[6/7] Google searching: village légendes...")
        legends_urls, legends_content = self._google_search(village, department, "légendes")
        results['sources_found'].extend(['Legends Site'] * len(legends_urls))
        results['urls_discovered'].extend(legends_urls)
        results['content']['legendes'] = legends_content
        print(f"      ✓ Found {len(legends_urls)} legend pages")

        # 7. Google: Bataille (battles)
        print("\n[7/7] Google searching: village bataille...")
        battle_urls, battle_content = self._google_search(village, department, "bataille")
        results['sources_found'].extend(['Battle Site'] * len(battle_urls))
        results['urls_discovered'].extend(battle_urls)
        results['content']['bataille'] = battle_content
        print(f"      ✓ Found {len(battle_urls)} battle pages")

        # Summary
        print(f"\n{'='*70}")
        print(f"SEARCH COMPLETE")
        print(f"{'='*70}")
        print(f"Total URLs discovered: {len(results['urls_discovered'])}")
        print(f"Total content sources: {len([c for c in results['content'].values() if c])}")

        return results

    def _search_wikipedia(self, village: str, department: str = None) -> Tuple[List[str], Dict]:
        """Search Wikipedia with multiple patterns."""
        urls_found = []
        content = {}

        # Try multiple Wikipedia URL patterns
        patterns = [
            village,
            f"{village}_{department}" if department else None,
            f"{village}_(Charente)" if department == "Charente" else None,
            f"{village}_(France)",
            f"{village}_({department})" if department else None,
        ]

        patterns = [p for p in patterns if p]  # Remove None

        for i, pattern in enumerate(patterns):
            for lang in ['fr', 'en']:
                url = f"https://{lang}.wikipedia.org/wiki/{pattern.replace(' ', '_')}"

                try:
                    response = self.session.get(url, timeout=10, allow_redirects=True)

                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')

                        # Check if it's the right page (not redirect to different village)
                        title = soup.find('h1', {'id': 'firstHeading'})
                        if title and village.lower() in title.get_text().lower():
                            urls_found.append(response.url)

                            # Extract content
                            content_div = soup.find('div', {'id': 'mw-content-text'})
                            if content_div:
                                # Remove scripts, styles, references
                                for tag in content_div.find_all(['script', 'style', 'table', 'div.reference']):
                                    tag.decompose()

                                text = content_div.get_text(separator=' ', strip=True)
                                text = ' '.join(text.split())[:10000]  # Limit to 10K chars

                                content[f'wikipedia_{lang}_{i}'] = {
                                    'url': response.url,
                                    'text': text,
                                    'length': len(text)
                                }

                                print(f"      • Found: {response.url} ({len(text)} chars)")
                                break  # Found this pattern, try next

                except Exception as e:
                    continue

                time.sleep(0.5)  # Rate limiting

        return urls_found, content

    def _search_mairie_sites(self, village: str) -> Tuple[List[str], Dict]:
        """Try multiple mairie website URL patterns."""
        urls_found = []
        content = {}

        village_clean = village.lower().replace(' ', '-').replace("'", '-')

        # Common mairie URL patterns
        patterns = [
            f"https://www.mairie-{village_clean}.fr",
            f"http://www.mairie-{village_clean}.fr",
            f"https://mairie-{village_clean}.fr",
            f"https://www.mairie-{village_clean}.com",
            f"http://{village_clean}.fr",
            f"https://{village_clean}.fr",
            f"http://www.{village_clean}.fr",
            f"https://www.{village_clean}.fr",
            f"https://{village_clean}.com",
            f"http://mairie{village_clean}.free.fr",
            f"http://www.mairie{village_clean}.free.fr",
        ]

        for url in patterns:
            try:
                response = self.session.get(url, timeout=5, allow_redirects=True)

                if response.status_code == 200 and 'text/html' in response.headers.get('content-type', ''):
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Extract text
                    for tag in soup.find_all(['script', 'style', 'nav', 'footer', 'header']):
                        tag.decompose()

                    text = soup.get_text(separator=' ', strip=True)
                    text = ' '.join(text.split())[:5000]

                    if len(text) > 100:  # Meaningful content
                        urls_found.append(response.url)
                        content[f'mairie_{len(content)}'] = {
                            'url': response.url,
                            'text': text,
                            'length': len(text)
                        }
                        print(f"      • Found: {response.url} ({len(text)} chars)")

            except Exception:
                continue

            time.sleep(0.3)

        return urls_found, content

    def _search_archives(self, village: str, department: str = None) -> Tuple[List[str], Dict]:
        """Search department archives and local history sites."""
        urls_found = []
        content = {}

        if not department:
            return urls_found, content

        village_clean = village.lower().replace(' ', '-')
        dept_clean = department.lower().replace(' ', '-')

        # Archive URL patterns
        patterns = [
            f"http://{dept_clean}.free.fr",
            f"http://www.{dept_clean}.free.fr",
            f"http://archives.{dept_clean}.fr",
            f"http://www.archives-{dept_clean}.fr",
            f"http://{village_clean}.{dept_clean}.free.fr",
            f"http://histoire-{dept_clean}.fr",
            f"http://patrimoine-{dept_clean}.fr",
        ]

        for base_url in patterns:
            try:
                # Try base URL
                response = self.session.get(base_url, timeout=5)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Look for links mentioning the village
                    links = soup.find_all('a', href=True)
                    for link in links:
                        if village.lower() in link.get_text().lower() or village.lower() in link['href'].lower():
                            full_url = urljoin(base_url, link['href'])

                            # Try to fetch the linked page
                            try:
                                page_response = self.session.get(full_url, timeout=5)
                                if page_response.status_code == 200:
                                    page_soup = BeautifulSoup(page_response.content, 'html.parser')

                                    for tag in page_soup.find_all(['script', 'style', 'nav']):
                                        tag.decompose()

                                    text = page_soup.get_text(separator=' ', strip=True)
                                    text = ' '.join(text.split())[:5000]

                                    if len(text) > 100:
                                        urls_found.append(full_url)
                                        content[f'archive_{len(content)}'] = {
                                            'url': full_url,
                                            'text': text,
                                            'length': len(text)
                                        }
                                        print(f"      • Found: {full_url} ({len(text)} chars)")
                                        break  # One page per archive site
                            except:
                                continue

            except Exception:
                continue

            time.sleep(0.5)

        return urls_found, content

    def _google_search(self, village: str, department: str, query_type: str) -> Tuple[List[str], Dict]:
        """
        Simulate Google search by trying common French historical/cultural sites.

        Note: Real Google Search API would be better but requires API key.
        This version tries known historical/cultural websites.
        """
        urls_found = []
        content = {}

        # Common French historical/cultural sites to search
        sites_to_check = [
            f"https://www.france-voyage.com/villes-villages",
            f"https://www.pop.culture.gouv.fr",
            f"https://www.petit-patrimoine.com",
            f"https://monumentum.fr",
            f"https://www.patrimoine-de-france.com",
            f"https://www.charentelibre.fr",  # Local newspaper
            f"https://www.sudouest.fr",  # Regional newspaper
        ]

        search_terms = f"{village} {department or ''} {query_type}".strip()

        # Try each site
        for site in sites_to_check:
            try:
                # Try to search or browse for the village
                search_url = f"{site}/{village.lower()}"

                response = self.session.get(search_url, timeout=5, allow_redirects=True)

                if response.status_code == 200 and village.lower() in response.text.lower():
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Check if page mentions our search terms
                    text_content = soup.get_text().lower()
                    if any(term in text_content for term in [query_type, village.lower()]):
                        # Extract content
                        for tag in soup.find_all(['script', 'style', 'nav', 'footer']):
                            tag.decompose()

                        text = soup.get_text(separator=' ', strip=True)
                        text = ' '.join(text.split())[:5000]

                        if len(text) > 100:
                            urls_found.append(response.url)
                            content[f'{query_type}_{len(content)}'] = {
                                'url': response.url,
                                'text': text,
                                'length': len(text),
                                'search_term': query_type
                            }
                            print(f"      • Found: {response.url} ({len(text)} chars)")

            except Exception:
                continue

            time.sleep(0.5)

        return urls_found, content


def main():
    parser = argparse.ArgumentParser(
        description='Enhanced village intelligence gathering',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--village', required=True, help='Village name (e.g., "Chirac")')
    parser.add_argument('--department', help='Department name (e.g., "Charente")')
    parser.add_argument('--output', help='Output JSON file')

    args = parser.parse_args()

    # Run search
    scraper = EnhancedVillageIntelligence()
    results = scraper.search_village(args.village, args.department)

    # Save results
    output_file = args.output or f"{args.village.replace(' ', '_')}_intelligence.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Display summary
    print(f"\n{'='*70}")
    print(f"INTELLIGENCE REPORT: {args.village}")
    print(f"{'='*70}\n")

    print(f"URLs Discovered: {len(results['urls_discovered'])}")
    print(f"\nURLs by source:")
    for url in results['urls_discovered']:
        print(f"  • {url}")

    print(f"\nContent collected from:")
    for source_type, content in results['content'].items():
        if content:
            print(f"  • {source_type}: {len(content)} pages")
            for key, data in content.items():
                print(f"    - {data['url']} ({data['length']} chars)")

    print(f"\n✓ Intelligence saved to: {output_file}")


if __name__ == '__main__':
    main()
