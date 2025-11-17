# Battle Scraper - Complete Usage Guide

## Quick Start

### Method 1: Direct Scraping (May be blocked by Wikipedia)

```bash
# Install dependencies
pip install -r requirements.txt

# Scrape a single page
python wikipedia_battle_scraper.py --url "https://en.wikipedia.org/wiki/List_of_battles_1401–1500"

# Scrape multiple pages from file
python wikipedia_battle_scraper.py --urls example_battle_urls.txt --output battles.csv
```

### Method 2: Download Then Parse (Recommended if scraping is blocked)

```bash
# Step 1: Download Wikipedia pages
./download_wikipedia_pages.sh

# Step 2: Parse the downloaded HTML files
python parse_local_html.py --directory wikipedia_html/ --output battles.csv
```

## Detailed Workflows

### Workflow A: Scraping All Medieval/Early Modern Battles (1000-1700)

1. **Create a URL list** (`medieval_battles.txt`):
```
https://en.wikipedia.org/wiki/List_of_battles_301–1300
https://en.wikipedia.org/wiki/List_of_battles_1301–1400
https://en.wikipedia.org/wiki/List_of_battles_1401–1500
https://en.wikipedia.org/wiki/List_of_battles_1501–1600
https://en.wikipedia.org/wiki/List_of_battles_1601–1700
```

2. **Run the scraper**:
```bash
python wikipedia_battle_scraper.py --urls medieval_battles.txt --output medieval_battles.csv --delay 2.0
```

### Workflow B: Scraping Regional Battle Lists

For more comprehensive coverage, use regional lists:

1. **France battles** (`france_battles.txt`):
```
https://en.wikipedia.org/wiki/List_of_battles_involving_France
```

2. **UK battles** (`uk_battles.txt`):
```
https://en.wikipedia.org/wiki/List_of_battles_involving_England
https://en.wikipedia.org/wiki/List_of_battles_involving_Scotland
https://en.wikipedia.org/wiki/Battles_involving_the_United_Kingdom
```

3. **Run separately**:
```bash
python wikipedia_battle_scraper.py --urls france_battles.txt --output france_battles.csv
python wikipedia_battle_scraper.py --urls uk_battles.txt --output uk_battles.csv
```

### Workflow C: Download + Parse (When Scraping Fails)

**Step 1**: Download pages manually or with the script:

```bash
./download_wikipedia_pages.sh
```

Or download manually in your browser:
1. Visit Wikipedia battle list page
2. Right-click → "Save As" → Save as HTML
3. Save to `wikipedia_html/` directory

**Step 2**: Parse all downloaded files:

```bash
python parse_local_html.py --directory wikipedia_html/ --output all_battles.csv
```

**Step 3**: Verify the output:

```bash
# Count battles
wc -l all_battles.csv

# View first few
head -20 all_battles.csv

# Check specific year range
grep "^.*,14[0-9][0-9]," all_battles.csv
```

## Troubleshooting

### Problem: 403 Forbidden Error

**Cause**: Wikipedia is blocking automated requests from your IP/environment.

**Solutions**:

1. **Use the download script** (downloads with browser-like headers):
   ```bash
   ./download_wikipedia_pages.sh
   python parse_local_html.py --directory wikipedia_html/ --output battles.csv
   ```

2. **Manual download**:
   - Open Wikipedia page in browser
   - Save as HTML (Ctrl+S / Cmd+S)
   - Parse with `parse_local_html.py`

3. **Increase delay**:
   ```bash
   python wikipedia_battle_scraper.py --urls urls.txt --delay 5.0
   ```

4. **Use a different network**:
   - Try from home network instead of VPN
   - Some cloud environments are blocked by Wikipedia

### Problem: No battles extracted

**Cause**: Table structure doesn't match expected format.

**Solutions**:

1. **Check the Wikipedia page** - verify it has tables with class="wikitable"

2. **Examine table headers** - the script looks for these keywords:
   - Name: "name", "battle", "conflict"
   - Date: "date", "year", "time"
   - Location: "location", "place", "site"
   - Participants: "belligerents", "combatants", "participants"
   - Outcome: "result", "outcome", "victor", "winner"

3. **Modify the scraper** - add new header mappings if needed

### Problem: Missing data in some fields

**Cause**: Wikipedia tables have inconsistent structures.

**Expected**: Not all Wikipedia battle lists include all fields. Some may only have name, date, and location.

**Solution**: Post-process the CSV to add missing data:
- Use geocoding APIs for missing coordinates
- Cross-reference with other sources for participants/outcome

## Data Quality Tips

### 1. Deduplicate Battles

Battles may appear in multiple lists (e.g., century lists AND regional lists).

```python
import pandas as pd

# Load CSV
df = pd.read_csv('battles.csv')

# Remove duplicates based on name and year
df_unique = df.drop_duplicates(subset=['name', 'year'], keep='first')

# Save deduplicated data
df_unique.to_csv('battles_unique.csv', index=False)
```

### 2. Validate Years

Check for extraction errors:

