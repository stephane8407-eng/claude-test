#!/usr/bin/env python3
"""
Wikipedia API Battle Scraper
Uses Wikipedia's official MediaWiki API to extract battle data.
More reliable than HTML scraping and respects Wikipedia's terms of service.

Usage:
    python wikipedia_api_scraper.py --page "List_of_battles_1401–1500"
    python wikipedia_api_scraper.py --pages pages.txt --output battles.csv
"""

import requests
import csv
import argparse
import re
import time
import sys
from typing import List, Dict, Optional
from datetime import datetime
from bs4 import BeautifulSoup


class WikipediaAPIBattleScraper:
    """Scrapes battle data using Wikipedia's MediaWiki API."""

    def __init__(self, output_file: str = None):
        """Initialize the API scraper."""
        self.api_url = "https://en.wikipedia.org/w/api.php"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ChasseurDeTresors/1.0 (Educational historical research tool; Contact: treasure.research@example.com)'
        })

        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"battles_{timestamp}.csv"

        self.output_file = output_file
        self.battles = []

    def fetch_page_html(self, page_title: str, max_retries: int = 3) -> Optional[str]:
        """
        Fetch Wikipedia page HTML using MediaWiki API.

        Args:
            page_title: Wikipedia page title (e.g., "List_of_battles_1401–1500")
            max_retries: Maximum retry attempts

        Returns:
            Page HTML content or None if failed
        """
        params = {
            'action': 'parse',
            'page': page_title,
            'format': 'json',
            'prop': 'text',
            'disableeditsection': 1,
            'disabletoc': 1
        }

        for attempt in range(max_retries):
            try:
                print(f"Fetching via API: {page_title}" + (f" (attempt {attempt + 1}/{max_retries})" if attempt > 0 else ""))
                response = self.session.get(self.api_url, params=params, timeout=30)
                response.raise_for_status()

                data = response.json()

                # Check for errors
                if 'error' in data:
                    print(f"  API Error: {data['error'].get('info', 'Unknown error')}", file=sys.stderr)
                    return None

                # Extract HTML from parse result
                if 'parse' in data and 'text' in data['parse']:
                    html_content = data['parse']['text']['*']
                    print(f"  ✓ Fetched {len(html_content)} characters")
                    return html_content

                print("  Unexpected API response format", file=sys.stderr)
                return None

            except requests.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"  Error: {e}. Retrying in {wait_time}s...", file=sys.stderr)
                    time.sleep(wait_time)
                else:
                    print(f"Error fetching {page_title} after {max_retries} attempts: {e}", file=sys.stderr)
                    return None

        return None

    def clean_text(self, text: str) -> str:
        """Clean extracted text."""
        if not text:
            return ""

        # Remove reference brackets
        text = re.sub(r'\[\d+\]', '', text)
        text = re.sub(r'\[citation needed\]', '', text, flags=re.IGNORECASE)

        # Remove HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&ndash;', '–')
        text = text.replace('&mdash;', '—')

        # Normalize whitespace
        text = ' '.join(text.split())

        return text.strip()

    def extract_year(self, date_str: str) -> Optional[str]:
        """Extract year from date string."""
        if not date_str:
            return None

        # Look for 4-digit years
        year_match = re.search(r'\b(\d{4})\b', date_str)
        if year_match:
            return year_match.group(1)

        # Look for 3-digit years
        year_match = re.search(r'\b(\d{3})\b', date_str)
        if year_match:
            return year_match.group(1)

        return date_str.strip()

    def extract_battles_from_table(self, table) -> List[Dict[str, str]]:
        """Extract battle data from a Wikipedia table."""
        battles = []

        # Find header row
        headers = []
        header_row = table.find('tr')
        if header_row:
            for th in header_row.find_all(['th', 'td']):
                header_text = self.clean_text(th.get_text()).lower()
                headers.append(header_text)

        if not headers:
            return battles

        print(f"    Headers: {headers[:5]}...")  # Show first 5 headers

        # Map column names
        column_mapping = {
            'name': ['name', 'battle', 'conflict', 'engagement'],
            'date': ['date', 'year', 'time', 'when'],
            'location': ['location', 'place', 'site', 'where'],
            'participants': ['belligerents', 'combatants', 'participants', 'forces', 'sides'],
            'outcome': ['result', 'outcome', 'victor', 'winner']
        }

        # Find column indices
        field_indices = {}
        for field, possible_names in column_mapping.items():
            for i, header in enumerate(headers):
                if any(name in header for name in possible_names):
                    field_indices[field] = i
                    break

        print(f"    Mapped fields: {list(field_indices.keys())}")

        # Extract data rows
        rows = table.find_all('tr')[1:]  # Skip header

        for row in rows:
            cells = row.find_all(['td', 'th'])

            if len(cells) < 2:
                continue

            battle = {
                'name': '',
                'year': '',
                'date': '',
                'location': '',
                'participants': '',
                'outcome': ''
            }

            # Extract name
            if 'name' in field_indices and field_indices['name'] < len(cells):
                name_cell = cells[field_indices['name']]
                link = name_cell.find('a')
                if link:
                    battle['name'] = self.clean_text(link.get_text())
                else:
                    battle['name'] = self.clean_text(name_cell.get_text())

            # Extract date
            if 'date' in field_indices and field_indices['date'] < len(cells):
                date_text = self.clean_text(cells[field_indices['date']].get_text())
                battle['date'] = date_text
                battle['year'] = self.extract_year(date_text)

            # Extract location
            if 'location' in field_indices and field_indices['location'] < len(cells):
                battle['location'] = self.clean_text(cells[field_indices['location']].get_text())

            # Extract participants
            if 'participants' in field_indices and field_indices['participants'] < len(cells):
                participants_parts = []
                start_idx = field_indices['participants']
                for i in range(start_idx, min(start_idx + 3, len(cells))):
                    text = self.clean_text(cells[i].get_text())
                    if text and text.lower() not in ['vs', 'vs.', 'v.', 'versus']:
                        participants_parts.append(text)
                battle['participants'] = ' vs '.join(participants_parts[:2]) if len(participants_parts) > 1 else participants_parts[0] if participants_parts else ''

            # Extract outcome
            if 'outcome' in field_indices and field_indices['outcome'] < len(cells):
                battle['outcome'] = self.clean_text(cells[field_indices['outcome']].get_text())

            if battle['name']:
                battles.append(battle)

        return battles

    def scrape_page(self, page_title: str) -> int:
        """
        Scrape battles from a Wikipedia page.

        Args:
            page_title: Wikipedia page title

        Returns:
            Number of battles extracted
        """
        html = self.fetch_page_html(page_title)
        if not html:
            return 0

        soup = BeautifulSoup(html, 'html.parser')

        # Find all tables with class 'wikitable'
        tables = soup.find_all('table', {'class': 'wikitable'})

        print(f"  Found {len(tables)} tables")

        count = 0
        for i, table in enumerate(tables):
            print(f"  Processing table {i+1}/{len(tables)}...")
            battles = self.extract_battles_from_table(table)
            self.battles.extend(battles)
            count += len(battles)
            print(f"    Extracted {len(battles)} battles")

        return count

    def scrape_pages(self, page_titles: List[str], delay: float = 1.0):
        """
        Scrape battles from multiple Wikipedia pages.

        Args:
            page_titles: List of Wikipedia page titles
            delay: Delay between requests in seconds
        """
        total = 0
        for i, page_title in enumerate(page_titles):
            print(f"\nProcessing page {i+1}/{len(page_titles)}: {page_title}")
            count = self.scrape_page(page_title)
            total += count
            print(f"  Extracted {count} battles from this page (total: {total})")

            if i < len(page_titles) - 1:
                time.sleep(delay)

        print(f"\n✓ Total battles extracted: {total}")

    def export_to_csv(self) -> str:
        """Export extracted battles to CSV file."""
        if not self.battles:
            print("No battles to export!", file=sys.stderr)
            return None

        print(f"\nExporting {len(self.battles)} battles to {self.output_file}")

        fieldnames = ['name', 'year', 'date', 'location', 'participants', 'outcome']

        with open(self.output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.battles)

        print(f"✓ Exported to {self.output_file}")
        return self.output_file

    def get_battles(self) -> List[Dict[str, str]]:
        """Return the list of extracted battles."""
        return self.battles


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Scrape battle data using Wikipedia MediaWiki API.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape a single page
  python wikipedia_api_scraper.py --page "List_of_battles_1401–1500"

  # Scrape multiple pages from a file (one page title per line)
  python wikipedia_api_scraper.py --pages page_titles.txt

  # Specify output file
  python wikipedia_api_scraper.py --page "List_of_battles_1701–1800" --output battles_1700s.csv

  # Add delay between requests
  python wikipedia_api_scraper.py --pages titles.txt --delay 2.0
        """
    )

    parser.add_argument('--page', type=str, help='Single Wikipedia page title to scrape')
    parser.add_argument('--pages', type=str, help='Text file containing page titles (one per line)')
    parser.add_argument('--output', type=str, help='Output CSV file (default: battles_TIMESTAMP.csv)')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests in seconds (default: 1.0)')

    args = parser.parse_args()

    # Validate input
    if not args.page and not args.pages:
        parser.error("Must specify either --page or --pages")

    if args.page and args.pages:
        parser.error("Cannot specify both --page and --pages")

    # Collect page titles
    page_titles = []
    if args.page:
        page_titles = [args.page]
    elif args.pages:
        try:
            with open(args.pages, 'r') as f:
                page_titles = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
        except FileNotFoundError:
            print(f"Error: File '{args.pages}' not found", file=sys.stderr)
            sys.exit(1)

    if not page_titles:
        print("Error: No page titles to process", file=sys.stderr)
        sys.exit(1)

    print(f"Wikipedia API Battle Scraper")
    print(f"============================")
    print(f"Pages to process: {len(page_titles)}")
    print(f"Output file: {args.output or 'battles_TIMESTAMP.csv'}")
    print(f"Request delay: {args.delay}s\n")

    # Create scraper and run
    scraper = WikipediaAPIBattleScraper(output_file=args.output)
    scraper.scrape_pages(page_titles, delay=args.delay)

    # Export results
    output_file = scraper.export_to_csv()

    if output_file:
        print(f"\n✓ Success! Extracted {len(scraper.get_battles())} battles")
        print(f"✓ Data saved to: {output_file}")
        sys.exit(0)
    else:
        print("\n✗ Failed to export data", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
