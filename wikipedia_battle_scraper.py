#!/usr/bin/env python3
"""
Wikipedia Battle Scraper
Extracts battle data from Wikipedia battle list pages and exports to CSV.

Usage:
    python wikipedia_battle_scraper.py --url "https://en.wikipedia.org/wiki/List_of_battles_1401–1500"
    python wikipedia_battle_scraper.py --urls urls.txt --output battles.csv
"""

import requests
from bs4 import BeautifulSoup
import csv
import argparse
import re
from typing import List, Dict, Optional
from datetime import datetime
import time
import sys


class WikipediaBattleScraper:
    """Scrapes battle data from Wikipedia battle list pages."""

    def __init__(self, output_file: str = None):
        """
        Initialize the scraper.

        Args:
            output_file: Path to output CSV file (default: battles_TIMESTAMP.csv)
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"battles_{timestamp}.csv"

        self.output_file = output_file
        self.battles = []

    def fetch_page(self, url: str, max_retries: int = 3) -> Optional[BeautifulSoup]:
        """
        Fetch a Wikipedia page and return BeautifulSoup object.

        Args:
            url: Wikipedia page URL
            max_retries: Maximum number of retry attempts

        Returns:
            BeautifulSoup object or None if failed
        """
        for attempt in range(max_retries):
            try:
                print(f"Fetching: {url}" + (f" (attempt {attempt + 1}/{max_retries})" if attempt > 0 else ""))
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            except requests.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"  Error: {e}. Retrying in {wait_time}s...", file=sys.stderr)
                    time.sleep(wait_time)
                else:
                    print(f"Error fetching {url} after {max_retries} attempts: {e}", file=sys.stderr)
                    return None

    def extract_year(self, date_str: str) -> Optional[str]:
        """
        Extract year from date string.

        Args:
            date_str: Date string from Wikipedia

        Returns:
            Year as string or original string if no year found
        """
        if not date_str:
            return None

        # Look for 4-digit years
        year_match = re.search(r'\b(\d{4})\b', date_str)
        if year_match:
            return year_match.group(1)

        # Look for 3-digit years (e.g., 732)
        year_match = re.search(r'\b(\d{3})\b', date_str)
        if year_match:
            return year_match.group(1)

        return date_str.strip()

    def clean_text(self, text: str) -> str:
        """
        Clean extracted text by removing references, extra whitespace, etc.

        Args:
            text: Raw text

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove reference brackets [1], [2], etc.
        text = re.sub(r'\[\d+\]', '', text)

        # Remove citation needed tags
        text = re.sub(r'\[citation needed\]', '', text, flags=re.IGNORECASE)

        # Normalize whitespace
        text = ' '.join(text.split())

        return text.strip()

    def extract_battles_from_table(self, table) -> List[Dict[str, str]]:
        """
        Extract battle data from a Wikipedia table.

        Args:
            table: BeautifulSoup table element

        Returns:
            List of battle dictionaries
        """
        battles = []

        # Find header row to identify columns
        headers = []
        header_row = table.find('tr')
        if header_row:
            for th in header_row.find_all(['th', 'td']):
                header_text = self.clean_text(th.get_text()).lower()
                headers.append(header_text)

        print(f"  Found headers: {headers}")

        # Map common column names to our standard fields
        column_mapping = {
            'name': ['name', 'battle', 'conflict'],
            'date': ['date', 'year', 'time'],
            'location': ['location', 'place', 'site'],
            'participants': ['belligerents', 'combatants', 'participants', 'forces'],
            'outcome': ['result', 'outcome', 'victor', 'winner']
        }

        # Find which columns map to which fields
        field_indices = {}
        for field, possible_names in column_mapping.items():
            for i, header in enumerate(headers):
                if any(name in header for name in possible_names):
                    field_indices[field] = i
                    break

        print(f"  Mapped columns: {field_indices}")

        # Extract data rows
        rows = table.find_all('tr')[1:]  # Skip header row

        for row in rows:
            cells = row.find_all(['td', 'th'])

            if len(cells) < 2:  # Skip rows with too few cells
                continue

            battle = {
                'name': '',
                'year': '',
                'date': '',
                'location': '',
                'participants': '',
                'outcome': ''
            }

            # Extract data based on column mapping
            if 'name' in field_indices and field_indices['name'] < len(cells):
                name_cell = cells[field_indices['name']]
                # Try to get link text first (usually more accurate)
                link = name_cell.find('a')
                if link:
                    battle['name'] = self.clean_text(link.get_text())
                else:
                    battle['name'] = self.clean_text(name_cell.get_text())

            if 'date' in field_indices and field_indices['date'] < len(cells):
                date_text = self.clean_text(cells[field_indices['date']].get_text())
                battle['date'] = date_text
                battle['year'] = self.extract_year(date_text)

            if 'location' in field_indices and field_indices['location'] < len(cells):
                battle['location'] = self.clean_text(cells[field_indices['location']].get_text())

            if 'participants' in field_indices and field_indices['participants'] < len(cells):
                # For participants, there might be multiple columns (e.g., side 1 vs side 2)
                participants_parts = []
                start_idx = field_indices['participants']
                # Collect next few columns that might be participants
                for i in range(start_idx, min(start_idx + 3, len(cells))):
                    text = self.clean_text(cells[i].get_text())
                    if text and text.lower() not in ['vs', 'vs.', 'v.', 'versus']:
                        participants_parts.append(text)
                battle['participants'] = ' vs '.join(participants_parts[:2]) if len(participants_parts) > 1 else participants_parts[0] if participants_parts else ''

            if 'outcome' in field_indices and field_indices['outcome'] < len(cells):
                battle['outcome'] = self.clean_text(cells[field_indices['outcome']].get_text())

            # Only add if we have at least a name
            if battle['name']:
                battles.append(battle)

        return battles

    def scrape_url(self, url: str) -> int:
        """
        Scrape battles from a Wikipedia URL.

        Args:
            url: Wikipedia page URL

        Returns:
            Number of battles extracted
        """
        soup = self.fetch_page(url)
        if not soup:
            return 0

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

    def scrape_urls(self, urls: List[str], delay: float = 1.0):
        """
        Scrape battles from multiple Wikipedia URLs.

        Args:
            urls: List of Wikipedia page URLs
            delay: Delay between requests in seconds (be respectful!)
        """
        total = 0
        for i, url in enumerate(urls):
            print(f"\nProcessing URL {i+1}/{len(urls)}")
            count = self.scrape_url(url)
            total += count
            print(f"  Extracted {count} battles from this page (total: {total})")

            # Be respectful with delays between requests
            if i < len(urls) - 1:
                time.sleep(delay)

        print(f"\nTotal battles extracted: {total}")

    def export_to_csv(self) -> str:
        """
        Export extracted battles to CSV file.

        Returns:
            Path to output file
        """
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
    """Main entry point for command-line usage."""
    parser = argparse.ArgumentParser(
        description='Scrape battle data from Wikipedia battle list pages.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape a single URL
  python wikipedia_battle_scraper.py --url "https://en.wikipedia.org/wiki/List_of_battles_1401–1500"

  # Scrape multiple URLs from a file (one URL per line)
  python wikipedia_battle_scraper.py --urls urls.txt

  # Specify output file
  python wikipedia_battle_scraper.py --url "..." --output my_battles.csv

  # Add delay between requests (seconds)
  python wikipedia_battle_scraper.py --urls urls.txt --delay 2.0
        """
    )

    parser.add_argument('--url', type=str, help='Single Wikipedia battle list URL to scrape')
    parser.add_argument('--urls', type=str, help='Text file containing URLs (one per line)')
    parser.add_argument('--output', type=str, help='Output CSV file (default: battles_TIMESTAMP.csv)')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests in seconds (default: 1.0)')

    args = parser.parse_args()

    # Validate input
    if not args.url and not args.urls:
        parser.error("Must specify either --url or --urls")

    if args.url and args.urls:
        parser.error("Cannot specify both --url and --urls")

    # Collect URLs
    urls = []
    if args.url:
        urls = [args.url]
    elif args.urls:
        try:
            with open(args.urls, 'r') as f:
                urls = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
        except FileNotFoundError:
            print(f"Error: File '{args.urls}' not found", file=sys.stderr)
            sys.exit(1)

    if not urls:
        print("Error: No URLs to process", file=sys.stderr)
        sys.exit(1)

    print(f"Wikipedia Battle Scraper")
    print(f"========================")
    print(f"URLs to process: {len(urls)}")
    print(f"Output file: {args.output or 'battles_TIMESTAMP.csv'}")
    print(f"Request delay: {args.delay}s\n")

    # Create scraper and run
    scraper = WikipediaBattleScraper(output_file=args.output)
    scraper.scrape_urls(urls, delay=args.delay)

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