```bash
# Find battles with non-numeric years
grep -v "^[^,]*,[0-9]*," battles.csv

# Find battles with years outside expected range (1000-1945)
awk -F',' '$2 < 1000 || $2 > 1945 {print}' battles.csv
```

### 3. Standardize Location Names

Location names vary (e.g., "Agincourt", "Azincourt", "France", "Northern France").

**Solution**: Create a location normalization script or use geocoding APIs.

## Next Steps for Chasseur de Trésors

### 1. Geocode Locations

Add GPS coordinates to each battle:

```python
# Install geopy
pip install geopy

# Example geocoding script
from geopy.geocoders import Nominatim
import pandas as pd
import time

geolocator = Nominatim(user_agent="treasure_hunter")

df = pd.read_csv('battles.csv')
df['latitude'] = None
df['longitude'] = None

for idx, row in df.iterrows():
    if pd.notna(row['location']):
        try:
            location = geolocator.geocode(row['location'])
            if location:
                df.at[idx, 'latitude'] = location.latitude
                df.at[idx, 'longitude'] = location.longitude
            time.sleep(1)  # Respectful rate limiting
        except:
            pass

df.to_csv('battles_geocoded.csv', index=False)
```

### 2. Merge with Archaeological Data

Combine with PAS (Portable Antiquities Scheme) data:

```python
import pandas as pd

battles = pd.read_csv('battles_geocoded.csv')
pas_finds = pd.read_csv('pas_finds.csv')  # From UK PAS database

# Spatial join to find archaeological finds near battle sites
# (Requires GeoPandas for proper spatial operations)
```

### 3. Calculate Treasure Probability

Create scoring algorithm:

```python
# Factors that increase treasure probability:
# - Multiple battles in same location
# - Siege locations (longer = more buried valuables)
# - Retreat routes (armies bury loot)
# - High archaeological find density
# - Distance from modern development

# Example scoring:
def calculate_treasure_score(battle_row):
    score = 0

    # Base score for any battle
    score += 10

    # Bonus for sieges
    if 'siege' in str(battle_row['name']).lower():
        score += 25

    # Bonus for retreats
    if 'retreat' in str(battle_row['outcome']).lower():
        score += 20

    # Bonus for medieval period (1000-1500)
    if 1000 <= int(battle_row['year']) <= 1500:
        score += 15

    return score
```

### 4. Create Heatmap Data

Generate density maps for visualization:

```python
from scipy.stats import gaussian_kde
import numpy as np

# Create 2D kernel density estimation
battles_coords = battles[['latitude', 'longitude']].dropna()
kde = gaussian_kde(battles_coords.T)

# Generate heatmap grid
# Export as GeoJSON for Leaflet.js heatmap overlay
```

## File Structure

After running all scripts, you should have:

```
claude-test/
├── wikipedia_battle_scraper.py      # Main scraper
├── parse_local_html.py              # HTML parser
├── download_wikipedia_pages.sh      # Download helper
├── requirements.txt                 # Dependencies
├── README_SCRAPER.md               # Documentation
├── USAGE_GUIDE.md                  # This file
├── example_battle_urls.txt         # Sample URLs
├── wikipedia_html/                 # Downloaded HTML files
│   ├── List_of_battles_1401-1500.html
│   ├── List_of_battles_1501-1600.html
│   └── ...
└── battles.csv                     # Output data
```

## Command Reference

### wikipedia_battle_scraper.py

```bash
# Options:
--url URL              Single URL to scrape
--urls FILE            File with URLs (one per line)
--output FILE          Output CSV file (default: battles_TIMESTAMP.csv)
--delay SECONDS        Delay between requests (default: 1.0)

# Examples:
python wikipedia_battle_scraper.py --url "https://en.wikipedia.org/wiki/List_of_battles_1401–1500"
python wikipedia_battle_scraper.py --urls urls.txt --output my_battles.csv --delay 2.0
```

### parse_local_html.py

```bash
# Options:
--file FILE            Parse single HTML file
--files FILE1 FILE2    Parse multiple HTML files
--directory DIR        Parse all HTML files in directory
--output FILE          Output CSV file (default: battles_TIMESTAMP.csv)

# Examples:
python parse_local_html.py --file page.html
python parse_local_html.py --directory wikipedia_html/ --output battles.csv
python parse_local_html.py --files page1.html page2.html --output battles.csv
```

## Tips for Large-Scale Scraping

1. **Use the Wikipedia API** for large datasets (more reliable than scraping)
2. **Download database dumps** - Wikipedia offers complete database dumps
3. **Be respectful** - Use delays, proper user agents, check robots.txt
4. **Cache results** - Save HTML files for re-parsing if structure changes
5. **Validate data** - Spot-check output for accuracy
6. **Contribute back** - If you find errors, update Wikipedia!

## Support

For issues or questions:
1. Check Wikipedia page structure hasn't changed
2. Verify network connectivity
3. Try the download + parse workflow
4. Check the CSV output for data quality issues

## License & Attribution

- **Code**: Use freely for your Chasseur de Trésors project
- **Data**: Wikipedia content is licensed under CC BY-SA 3.0
- **Attribution**: Include "Data from Wikipedia" in your application
