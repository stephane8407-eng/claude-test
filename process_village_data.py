#!/usr/bin/env python3
"""
Village Data Processor with Claude API
Takes raw scraped text about a village and uses Claude AI to extract and structure:
- Legends and folklore
- Historical events with dates
- Notable sites and monuments
- Treasure probability score
- Interesting facts

Requires: anthropic Python package and ANTHROPIC_API_KEY environment variable

Usage:
    python process_village_data.py --text "Raw village text..." --village "Azincourt"
    python process_village_data.py --file village_raw.txt --village "Reims" --output village_data.json
"""

import os
import json
import argparse
import sys
from typing import Dict, Optional
from datetime import datetime


# Check if anthropic is available
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("Warning: anthropic package not installed. Install with: pip install anthropic", file=sys.stderr)


class VillageDataProcessor:
    """
    Process raw village text using Claude AI to extract structured data.
    """

    def __init__(self, api_key: str = None):
        """
        Initialize processor with Claude API.

        Args:
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic package required. Install with: pip install anthropic")

        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable or api_key parameter required")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-5-20250929"  # Latest model

    def process_village(self, village_name: str, raw_text: str, coordinates: Dict = None) -> Dict:
        """
        Process raw village text into structured JSON.

        Args:
            village_name: Name of the village
            raw_text: Raw scraped text (Wikipedia, tourism sites, etc.)
            coordinates: Optional dict with 'lat' and 'lng'

        Returns:
            Structured village data dictionary
        """
        print(f"Processing village data for: {village_name}")
        print(f"  Raw text length: {len(raw_text)} characters")

        if not raw_text or len(raw_text) < 50:
            print("  ⚠ Text too short for processing")
            return self._empty_village_data(village_name, coordinates)

        prompt = self._build_extraction_prompt(village_name, raw_text)

        try:
            print(f"  Calling Claude API...")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Extract JSON from response
            response_text = response.content[0].text

            # Try to parse JSON from response
            village_data = self._parse_claude_response(response_text)

            # Add metadata
            village_data['village_name'] = village_name
            village_data['coordinates'] = coordinates or {}
            village_data['processed_date'] = datetime.now().isoformat()
            village_data['source_text_length'] = len(raw_text)

            print(f"  ✓ Processed successfully")
            print(f"    - Legends: {len(village_data.get('legends', []))}")
            print(f"    - Historical events: {len(village_data.get('historical_events', []))}")
            print(f"    - Notable sites: {len(village_data.get('notable_sites', []))}")
            print(f"    - Treasure score: {village_data.get('treasure_probability', {}).get('score', 0)}/100")

            return village_data

        except Exception as e:
            print(f"  Error processing with Claude API: {e}", file=sys.stderr)
            return self._empty_village_data(village_name, coordinates)

    def _build_extraction_prompt(self, village_name: str, raw_text: str) -> str:
        """Build the prompt for Claude to extract village data."""
        return f"""You are analyzing historical and cultural information about the French/Belgian village of "{village_name}" for a treasure hunting historical GIS application.

INPUT TEXT:
{raw_text[:15000]}

Your task is to extract and structure the following information from the text above. Return ONLY valid JSON with this exact structure:

{{
  "legends": [
    {{
      "title": "Legend title",
      "summary": "Brief 2-3 sentence summary of the legend",
      "treasure_related": true/false,
      "keywords": ["keyword1", "keyword2"]
    }}
  ],
  "historical_events": [
    {{
      "date": "YYYY or YYYY-MM-DD or descriptive date",
      "event": "Event description",
      "significance": "Why this matters for treasure hunting",
      "treasure_potential": "High/Medium/Low"
    }}
  ],
  "notable_sites": [
    {{
      "name": "Site name",
      "type": "castle/church/abbey/fortification/monument/archaeological site",
      "description": "Brief description",
      "period": "Medieval/Renaissance/etc.",
      "treasure_relevance": "Why this site might have treasure"
    }}
  ],
  "interesting_facts": [
    "Fact 1 that would impress village officials",
    "Fact 2 showing deep research",
    "Fact 3 about local history"
  ],
  "treasure_probability": {{
    "score": 0-100,
    "reasoning": "Explanation of treasure probability based on history",
    "key_factors": [
      "Factor 1 (e.g., site of medieval battle)",
      "Factor 2 (e.g., historic monastery nearby)",
      "Factor 3 (e.g., retreat route passed through)"
    ],
    "category": "High/Medium/Low"
  }},
  "summary": "2-3 sentence compelling summary for village pitch"
}}

