#!/usr/bin/env python3
"""
Mérimée API Integration
Access France's official cultural heritage database (POP - Plateforme Ouverte du Patrimoine)
containing 50,000+ classified monuments and historical sites.

The Mérimée database includes:
- Historical monuments (castles, churches, abbeys, fortifications)
- Architectural heritage
- GPS coordinates
- Historical descriptions
- Protection status (Classé, Inscrit, etc.)

API Documentation: https://www.pop.culture.gouv.fr
API Endpoint: https://api.pop.culture.gouv.fr

Usage:
    python merimee_api.py --commune "Agincourt" --output monuments.json
    python merimee_api.py --coordinates 50.4667,2.1333 --radius 10 --output area_monuments.json
"""

import requests
import json
import argparse
import time
import sys
from typing import List, Dict, Optional
from datetime import datetime


class MerimeeAPI:
    """
    Interface to France's Mérimée cultural heritage database.
    """

    def __init__(self):
        """Initialize the Mérimée API client."""
        self.api_base = "https://api.pop.culture.gouv.fr"
        self.search_endpoint = f"{self.api_base}/search/merimee"

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ChasseurDeTresors/1.0 (Historical research tool)',
            'Accept': 'application/json'
        })

    def search_by_commune(self, commune: str, department: str = None, max_results: int = 100) -> List[Dict]:
        """
        Search for monuments in a specific commune (village/town).

        Args:
            commune: Commune name (e.g., "Agincourt", "Azincourt")
            department: Optional department code or name for disambiguation
            max_results: Maximum number of results to return

        Returns:
            List of monument dictionaries
        """
        print(f"Searching Mérimée database for commune: {commune}")

        params = {
            'q': commune,
            'size': max_results
        }

        if department:
            params['qf'] = f'DPT:"{department}"'

        try:
            response = self.session.get(self.search_endpoint, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if 'hits' in data and 'hits' in data['hits']:
                monuments = data['hits']['hits']
                print(f"  ✓ Found {len(monuments)} monuments")
                return [self._parse_monument(m) for m in monuments]
            else:
                print(f"  No monuments found")
                return []

        except requests.RequestException as e:
            print(f"  Error querying API: {e}", file=sys.stderr)
            return []

    def search_by_coordinates(self, lat: float, lng: float, radius_km: float = 5, max_results: int = 100) -> List[Dict]:
        """
        Search for monuments near GPS coordinates.

        Args:
            lat: Latitude
            lng: Longitude
            radius_km: Search radius in kilometers
            max_results: Maximum number of results

        Returns:
            List of monument dictionaries
        """
        print(f"Searching monuments within {radius_km}km of ({lat}, {lng})")

        # Convert radius to degrees (approximate)
        radius_deg = radius_km / 111.0  # 1 degree ≈ 111km

        params = {
            'geo_distance': f'{radius_km}km',
            'lat': lat,
            'lon': lng,
            'size': max_results
        }

        try:
            response = self.session.get(self.search_endpoint, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if 'hits' in data and 'hits' in data['hits']:
                monuments = data['hits']['hits']
                print(f"  ✓ Found {len(monuments)} monuments")
                return [self._parse_monument(m) for m in monuments]
            else:
                print(f"  No monuments found")
                return []

        except requests.RequestException as e:
            print(f"  Error querying API: {e}", file=sys.stderr)
            return []

    def search_by_text(self, query: str, max_results: int = 50) -> List[Dict]:
        """
        Full-text search across monument descriptions.

        Args:
            query: Search query (e.g., "castle", "church", "fortification")
            max_results: Maximum results

        Returns:
            List of monument dictionaries
        """
        print(f"Full-text search: {query}")

        params = {
            'q': query,
            'size': max_results
        }

        try:
            response = self.session.get(self.search_endpoint, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if 'hits' in data and 'hits' in data['hits']:
                monuments = data['hits']['hits']
                print(f"  ✓ Found {len(monuments)} monuments")
                return [self._parse_monument(m) for m in monuments]
            else:
                print(f"  No monuments found")
                return []

        except requests.RequestException as e:
            print(f"  Error querying API: {e}", file=sys.stderr)
            return []

    def _parse_monument(self, raw_monument: Dict) -> Dict:
        """
        Parse raw API response into standardized monument dictionary.

        Args:
            raw_monument: Raw monument data from API

        Returns:
            Cleaned monument dictionary
        """
        source = raw_monument.get('_source', {})

        monument = {
            'id': raw_monument.get('_id', ''),
            'reference': source.get('REF', ''),
            'name': source.get('TICO', ''),  # Titre courant
            'denomination': source.get('DENO', []),  # Type (château, église, etc.)
            'description': source.get('DESC', ''),
            'history': source.get('HIST', ''),
            'commune': source.get('COM', ''),
            'department': source.get('DPT', ''),
            'region': source.get('REG', ''),
            'address': source.get('ADRS', ''),
            'coordinates': {
                'latitude': source.get('POP_COORDONNEES', {}).get('lat'),
                'longitude': source.get('POP_COORDONNEES', {}).get('lon')
            },
            'protection': {
                'status': source.get('PROT', ''),  # Protection status
                'date': source.get('DPRO', '')     # Protection date
            },
            'period': source.get('SCLE', []),  # Century/period
            'author': source.get('AUTR', []),  # Architect/creator
            'images': source.get('MEMOIRE', []),  # Image references
            'url': source.get('POP_CONTIENT_GEOLOCALISATION', {}).get('url', ''),
            'treasure_relevance': self._calculate_treasure_relevance(source)
        }

        return monument

    def _calculate_treasure_relevance(self, source: Dict) -> Dict:
        """
        Calculate treasure hunting relevance score for a monument.

        Args:
            source: Raw monument source data

        Returns:
            Dictionary with score and reasoning
        """
        score = 0
        reasons = []

        # Check denomination (type of monument)
        deno = ' '.join(source.get('DENO', [])).lower()

        if any(x in deno for x in ['château', 'castle', 'fort']):
            score += 30
            reasons.append("Castle/fortification (high treasure probability)")

        if any(x in deno for x in ['abbaye', 'abbey', 'monastère', 'monastery', 'prieuré']):
            score += 25
            reasons.append("Religious site (often pillaged/treasures hidden)")

        if any(x in deno for x in ['église', 'church', 'cathédrale', 'cathedral']):
            score += 15
            reasons.append("Church (religious artifacts)")

        # Check period (older = more interesting)
        periods = source.get('SCLE', [])
        if any(p for p in periods if '12e' in str(p) or '13e' in str(p) or '14e' in str(p) or '15e' in str(p)):
            score += 20
            reasons.append("Medieval period (1100-1500)")

        # Check protection status (higher protection = more significant)
        prot = source.get('PROT', '').lower()
        if 'classé' in prot:
            score += 15
            reasons.append("Classified monument (high historical significance)")

        # Check description for treasure-related keywords
        desc = (source.get('DESC', '') + ' ' + source.get('HIST', '')).lower()
        if any(x in desc for x in ['trésor', 'treasure', 'caché', 'hidden', 'guerre', 'war', 'siège', 'siege']):
            score += 10
            reasons.append("Historical mention of treasures/conflict")

        return {
            'score': min(score, 100),  # Cap at 100
            'reasons': reasons,
            'category': 'High' if score >= 60 else 'Medium' if score >= 30 else 'Low'
        }

    def get_monument_details(self, reference: str) -> Optional[Dict]:
        """
        Get detailed information about a specific monument by reference ID.

        Args:
            reference: Monument reference (e.g., "PA00078445")

        Returns:
            Detailed monument dictionary or None
        """
        print(f"Fetching details for monument: {reference}")

        endpoint = f"{self.api_base}/notice/merimee/{reference}"

        try:
            response = self.session.get(endpoint, timeout=30)
            response.raise_for_status()

            data = response.json()
            print(f"  ✓ Retrieved details")
            return self._parse_monument({'_source': data, '_id': reference})

        except requests.RequestException as e:
            print(f"  Error fetching details: {e}", file=sys.stderr)
            return None


def export_to_json(monuments: List[Dict], output_file: str):
    """Export monuments to JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'count': len(monuments),
            'generated': datetime.now().isoformat(),
            'monuments': monuments
        }, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Exported {len(monuments)} monuments to {output_file}")


def export_to_csv(monuments: List[Dict], output_file: str):
    """Export monuments to CSV file."""
    import csv

    if not monuments:
        print("No monuments to export", file=sys.stderr)
        return

    fieldnames = ['name', 'denomination', 'commune', 'department', 'latitude', 'longitude',
                  'protection_status', 'period', 'treasure_score', 'treasure_category']

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for m in monuments:
            writer.writerow({
                'name': m.get('name', ''),
                'denomination': ', '.join(m.get('denomination', [])),
                'commune': m.get('commune', ''),
                'department': m.get('department', ''),
                'latitude': m.get('coordinates', {}).get('latitude', ''),
                'longitude': m.get('coordinates', {}).get('longitude', ''),
                'protection_status': m.get('protection', {}).get('status', ''),
                'period': ', '.join(m.get('period', [])),
                'treasure_score': m.get('treasure_relevance', {}).get('score', 0),
                'treasure_category': m.get('treasure_relevance', {}).get('category', '')
            })

    print(f"✓ Exported {len(monuments)} monuments to {output_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Search French Mérimée cultural heritage database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search by commune name
  python merimee_api.py --commune "Azincourt" --output azincourt_monuments.json

  # Search with department for disambiguation
  python merimee_api.py --commune "Saint-Denis" --department "Seine-Saint-Denis"

  # Search by coordinates (within 10km radius)
  python merimee_api.py --coordinates 50.4667,2.1333 --radius 10

  # Full-text search
  python merimee_api.py --search "château médiéval" --output castles.json

  # Export to CSV instead of JSON
  python merimee_api.py --commune "Reims" --format csv --output reims_monuments.csv
        """
    )

    parser.add_argument('--commune', type=str, help='Commune (village/town) name')
    parser.add_argument('--department', type=str, help='Department code or name (for disambiguation)')
    parser.add_argument('--coordinates', type=str, help='GPS coordinates as "lat,lng"')
    parser.add_argument('--radius', type=float, default=5.0, help='Search radius in km (default: 5)')
    parser.add_argument('--search', type=str, help='Full-text search query')
    parser.add_argument('--max-results', type=int, default=100, help='Maximum results (default: 100)')
    parser.add_argument('--output', type=str, help='Output file (default: monuments_TIMESTAMP.json)')
    parser.add_argument('--format', choices=['json', 'csv'], default='json', help='Output format (default: json)')

    args = parser.parse_args()

    # Validate input
    if not any([args.commune, args.coordinates, args.search]):
        parser.error("Must specify --commune, --coordinates, or --search")

    # Set output file
    if args.output:
        output_file = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = args.format
        output_file = f"monuments_{timestamp}.{ext}"

    print(f"Mérimée Cultural Heritage Database Search")
    print(f"==========================================\n")

    # Create API client
    api = MerimeeAPI()

    # Execute search
    monuments = []

    if args.commune:
        monuments = api.search_by_commune(args.commune, args.department, args.max_results)
    elif args.coordinates:
        try:
            lat, lng = map(float, args.coordinates.split(','))
            monuments = api.search_by_coordinates(lat, lng, args.radius, args.max_results)
        except ValueError:
            print("Error: Coordinates must be in format 'lat,lng'", file=sys.stderr)
            sys.exit(1)
    elif args.search:
        monuments = api.search_by_text(args.search, args.max_results)

    if not monuments:
        print("\n✗ No monuments found")
        sys.exit(1)

    # Display summary
    print(f"\n{'='*60}")
    print(f"RESULTS SUMMARY")
    print(f"{'='*60}")
    print(f"Total monuments found: {len(monuments)}")

    # Show treasure relevance distribution
    high = sum(1 for m in monuments if m.get('treasure_relevance', {}).get('category') == 'High')
    medium = sum(1 for m in monuments if m.get('treasure_relevance', {}).get('category') == 'Medium')
    low = sum(1 for m in monuments if m.get('treasure_relevance', {}).get('category') == 'Low')

    print(f"\nTreasure Hunting Relevance:")
    print(f"  High:   {high} monuments")
    print(f"  Medium: {medium} monuments")
    print(f"  Low:    {low} monuments")

    # Show top monuments by treasure score
    print(f"\nTop 5 Monuments by Treasure Score:")
    top_monuments = sorted(monuments, key=lambda m: m.get('treasure_relevance', {}).get('score', 0), reverse=True)[:5]

    for i, m in enumerate(top_monuments, 1):
        score = m.get('treasure_relevance', {}).get('score', 0)
        name = m.get('name', 'Unknown')
        commune = m.get('commune', '')
        print(f"  {i}. {name} ({commune}) - Score: {score}/100")

    # Export results
    if args.format == 'json':
        export_to_json(monuments, output_file)
    else:
        export_to_csv(monuments, output_file)

    print(f"\n✓ Success! Found {len(monuments)} monuments")
    print(f"✓ Data saved to: {output_file}")


if __name__ == '__main__':
    main()
