# Wikipedia Battle Scraper

A Python tool to extract battle data from Wikipedia battle list pages and export to CSV format.

## Features

- Scrapes Wikipedia battle list pages automatically
- Extracts: name, year, date, location, participants, outcome
- Exports to CSV format
- Supports multiple URLs from a file
- Intelligent retry logic with exponential backoff
- Respectful rate limiting
- Handles different Wikipedia table formats

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Single URL

```bash
python wikipedia_battle_scraper.py --url "https://en.wikipedia.org/wiki/List_of_battles_1401–1500"
```

### Multiple URLs from file

Create a text file with one URL per line:

```bash
python wikipedia_battle_scraper.py --urls example_battle_urls.txt
```

### Custom output file

```bash
python wikipedia_battle_scraper.py --url "..." --output my_battles.csv
```

### Adjust delay between requests

```bash
python wikipedia_battle_scraper.py --urls urls.txt --delay 2.0
```

## Example URL Lists

### Medieval & Early Modern (1000-1700)
- https://en.wikipedia.org/wiki/List_of_battles_before_301
- https://en.wikipedia.org/wiki/List_of_battles_301–1300
- https://en.wikipedia.org/wiki/List_of_battles_1301–1400
- https://en.wikipedia.org/wiki/List_of_battles_1401–1500
- https://en.wikipedia.org/wiki/List_of_battles_1501–1600
- https://en.wikipedia.org/wiki/List_of_battles_1601–1700

### Modern Era (1700-1945)
- https://en.wikipedia.org/wiki/List_of_battles_1701–1800
- https://en.wikipedia.org/wiki/List_of_battles_1801–1900
- https://en.wikipedia.org/wiki/List_of_battles_1901–2000

### Regional Lists (for more detail)
- https://en.wikipedia.org/wiki/List_of_battles_involving_France
- https://en.wikipedia.org/wiki/List_of_battles_involving_England
- https://en.wikipedia.org/wiki/List_of_battles_involving_Scotland
- https://en.wikipedia.org/wiki/Battles_involving_the_United_Kingdom

## Output Format

CSV file with the following columns:

- `name`: Battle name
- `year`: Extracted year (for easy sorting/filtering)
- `date`: Full date string (may include month, day, or range)
- `location`: Geographic location
- `participants`: Combatants (formatted as "Side A vs Side B")
- `outcome`: Battle result/victor

## Troubleshooting

### 403 Forbidden Errors

If you encounter 403 errors from Wikipedia, it may be due to:

1. **Network restrictions**: Your IP or environment may be blocked
2. **Rate limiting**: Add longer delays with `--delay 3.0`
3. **Wikipedia API alternative**: Consider using the Wikipedia API instead

**Workaround**: Download the HTML pages manually and modify the scraper to read from local files, or run from a different network/environment.

### No tables found

- The page might not have the expected table structure
- Check the Wikipedia page manually to verify it has battle tables with class="wikitable"

## Code Structure

```python
WikipediaBattleScraper
├── fetch_page()              # Downloads Wikipedia page with retry logic
├── extract_year()            # Extracts year from date strings
├── clean_text()              # Removes references and cleans text
├── extract_battles_from_table()  # Parses HTML tables
├── scrape_url()              # Scrapes single URL
├── scrape_urls()             # Scrapes multiple URLs with delays
└── export_to_csv()           # Exports to CSV
```

## Extending the Scraper

### Add new fields

Modify the `column_mapping` dictionary in `extract_battles_from_table()`:

```python
column_mapping = {
    'name': ['name', 'battle', 'conflict'],
    'date': ['date', 'year', 'time'],
    # Add your new field here
    'casualties': ['casualties', 'losses'],
}
```

### Handle different table structures

The scraper automatically maps column headers to fields. If a Wikipedia page uses different header names, add them to the `column_mapping`.

## Best Practices

1. **Be respectful**: Use appropriate delays (1-2 seconds minimum)
2. **Check robots.txt**: Ensure you're allowed to scrape
3. **Verify data**: Always spot-check the output CSV for accuracy
4. **Attribution**: Wikipedia content is CC BY-SA licensed
5. **Consider alternatives**: For large-scale scraping, use the Wikipedia API or database dumps

## Next Steps

For the "Chasseur de Trésors" project:

1. Run scraper on all century battle lists (1000-1945)
2. Deduplicate battles that appear in multiple lists
3. Add geocoding for locations without coordinates
4. Merge with archaeological finds data (PAS database)
5. Create treasure probability scoring algorithm

## License

This tool is for educational purposes. Wikipedia content is licensed under CC BY-SA 3.0.

## Contributing

Improvements welcome! Priority areas:
- Better table format detection
- Coordinate extraction from Wikipedia pages
- Support for battle infoboxes (additional detail)
- Integration with Wikidata for structured data