EXTRACTION RULES:
1. Only extract information explicitly mentioned in the text
2. If no legends found, return empty array
3. If no historical events, return empty array
4. Treasure probability score factors:
   - Battles/conflicts: +30 points
   - Medieval religious sites: +25 points
   - Castles/fortifications: +20 points
   - Documented treasure finds: +15 points
   - Historical trade routes: +10 points
5. Be concise but specific
6. Focus on treasure hunting relevance
7. Return ONLY the JSON, no other text

RETURN JSON NOW:"""

    def _parse_claude_response(self, response_text: str) -> Dict:
        """Parse Claude's JSON response."""
        # Try to extract JSON from response
        # Claude might wrap it in ```json``` or other formatting

        # Remove markdown code blocks if present
        response_text = response_text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]

        response_text = response_text.strip()

        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"  Warning: Could not parse JSON from Claude response: {e}", file=sys.stderr)
            print(f"  Response preview: {response_text[:500]}", file=sys.stderr)
            raise

    def _empty_village_data(self, village_name: str, coordinates: Dict = None) -> Dict:
        """Return empty village data structure."""
        return {
            'village_name': village_name,
            'coordinates': coordinates or {},
            'processed_date': datetime.now().isoformat(),
            'legends': [],
            'historical_events': [],
            'notable_sites': [],
            'interesting_facts': [],
            'treasure_probability': {
                'score': 0,
                'reasoning': 'Insufficient data for analysis',
                'key_factors': [],
                'category': 'Unknown'
            },
            'summary': f'No data available for {village_name}',
            'source_text_length': 0
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Process village data using Claude AI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process from text file
  python process_village_data.py --file village_text.txt --village "Azincourt"

  # Process with direct text
  python process_village_data.py --text "Historical info..." --village "Reims"

  # With coordinates
  python process_village_data.py --file data.txt --village "Paris" --lat 48.8566 --lng 2.3522

  # Specify output file
  python process_village_data.py --file data.txt --village "Lyon" --output lyon_data.json

Environment:
  ANTHROPIC_API_KEY must be set with your Claude API key
        """
    )

    parser.add_argument('--village', type=str, required=True, help='Village name')
    parser.add_argument('--text', type=str, help='Raw text to process')
    parser.add_argument('--file', type=str, help='File containing raw text')
    parser.add_argument('--lat', type=float, help='Village latitude')
    parser.add_argument('--lng', type=float, help='Village longitude')
    parser.add_argument('--output', type=str, help='Output JSON file')
    parser.add_argument('--api-key', type=str, help='Anthropic API key (or use ANTHROPIC_API_KEY env var)')

    args = parser.parse_args()

    # Validate input
    if not args.text and not args.file:
        parser.error("Must specify either --text or --file")

    if args.text and args.file:
        parser.error("Cannot specify both --text and --file")

    # Read input text
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                raw_text = f.read()
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found", file=sys.stderr)
            sys.exit(1)
    else:
        raw_text = args.text

    # Prepare coordinates
    coordinates = None
    if args.lat and args.lng:
        coordinates = {'lat': args.lat, 'lng': args.lng}

    # Set output file
    if args.output:
        output_file = args.output
    else:
        village_safe = args.village.replace(' ', '_').replace('/', '_')
        output_file = f"{village_safe}_data.json"

    print(f"Village Data Processor with Claude AI")
    print(f"======================================\n")

    # Create processor
    try:
        processor = VillageDataProcessor(api_key=args.api_key)
    except (ImportError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Process village
    village_data = processor.process_village(
        village_name=args.village,
        raw_text=raw_text,
        coordinates=coordinates
    )

    # Save output
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(village_data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Village data saved to: {output_file}")

    # Display summary
    print(f"\n{'='*60}")
    print(f"VILLAGE PROFILE SUMMARY: {args.village}")
    print(f"{'='*60}")

    if village_data.get('summary'):
        print(f"\n{village_data['summary']}\n")

    print(f"Legends: {len(village_data.get('legends', []))}")
    print(f"Historical Events: {len(village_data.get('historical_events', []))}")
    print(f"Notable Sites: {len(village_data.get('notable_sites', []))}")

    treasure = village_data.get('treasure_probability', {})
    score = treasure.get('score', 0)
    category = treasure.get('category', 'Unknown')

    print(f"\nTreasure Probability: {score}/100 ({category})")

    if treasure.get('key_factors'):
        print(f"\nKey Factors:")
        for factor in treasure['key_factors']:
            print(f"  • {factor}")

    print(f"\n✓ Success! Processed {args.village}")


if __name__ == '__main__':
    main()
