#!/usr/bin/env python3
"""
Batch Village Processor
Process thousands of French/Belgian villages automatically.

Takes a CSV file with village data and processes each village through the
complete auto-population pipeline:
1. Wikipedia scraping
2. Mérimée monument database
3. Tourism site scraping
4. Claude AI structuring

Features:
- Progress tracking with resume capability
- Error handling and retry logic
- Rate limiting to be respectful
- CSV and JSON output
- Statistics and reporting

Input CSV Format:
    village_name,latitude,longitude,department
    Azincourt,50.4667,2.1333,Pas-de-Calais
    Reims,49.2583,4.0317,Marne

Usage:
    python batch_process_villages.py --input villages.csv --output-dir village_data/
    python batch_process_villages.py --input villages.csv --resume --delay 3.0
"""

import os
import sys
import csv
import json
import argparse
import time
from typing import List, Dict
from datetime import datetime
from pathlib import Path


# Import village scraper
try:
    from village_auto_scraper import VillageAutoScraper
except ImportError:
    print("Error: village_auto_scraper.py not found", file=sys.stderr)
    sys.exit(1)


class BatchVillageProcessor:
    """
    Process multiple villages in batch with progress tracking.
    """

    def __init__(self, output_dir: str = "village_data", anthropic_api_key: str = None,
                 delay: float = 2.0):
        """
        Initialize batch processor.

        Args:
            output_dir: Directory to save village JSON files
            anthropic_api_key: API key for Claude
            delay: Delay between requests in seconds
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.scraper = VillageAutoScraper(anthropic_api_key=anthropic_api_key)
        self.delay = delay

        self.progress_file = self.output_dir / "progress.json"
        self.stats_file = self.output_dir / "batch_stats.json"
        self.summary_csv = self.output_dir / "villages_summary.csv"

        self.stats = {
            'total_villages': 0,
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'errors': []
        }

    def load_villages_from_csv(self, csv_file: str) -> List[Dict]:
        """
        Load villages from CSV file.

        Expected columns: village_name,latitude,longitude,department
        """
        villages = []

        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                village = {
                    'name': row.get('village_name', row.get('name', '')).strip(),
                    'lat': float(row['latitude']) if row.get('latitude') else None,
                    'lng': float(row['longitude']) if row.get('longitude') else None,
                    'department': row.get('department', '').strip()
                }

                if village['name']:
                    villages.append(village)

        return villages

    def load_progress(self) -> Dict:
        """Load processing progress from file."""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return {'processed_villages': []}

    def save_progress(self, progress: Dict):
        """Save processing progress."""
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f, indent=2)

    def is_already_processed(self, village_name: str, progress: Dict) -> bool:
        """Check if village was already processed."""
        return village_name in progress.get('processed_villages', [])

    def process_batch(self, villages: List[Dict], resume: bool = False):
        """
        Process a batch of villages.

        Args:
            villages: List of village dictionaries
            resume: If True, skip already processed villages
        """
        self.stats['total_villages'] = len(villages)

        # Load progress if resuming
        progress = self.load_progress() if resume else {'processed_villages': []}

        print(f"\n{'='*70}")
        print(f"BATCH VILLAGE PROCESSING")
        print(f"{'='*70}")
        print(f"Total villages: {len(villages)}")
        print(f"Output directory: {self.output_dir}")
        print(f"Delay between requests: {self.delay}s")
        if resume:
            print(f"Resuming: {len(progress['processed_villages'])} already processed")
        print(f"{'='*70}\n")

        # Process each village
        for i, village in enumerate(villages, 1):
            village_name = village['name']

            print(f"\n[{i}/{len(villages)}] Processing: {village_name}")

            # Skip if already processed (resume mode)
            if resume and self.is_already_processed(village_name, progress):
                print(f"  ⊙ Skipping (already processed)")
                self.stats['skipped'] += 1
                continue

            try:
                # Process village
                village_data = self.scraper.scrape_village(
                    village_name=village_name,
                    lat=village['lat'],
                    lng=village['lng'],
                    department=village['department']
                )

                # Save to file
                filename = self._sanitize_filename(village_name) + ".json"
                output_path = self.output_dir / filename

                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(village_data, f, indent=2, ensure_ascii=False)

                print(f"  ✓ Saved to: {filename}")
                print(f"  Completeness: {village_data.get('completeness_score', 0)}/100")

                # Update progress
                progress['processed_villages'].append(village_name)
                self.save_progress(progress)

                self.stats['processed'] += 1
                self.stats['successful'] += 1

            except Exception as e:
                print(f"  ✗ Error processing {village_name}: {e}", file=sys.stderr)
                self.stats['processed'] += 1
                self.stats['failed'] += 1
                self.stats['errors'].append({
                    'village': village_name,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })

            # Rate limiting delay (except for last village)
            if i < len(villages):
                time.sleep(self.delay)

        # Finalize
        self.stats['end_time'] = datetime.now().isoformat()
        self._save_stats()
        self._generate_summary()

    def _sanitize_filename(self, village_name: str) -> str:
        """Sanitize village name for use as filename."""
        return village_name.replace(' ', '_').replace('/', '_').replace('\\', '_')

    def _save_stats(self):
        """Save batch processing statistics."""
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)

        print(f"\n{'='*70}")
        print(f"BATCH PROCESSING COMPLETE")
        print(f"{'='*70}")
        print(f"Total villages: {self.stats['total_villages']}")
        print(f"Processed: {self.stats['processed']}")
        print(f"Successful: {self.stats['successful']}")
        print(f"Failed: {self.stats['failed']}")
        print(f"Skipped: {self.stats['skipped']}")
        print(f"\nStatistics saved to: {self.stats_file}")

    def _generate_summary(self):
        """Generate CSV summary of all processed villages."""
        print(f"\nGenerating summary CSV...")

        # Load all processed village JSON files
        villages_data = []

        for json_file in self.output_dir.glob("*.json"):
            if json_file.name in ['progress.json', 'batch_stats.json']:
                continue

            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    villages_data.append(data)
            except Exception:
                continue

        if not villages_data:
            print(f"  No village data to summarize")
            return

        # Write CSV summary
        with open(self.summary_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'village_name', 'latitude', 'longitude', 'completeness_score',
                'wikipedia_chars', 'merimee_monuments', 'tourism_chars',
                'legends_count', 'historical_events_count', 'notable_sites_count',
                'treasure_score', 'treasure_category'
            ])

            # Data rows
            for data in villages_data:
                coords = data.get('coordinates', {})
                sources = data.get('sources', {})
                processed = data.get('processed_data', {})
                treasure = processed.get('treasure_probability', {}) if processed else {}

                writer.writerow([
                    data.get('village_name', ''),
                    coords.get('lat', ''),
                    coords.get('lng', ''),
                    data.get('completeness_score', 0),
                    sources.get('wikipedia', {}).get('length', 0),
                    sources.get('merimee', {}).get('count', 0),
                    sources.get('tourism', {}).get('length', 0),
                    len(processed.get('legends', [])) if processed else 0,
                    len(processed.get('historical_events', [])) if processed else 0,
                    len(processed.get('notable_sites', [])) if processed else 0,
                    treasure.get('score', 0),
                    treasure.get('category', '')
                ])

        print(f"  ✓ Summary CSV saved to: {self.summary_csv}")
        print(f"  Total villages in summary: {len(villages_data)}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Batch process villages from CSV file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process villages from CSV
  python batch_process_villages.py --input villages.csv

  # With custom output directory
  python batch_process_villages.py --input villages.csv --output-dir data/villages/

  # Resume interrupted processing
  python batch_process_villages.py --input villages.csv --resume

  # Slower rate (more respectful)
  python batch_process_villages.py --input villages.csv --delay 5.0

CSV Format:
  village_name,latitude,longitude,department
  Azincourt,50.4667,2.1333,Pas-de-Calais
  Reims,49.2583,4.0317,Marne

Environment:
  ANTHROPIC_API_KEY should be set for Claude AI processing
        """
    )

    parser.add_argument('--input', type=str, required=True, help='Input CSV file with villages')
    parser.add_argument('--output-dir', type=str, default='village_data', help='Output directory (default: village_data)')
    parser.add_argument('--delay', type=float, default=2.0, help='Delay between requests in seconds (default: 2.0)')
    parser.add_argument('--resume', action='store_true', help='Resume from previous run (skip processed villages)')
    parser.add_argument('--api-key', type=str, help='Anthropic API key')

    args = parser.parse_args()

    # Verify input file exists
    if not Path(args.input).exists():
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)

    # Create processor
    processor = BatchVillageProcessor(
        output_dir=args.output_dir,
        anthropic_api_key=args.api_key,
        delay=args.delay
    )

    # Load villages
    print(f"Loading villages from {args.input}...")
    villages = processor.load_villages_from_csv(args.input)
    print(f"  ✓ Loaded {len(villages)} villages")

    if not villages:
        print("Error: No villages found in CSV", file=sys.stderr)
        sys.exit(1)

    # Process batch
    processor.process_batch(villages, resume=args.resume)

    print(f"\n✓ Batch processing complete!")
    print(f"✓ Village data saved in: {args.output_dir}")
    print(f"✓ Summary CSV: {processor.summary_csv}")


if __name__ == '__main__':
    main()
