#!/usr/bin/env python3
"""
Village Auto-Population System
Automatically gather ALL available data about French/Belgian villages for treasure hunting partnerships.

Scrapes multiple sources:
- Wikipedia (history, demographics, events)
- Mérimée database (monuments, heritage sites)
- Tourism websites
- Google Books (if available)

Uses Claude AI to structure raw text into actionable intelligence:
- Legends and folklore
- Historical events with dates
- Notable sites and monuments
- Treasure probability scoring
- Partnership pitch points

Goal: Pre-populate 10,000+ villages with impressive research to increase
village partnership conversion from 20% to 80%.

Usage:
    python village_auto_scraper.py --village "Azincourt" --lat 50.4667 --lng 2.1333
    python village_auto_scraper.py --village "Reims" --coordinates 49.2583,4.0317 --output reims.json
"""

import os
import sys
import json
import argparse
import time
from typing import Dict, List, Optional
from datetime import datetime
import requests
from bs4 import BeautifulSoup


# Import our modules
try:
    from merimee_api import MerimeeAPI
except ImportError:
    print("Error: merimee_api.py not found in current directory", file=sys.stderr)
    sys.exit(1)

try:
    from process_village_data import VillageDataProcessor
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False
    print("Warning: process_village_data.py not available or anthropic not installed", file=sys.stderr)


