# How to Run the Battle Scrapers on Your Machine

## Why This Is Needed

Wikipedia access is blocked in the Claude Code environment (403 Forbidden), so the scrapers must be run from your local machine. This is actually **better** because:

1. No network restrictions
2. You control the data collection
3. Can run overnight for large datasets
4. Can pause/resume as needed

## Quick Start (5 Minutes)

### Step 1: Set Up Python Environment

```bash
# Clone/navigate to project directory
cd /path/to/claude-test

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Run Test Scrape (API Method - Recommended)

```bash
# Test with single page
python wikipedia_api_scraper.py --page "List_of_battles_1401–1500" --output test.csv

# Test with multiple pages
python wikipedia_api_scraper.py --pages test_page_titles.txt --output battles_test.csv
```

### Step 3: Verify Results

```bash
# Count battles
wc -l battles_test.csv

# View sample
head -20 battles_test.csv

# Check year distribution
cut -d',' -f2 battles_test.csv | sort | uniq -c
```

## Full Data Collection Workflow

### Option A: Wikipedia API Scraper (Recommended)

**Pros:**
- Official API, less likely to be blocked
- More reliable
- Structured data
- Respects Wikipedia's terms

**Cons:**
- Still makes HTTP requests (but to api.php endpoint)

**Usage:**

```bash
# Create a file with all the page titles you want
cat > all_medieval_battles.txt <<EOF
List_of_battles_before_301
List_of_battles_301–1300
List_of_battles_1301–1400
List_of_battles_1401–1500
List_of_battles_1501–1600
List_of_battles_1601–1700
List_of_battles_1701–1800
EOF

# Run the scraper
python wikipedia_api_scraper.py --pages all_medieval_battles.txt --output medieval_battles.csv --delay 2.0
```

### Option B: HTML Scraper + Manual Download

**If API fails or for maximum reliability:**

```bash
# Step 1: Download pages manually in browser
# - Visit each Wikipedia page
# - Right-click → Save Page As → Save to wikipedia_html/
# - Or use the download script (if your network allows):
./download_wikipedia_pages.sh

# Step 2: Parse the HTML files
python parse_local_html.py --directory wikipedia_html/ --output battles.csv
```

### Option C: HTML Scraper (Direct)

**For quick tests if your IP isn't blocked:**

```bash
python wikipedia_battle_scraper.py --urls example_battle_urls.txt --output battles.csv --delay 2.0
```

## Complete Battle Data Collection (1000-1945)

### Medieval & Early Modern (1000-1700)

```bash
# Create comprehensive URL list
cat > comprehensive_battles.txt <<EOF
List_of_battles_301–1300
List_of_battles_1301–1400
List_of_battles_1401–1500
List_of_battles_1501–1600
List_of_battles_1601–1700
EOF

# Scrape (will take 5-10 minutes with 2s delay)
python wikipedia_api_scraper.py --pages comprehensive_battles.txt --output battles_1000_1700.csv --delay 2.0

# Expected: 500-1000 battles
```

### Modern Era (1700-1945)

```bash
cat > modern_battles.txt <<EOF
List_of_battles_1701–1800
List_of_battles_1801–1900
List_of_battles_1901–2000
EOF

python wikipedia_api_scraper.py --pages modern_battles.txt --output battles_1700_1945.csv --delay 2.0

# Expected: 1000-2000 battles
```

### Regional Lists (More Detailed Coverage)

```bash
cat > regional_battles.txt <<EOF
List_of_battles_involving_France
List_of_battles_involving_England
List_of_battles_involving_Scotland
Battles_involving_the_United_Kingdom
List_of_sieges
EOF

python wikipedia_api_scraper.py --pages regional_battles.txt --output battles_regional.csv --delay 2.0

# Expected: 500-1500 additional battles
```

## Expected Results

After running all scrapers, you should have:

```
battles_1000_1700.csv      ~500-1000 battles
battles_1700_1945.csv      ~1000-2000 battles
battles_regional.csv       ~500-1500 battles
```

**Total: 2,000-4,500 battles** from Wikipedia alone!

## Data Quality & Next Steps

### 1. Merge All CSV Files

```python
import pandas as pd

# Load all CSVs
df1 = pd.read_csv('battles_1000_1700.csv')
df2 = pd.read_csv('battles_1700_1945.csv')
df3 = pd.read_csv('battles_regional.csv')

# Merge
all_battles = pd.concat([df1, df2, df3], ignore_index=True)

# Remove duplicates
all_battles_unique = all_battles.drop_duplicates(subset=['name', 'year'], keep='first')

# Save
all_battles_unique.to_csv('all_battles_merged.csv', index=False)

print(f"Total battles: {len(all_battles)}")
print(f"Unique battles: {len(all_battles_unique)}")
print(f"Duplicates removed: {len(all_battles) - len(all_battles_unique)}")
```

### 2. Add Geocoding (Next Phase)

```python
# Install geocoding library
pip install geopy

# Run geocoding script (we'll build this next)
python geocode_battles.py --input all_battles_merged.csv --output battles_with_coords.csv
```

### 3. Filter for Treasure Hunting Focus

```python
import pandas as pd

