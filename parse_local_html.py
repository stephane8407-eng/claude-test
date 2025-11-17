#!/usr/bin/env python3
"""
Parse Wikipedia Battle HTML Files
For use when direct scraping is blocked. Download Wikipedia pages manually, then parse them.

Usage:
    python parse_local_html.py --file downloaded_page.html --output battles.csv
    python parse_local_html.py --directory ./html_files/ --output all_battles.csv
"""

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import List, Dict
from datetime import datetime
from bs4 import BeautifulSoup


def clean_text(text: str) -> str:
    """Clean extracted text by removing references, extra whitespace, etc."""
    if not text:
        return ""

    # Remove reference brackets [1], [2], etc.
    text = re.sub(r'\[\d+\]', '', text)

    # Remove citation needed tags
    text = re.sub(r'\[citation needed\]', '', text, flags=re.IGNORECASE)

    # Normalize whitespace
    text = ' '.join(text.split())

    return text.strip()


def extract_year(date_str: str) -> str:
    """Extract year from date string."""
    if not date_str:
        return ""

    # Look for 4-digit years
    year_match = re.search(r'\b(\d{4})\b', date_str)
    if year_match:
        return year_match.group(1)

    # Look for 3-digit years (e.g., 732)
    year_match = re.search(r'\b(\d{3})\b', date_str)
    if year_match:
        return year_match.group(1)

    return date_str.strip()


def extract_battles_from_table(table) -> List[Dict[str, str]]:
    """Extract battle data from a Wikipedia table."""
    battles = []

    # Find header row to identify columns
    headers = []
    header_row = table.find('tr')
    if header_row:
        for th in header_row.find_all(['th', 'td']):
            header_text = clean_text(th.get_text()).lower()
            headers.append(header_text)

    print(f"  Headers: {headers}")

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

    print(f"  Mapped: {field_indices}")

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
            link = name_cell.find('a')
            if link:
                battle['name'] = clean_text(link.get_text())
            else:
                battle['name'] = clean_text(name_cell.get_text())

        if 'date' in field_indices and field_indices['date'] < len(cells):
            date_text = clean_text(cells[field_indices['date']].get_text())
            battle['date'] = date_text
            battle['year'] = extract_year(date_text)

        if 'location' in field_indices and field_indices['location'] < len(cells):
            battle['location'] = clean_text(cells[field_indices['location']].get_text())

        if 'participants' in field_indices and field_indices['participants'] < len(cells):
            participants_parts = []
            start_idx = field_indices['participants']
            for i in range(start_idx, min(start_idx + 3, len(cells))):
                text = clean_text(cells[i].get_text())
                if text and text.lower() not in ['vs', 'vs.', 'v.', 'versus']:
                    participants_parts.append(text)
            battle['participants'] = ' vs '.join(participants_parts[:2]) if len(participants_parts) > 1 else participants_parts[0] if participants_parts else ''

        if 'outcome' in field_indices and field_indices['outcome'] < len(cells):
            battle['outcome'] = clean_text(cells[field_indices['outcome']].get_text())

        if battle['name']:
            battles.append(battle)

    return battles


def parse_html_file(file_path: Path) -> List[Dict[str, str]]:
    """Parse a single HTML file and extract battles."""
    print(f"\nParsing: {file_path.name}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html = f.read()
    except Exception as e:
        print(f"  Error reading file: {e}", file=sys.stderr)
        return []

    soup = BeautifulSoup(html, 'html.parser')

    # Find all tables with class 'wikitable'
    tables = soup.find_all('table', {'class': 'wikitable'})
    print(f"  Found {len(tables)} tables")

    all_battles = []
    for i, table in enumerate(tables):
        print(f"  Table {i+1}/{len(tables)}:")
        battles = extract_battles_from_table(table)
        all_battles.extend(battles)
        print(f"    Extracted {len(battles)} battles")

    return all_battles


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Parse Wikipedia battle list HTML files.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse a single HTML file
  python parse_local_html.py --file battles_1401_1500.html --output battles.csv

  # Parse all HTML files in a directory
  python parse_local_html.py --directory ./html_files/ --output all_battles.csv

  # Parse multiple specific files
  python parse_local_html.py --files file1.html file2.html --output battles.csv
        """
    )

    parser.add_argument('--file', type=str, help='Single HTML file to parse')
    parser.add_argument('--files', nargs='+', help='Multiple HTML files to parse')
    parser.add_argument('--directory', type=str, help='Directory containing HTML files')
    parser.add_argument('--output', type=str, help='Output CSV file (default: battles_TIMESTAMP.csv)')

    args = parser.parse_args()

    # Validate input
    if not any([args.file, args.files, args.directory]):
        parser.error("Must specify --file, --files, or --directory")

    # Collect file paths
    file_paths = []

    if args.file:
        file_paths.append(Path(args.file))

    if args.files:
        file_paths.extend([Path(f) for f in args.files])

    if args.directory:
        dir_path = Path(args.directory)
        if not dir_path.is_dir():
            print(f"Error: '{args.directory}' is not a directory", file=sys.stderr)
            sys.exit(1)
        file_paths.extend(dir_path.glob('*.html'))
        file_paths.extend(dir_path.glob('*.htm'))

    if not file_paths:
        print("Error: No HTML files found", file=sys.stderr)
        sys.exit(1)

    # Set output file
    if args.output:
        output_file = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"battles_{timestamp}.csv"

    print(f"Wikipedia Battle HTML Parser")
    print(f"============================")
    print(f"Files to process: {len(file_paths)}")
    print(f"Output file: {output_file}\n")

    # Parse all files
    all_battles = []
    for file_path in file_paths:
        if not file_path.exists():
            print(f"Warning: File not found: {file_path}", file=sys.stderr)
            continue

        battles = parse_html_file(file_path)
        all_battles.extend(battles)

    if not all_battles:
        print("\nNo battles extracted!", file=sys.stderr)
        sys.exit(1)

    # Export to CSV
    print(f"\nExporting {len(all_battles)} battles to {output_file}")

    fieldnames = ['name', 'year', 'date', 'location', 'participants', 'outcome']

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_battles)

    print(f"✓ Success! Extracted {len(all_battles)} battles")
    print(f"✓ Data saved to: {output_file}")


if __name__ == '__main__':
    main()