class VillageAutoScraper:
    """
    Orchestrates village data collection from multiple sources.
    """

    def __init__(self, anthropic_api_key: str = None):
        """
        Initialize the auto-scraper.

        Args:
            anthropic_api_key: API key for Claude (optional if ANTHROPIC_API_KEY set)
        """
        self.merimee = MerimeeAPI()

        if CLAUDE_AVAILABLE:
            try:
                self.processor = VillageDataProcessor(api_key=anthropic_api_key)
            except ValueError:
                print("Warning: Claude API key not found. Data will not be processed.", file=sys.stderr)
                self.processor = None
        else:
            self.processor = None

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def scrape_village(self, village_name: str, lat: float = None, lng: float = None,
                      department: str = None) -> Dict:
        """
        Complete village data collection pipeline.

        Args:
            village_name: Village name (e.g., "Azincourt", "Reims")
            lat: Latitude (optional but recommended)
            lng: Longitude (optional but recommended)
            department: Department name for disambiguation (optional)

        Returns:
            Complete village data dictionary
        """
        print(f"\n{'='*70}")
        print(f"AUTO-POPULATING VILLAGE DATA: {village_name}")
        print(f"{'='*70}\n")

        coordinates = {'lat': lat, 'lng': lng} if lat and lng else {}

        # Collect raw data from all sources
        raw_data = {
            'village_name': village_name,
            'coordinates': coordinates,
            'collection_date': datetime.now().isoformat(),
            'sources': {}
        }

        # 1. Wikipedia data
        print("📚 [1/4] Scraping Wikipedia...")
        wikipedia_text = self._scrape_wikipedia(village_name)
        raw_data['sources']['wikipedia'] = {
            'text': wikipedia_text,
            'length': len(wikipedia_text),
            'success': len(wikipedia_text) > 0
        }
        print(f"     ✓ Collected {len(wikipedia_text)} characters from Wikipedia")

        # 2. Mérimée monuments
        print("\n🏰 [2/4] Querying Mérimée database...")
        monuments = self._get_merimee_monuments(village_name, lat, lng, department)
        raw_data['sources']['merimee'] = {
            'monuments': monuments,
            'count': len(monuments),
            'success': len(monuments) > 0
        }
        print(f"     ✓ Found {len(monuments)} monuments in Mérimée database")

        # 3. Tourism websites
        print("\n🗺️  [3/4] Scraping tourism websites...")
        tourism_text = self._scrape_tourism_sites(village_name, department)
        raw_data['sources']['tourism'] = {
            'text': tourism_text,
            'length': len(tourism_text),
            'success': len(tourism_text) > 0
        }
        print(f"     ✓ Collected {len(tourism_text)} characters from tourism sites")

        # 4. Process with Claude AI (if available)
        print("\n🤖 [4/4] Processing with Claude AI...")
        if self.processor:
            combined_text = self._combine_source_texts(wikipedia_text, monuments, tourism_text)
            structured_data = self.processor.process_village(village_name, combined_text, coordinates)
            raw_data['processed_data'] = structured_data
            print(f"     ✓ AI processing complete")
        else:
            print(f"     ⚠ Claude AI not available - raw data only")
            raw_data['processed_data'] = None

        # Calculate completeness score
        raw_data['completeness_score'] = self._calculate_completeness(raw_data)

        print(f"\n{'='*70}")
        print(f"COLLECTION COMPLETE")
        print(f"{'='*70}")
        print(f"Data completeness: {raw_data['completeness_score']}/100")

        return raw_data

    def _scrape_wikipedia(self, village_name: str) -> str:
        """Scrape Wikipedia page for village."""
        # Try multiple URL formats
        urls_to_try = [
            f"https://fr.wikipedia.org/wiki/{village_name.replace(' ', '_')}",
            f"https://en.wikipedia.org/wiki/{village_name.replace(' ', '_')}",
        ]

        for url in urls_to_try:
            try:
                response = self.session.get(url, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Extract main content
                    content_div = soup.find('div', {'id': 'mw-content-text'})
                    if content_div:
                        # Remove unwanted elements
                        for element in content_div.find_all(['script', 'style', 'table', 'div.reference']):
                            element.decompose()

                        # Get text
                        text = content_div.get_text(separator=' ', strip=True)

                        # Clean up
                        text = ' '.join(text.split())  # Normalize whitespace

                        return text[:10000]  # Limit to 10K characters

            except Exception as e:
                continue

        return ""

    def _get_merimee_monuments(self, village_name: str, lat: float = None, lng: float = None,
                               department: str = None) -> List[Dict]:
        """Get monuments from Mérimée database."""
        monuments = []

        try:
            # Try by commune name first
            monuments = self.merimee.search_by_commune(village_name, department, max_results=50)

            # If no results and we have coordinates, try coordinate search
            if not monuments and lat and lng:
                monuments = self.merimee.search_by_coordinates(lat, lng, radius_km=2, max_results=50)

        except Exception as e:
            print(f"     Warning: Mérimée API error: {e}", file=sys.stderr)

        return monuments

    def _scrape_tourism_sites(self, village_name: str, department: str = None) -> str:
        """Scrape tourism websites for village info."""
        # This is a placeholder - in production you'd scrape specific tourism sites
        # For now, we'll do a simple search

        search_query = f"{village_name} {department or ''} tourisme histoire légende"

        # Try office de tourisme websites
        tourism_urls = [
            f"https://www.france-voyage.com/villes-villages/{village_name.lower().replace(' ', '-')}.htm",
        ]

        combined_text = ""

        for url in tourism_urls:
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Extract text from main content
                    for element in soup.find_all(['script', 'style', 'nav', 'footer']):
                        element.decompose()

                    text = soup.get_text(separator=' ', strip=True)
                    text = ' '.join(text.split())

                    combined_text += " " + text[:5000]

            except Exception:
                continue

        return combined_text.strip()

    def _combine_source_texts(self, wikipedia: str, monuments: List[Dict], tourism: str) -> str:
        """Combine all source texts into one document for Claude processing."""
        combined = []

        # Wikipedia content
        if wikipedia:
            combined.append("=== WIKIPEDIA ===")
            combined.append(wikipedia)
            combined.append("")

        # Mérimée monuments
        if monuments:
            combined.append("=== MONUMENTS (MÉRIMÉE DATABASE) ===")
            for m in monuments[:10]:  # Limit to top 10
                combined.append(f"\nMONUMENT: {m.get('name', 'Unknown')}")
                combined.append(f"Type: {', '.join(m.get('denomination', []))}")
                combined.append(f"Description: {m.get('description', '')}")
                combined.append(f"History: {m.get('history', '')}")
                combined.append(f"Period: {', '.join(m.get('period', []))}")
                combined.append(f"Protection: {m.get('protection', {}).get('status', '')}")
                combined.append("")

        # Tourism content
        if tourism:
            combined.append("=== TOURISM INFORMATION ===")
            combined.append(tourism)

        return "\n".join(combined)

    def _calculate_completeness(self, raw_data: Dict) -> int:
        """Calculate data completeness score (0-100)."""
        score = 0

        # Wikipedia (30 points)
        wiki_len = raw_data['sources']['wikipedia']['length']
        if wiki_len > 5000:
            score += 30
        elif wiki_len > 2000:
            score += 20
        elif wiki_len > 500:
            score += 10

        # Mérimée monuments (30 points)
        monument_count = raw_data['sources']['merimee']['count']
        if monument_count >= 5:
            score += 30
        elif monument_count >= 3:
            score += 20
        elif monument_count >= 1:
            score += 10

        # Tourism (20 points)
        tourism_len = raw_data['sources']['tourism']['length']
        if tourism_len > 2000:
            score += 20
        elif tourism_len > 500:
            score += 10

        # Claude processing (20 points)
        if raw_data.get('processed_data'):
            processed = raw_data['processed_data']
            if processed.get('legends') or processed.get('historical_events') or processed.get('notable_sites'):
                score += 20

        return min(score, 100)


def export_to_json(village_data: Dict, output_file: str):
    """Export village data to JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(village_data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Village data saved to: {output_file}")


def display_summary(village_data: Dict):
    """Display village data summary."""
    print(f"\n{'='*70}")
    print(f"VILLAGE DATA SUMMARY")
    print(f"{'='*70}\n")

    village_name = village_data.get('village_name', 'Unknown')
    print(f"Village: {village_name}")

    coords = village_data.get('coordinates', {})
    if coords.get('lat') and coords.get('lng'):
        print(f"Coordinates: {coords['lat']}, {coords['lng']}")

    print(f"Collection Date: {village_data.get('collection_date', 'Unknown')}")
    print(f"Completeness Score: {village_data.get('completeness_score', 0)}/100")

    print(f"\nDATA SOURCES:")
    print(f"  Wikipedia: {village_data['sources']['wikipedia']['length']} characters")
    print(f"  Mérimée: {village_data['sources']['merimee']['count']} monuments")
    print(f"  Tourism: {village_data['sources']['tourism']['length']} characters")

    if village_data.get('processed_data'):
        processed = village_data['processed_data']
        print(f"\nPROCESSED DATA:")
        print(f"  Legends: {len(processed.get('legends', []))}")
        print(f"  Historical Events: {len(processed.get('historical_events', []))}")
        print(f"  Notable Sites: {len(processed.get('notable_sites', []))}")

        treasure = processed.get('treasure_probability', {})
        print(f"  Treasure Probability: {treasure.get('score', 0)}/100 ({treasure.get('category', 'Unknown')})")

        if processed.get('summary'):
            print(f"\nPITCH SUMMARY:")
            print(f"  {processed['summary']}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Auto-populate village data from multiple sources',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # With coordinates (recommended)
  python village_auto_scraper.py --village "Azincourt" --lat 50.4667 --lng 2.1333

  # Without coordinates
  python village_auto_scraper.py --village "Reims" --department "Marne"

  # With output file
  python village_auto_scraper.py --village "Lyon" --output lyon_complete.json

Environment:
  ANTHROPIC_API_KEY should be set for Claude AI processing (optional but recommended)
        """
    )

    parser.add_argument('--village', type=str, required=True, help='Village name')
    parser.add_argument('--lat', type=float, help='Latitude')
    parser.add_argument('--lng', type=float, help='Longitude')
    parser.add_argument('--coordinates', type=str, help='Coordinates as "lat,lng"')
    parser.add_argument('--department', type=str, help='Department name (for disambiguation)')
    parser.add_argument('--output', type=str, help='Output JSON file')
    parser.add_argument('--api-key', type=str, help='Anthropic API key')

    args = parser.parse_args()

    # Parse coordinates if provided
    lat, lng = args.lat, args.lng
    if args.coordinates:
        try:
            lat, lng = map(float, args.coordinates.split(','))
        except ValueError:
            print("Error: Coordinates must be in format 'lat,lng'", file=sys.stderr)
            sys.exit(1)

    # Set output file
    if args.output:
        output_file = args.output
    else:
        village_safe = args.village.replace(' ', '_').replace('/', '_')
        output_file = f"{village_safe}_complete.json"

    # Create scraper
    scraper = VillageAutoScraper(anthropic_api_key=args.api_key)

    # Scrape village
    village_data = scraper.scrape_village(
        village_name=args.village,
        lat=lat,
        lng=lng,
        department=args.department
    )

    # Export
    export_to_json(village_data, output_file)

    # Display summary
    display_summary(village_data)

    print(f"\n✓ Success! Complete data for {args.village} collected and saved.")


if __name__ == '__main__':
    main()