df = pd.read_csv('battles_with_coords.csv')

# Focus on France, UK, Belgium
france_uk_belgium = df[
    df['location'].str.contains('France|England|Scotland|Wales|Belgium|Flanders', case=False, na=False)
]

# Focus on 1000-1945
treasure_era = france_uk_belgium[
    (france_uk_belgium['year'].astype(str).str.match(r'^\d{4}$')) &
    (france_uk_belgium['year'].astype(int) >= 1000) &
    (france_uk_belgium['year'].astype(int) <= 1945)
]

treasure_era.to_csv('treasure_hunting_battles.csv', index=False)

print(f"Treasure hunting focus battles: {len(treasure_era)}")
```

## Troubleshooting

### Issue: Still getting 403 errors

**Solutions:**

1. **Use VPN**: Some IPs are blocked by Wikipedia
2. **Increase delay**: `--delay 5.0` or higher
3. **Manual download**: Download pages in browser, use `parse_local_html.py`
4. **Contact Wikipedia**: Request API access for research project
5. **Use Wikipedia dumps**: Download complete database dumps (advanced)

### Issue: No battles extracted from some pages

**Cause:** Table structure differs from expected format

**Fix:**

1. View the page manually
2. Check table headers
3. Update `column_mapping` in the scraper if needed
4. Some pages may use different table formats

### Issue: Missing data in fields

**Expected:** Not all Wikipedia tables include all fields

**Solutions:**

- Participants often missing → Cross-reference with other sources
- Outcome often missing → Mark as "unknown" or research manually
- Location varies in detail → Geocoding will standardize this

## Performance Tips

### Parallel Processing for Speed

If you have many pages to scrape, split into batches and run in parallel:

```bash
# Terminal 1
python wikipedia_api_scraper.py --pages batch1.txt --output batch1.csv &

# Terminal 2
python wikipedia_api_scraper.py --pages batch2.txt --output batch2.csv &

# Terminal 3
python wikipedia_api_scraper.py --pages batch3.txt --output batch3.csv &

# Wait for all to complete
wait

# Merge results
cat batch1.csv batch2.csv batch3.csv > all_battles.csv
```

### Caching for Re-runs

Save API responses to avoid re-fetching:

```python
# Modify wikipedia_api_scraper.py to cache responses
import json
import os

cache_dir = 'api_cache'
os.makedirs(cache_dir, exist_ok=True)

# In fetch_page_html():
cache_file = f"{cache_dir}/{page_title.replace('/', '_')}.json"
if os.path.exists(cache_file):
    with open(cache_file) as f:
        return json.load(f)['html']

# After successful fetch:
with open(cache_file, 'w') as f:
    json.dump({'html': html_content}, f)
```

## Time Estimates

| Task | URLs | Expected Battles | Time (2s delay) |
|------|------|------------------|-----------------|
| Test (3 pages) | 3 | 50-150 | 1 minute |
| Medieval (5 pages) | 5 | 500-1000 | 2 minutes |
| All centuries (9 pages) | 9 | 2000-3000 | 3 minutes |
| Regional lists (10 pages) | 10 | 1000-2000 | 4 minutes |
| **TOTAL** | **~25 pages** | **3000-5000** | **~10 minutes** |

## Sample Output Format

The CSV will look like this:

```csv
name,year,date,location,participants,outcome
Battle of Agincourt,1415,25 October 1415,"Agincourt, France",Kingdom of England vs Kingdom of France,English victory
Battle of the Somme,1916,1 July – 18 November 1916,"Somme River, France",British and French vs German Empire,Indecisive
Battle of Waterloo,1815,18 June 1815,"Waterloo, Belgium",Coalition vs French Empire,Coalition victory
```

## What to Do With the Data

1. **Upload to your GIS map**: Import the CSV into your Leaflet.js map
2. **Run geocoding**: Add GPS coordinates (next phase)
3. **Merge with PAS data**: Combine with archaeological finds (phase after)
4. **Calculate probabilities**: Score treasure likelihood (final phase)
5. **Share with me**: Send the CSV back to Claude Code environment for next steps!

## Next Session Plan

**When you run this on your machine and get the CSV data:**

1. Share the CSV file with me (or summary stats)
2. I'll build the geocoding pipeline
3. I'll build the PAS scraper
4. We'll merge everything into your GIS application

## Quick Test Command (Copy-Paste Ready)

```bash
# 30-second test to verify everything works
cd /path/to/claude-test
pip install -r requirements.txt
python wikipedia_api_scraper.py --page "List_of_battles_1401–1500" --output quick_test.csv
head -20 quick_test.csv
wc -l quick_test.csv
```

If this works, you're ready to collect all the data!

## Support

If you encounter issues:

1. Check your Python version: `python --version` (need 3.7+)
2. Check dependencies: `pip list | grep -E "requests|beautifulsoup4"`
3. Try the manual download method
4. Share error messages for troubleshooting

**Ready to collect thousands of battles for Chasseur de Trésors!**
