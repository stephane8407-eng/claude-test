# SPV Treasure Map - Scripts

Collection of utility scripts for geocoding and importing battle data.

## 📂 Scripts

### 1. `geocode_battles.py`
Geocode battles using Nominatim API (OpenStreetMap).

**Usage:**
```bash
python geocode_battles.py <input_csv> <output_csv>

# Example
python geocode_battles.py ../../comprehensive_battles.csv ../../all_battles_geocoded.csv
```

**Features:**
- Uses Nominatim API (free, no API key required)
- Rate limiting: 1.5 seconds per request
- Infers war period from year
- Handles rate limiting (429 errors)
- Progress reporting every 100 battles
- Statistics by country and war period

**Output fields:**
- All original fields from input CSV
- `latitude` - Decimal degrees
- `longitude` - Decimal degrees
- `country` - ISO country code (FR, UK, BE, etc.)
- `war_period` - Inferred from year (WW1, WW2, Napoleonic, etc.)
- `significance` - Default: "moderate"
- `sides_involved` - Parsed from participants

---

### 2. `geocode_battles_photon.py`
Geocode battles using Photon API (Komoot - OpenStreetMap data).

**Usage:**
```bash
python geocode_battles_photon.py <input_csv> <output_csv>

# Example
python geocode_battles_photon.py ../../comprehensive_battles.csv ../../all_battles_geocoded.csv
```

**Features:**
- Uses Photon API (free, more permissive than Nominatim)
- Rate limiting: 0.5 seconds per request
- Same output format as Nominatim script
- Better for bulk geocoding

**Advantages over Nominatim:**
- Faster (0.5s vs 1.5s per request)
- More permissive usage policy
- Same OSM data source

---

### 3. `import_battles.py`
Import geocoded battles into PostgreSQL database.

**Usage:**
```bash
python import_battles.py <geocoded_csv>

# Example
python import_battles.py ../../all_battles_geocoded.csv
```

**Prerequisites:**
- PostgreSQL database 'spv_treasure_map' must exist
- PostGIS extension enabled
- Database credentials in `backend/.env`

**Features:**
- Imports only battles with valid coordinates
- Skips battles without lat/lng
- Parses dates (multiple formats supported)
- Parses participants into sides_involved array
- Batch commits (every 100 battles)
- Statistics and verification
- Prompts before deleting existing data

**Date formats supported:**
- `14 October 1066`
- `October 14 1066`
- `1066-10-14`
- `14/10/1066`
- Date ranges (uses first date)

---

## 🚨 Network Restrictions

**Issue:** The scripts may fail with `403 Forbidden` errors in restricted environments.

**Solutions:**

### Option 1: Run from Local Machine ✅ RECOMMENDED

Download the scripts and CSV to your local machine and run there:

```bash
# On your local machine
cd ~/Documents/treasure-hunting/claude-test
python3 backend/scripts/geocode_battles_photon.py comprehensive_battles.csv all_battles_geocoded.csv
```

### Option 2: Use Google Geocoding API

If OSM-based services don't work, use Google's Geocoding API:

1. Get API key from Google Cloud Console
2. Enable Geocoding API
3. Use Python library `googlemaps`:

```python
import googlemaps
gmaps = googlemaps.Client(key='YOUR_API_KEY')
geocode_result = gmaps.geocode('Hastings, England')
```

**Cost:** $5 per 1,000 requests (first $200/month free)

### Option 3: Manual Geocoding

For the 115 battles in `comprehensive_battles.csv`, I can create a pre-geocoded version using existing battle location data.

---

## 📊 Expected Results

### For comprehensive_battles.csv (115 battles)

**Estimated time:** ~2 minutes (115 × 0.5s = 57.5 seconds)

**Expected success rate:** 75-85% (85-100 battles geocoded)

**Common failures:**
- Historical place names that no longer exist
- Ambiguous locations ("Near Poitiers")
- Very specific locations ("Senlac Hill")

### For 3,439 battles (when available)

**Estimated time:** ~30 minutes with Photon (3,439 × 0.5s = 1,719s)

**Expected success rate:** 70-80% (2,400-2,750 battles geocoded)

---

## 🔧 Troubleshooting

### Error: 403 Forbidden

**Cause:** Network restrictions or IP blocking

**Solutions:**
1. Run from local machine (not in container/cloud environment)
2. Wait 24 hours and try again (temporary block)
3. Use Google Geocoding API instead
4. Contact me for pre-geocoded data

### Error: Database connection failed

**Cause:** PostgreSQL not running or wrong credentials

**Solutions:**
1. Start PostgreSQL: `sudo systemctl start postgresql`
2. Check `.env` file for correct DATABASE_URL
3. Verify database exists: `psql -l | grep spv_treasure_map`

### Error: No battles imported

**Cause:** CSV has no valid coordinates

**Solutions:**
1. Check geocoding output CSV has lat/lng columns
2. Verify geocoding step succeeded
3. Check for blank values in lat/lng columns

---

## 📝 CSV Format

### Input CSV Format

Required columns:
```
name, year, date, location, participants, outcome
```

Example:
```csv
name,year,date,location,participants,outcome
Battle of Hastings,1066,14 October 1066,"Senlac Hill, near Hastings, England",Norman forces vs Anglo-Saxon forces,Norman victory
```

### Output CSV Format

Geocoded CSV adds:
```
latitude, longitude, country, war_period, significance, sides_involved
```

Example:
```csv
name,year,date,location,participants,outcome,latitude,longitude,country,war_period,significance,sides_involved
Battle of Hastings,1066,14 October 1066,"Senlac Hill, near Hastings, England",Norman forces vs Anglo-Saxon forces,Norman victory,50.9118,0.4889,GB,Medieval,moderate,"Norman forces,Anglo-Saxon forces"
```

---

## 🚀 Quick Start

### Full Workflow

```bash
# 1. Geocode battles
cd backend/scripts
python3 geocode_battles_photon.py ../../comprehensive_battles.csv ../../all_battles_geocoded.csv

# 2. Import to database
python3 import_battles.py ../../all_battles_geocoded.csv

# 3. Verify in database
psql -U spv_admin -d spv_treasure_map -c "SELECT COUNT(*) FROM battles;"
```

### Test with Sample (10 battles)

```bash
# Create test sample
head -11 ../../comprehensive_battles.csv > ../../test_sample.csv

# Geocode test sample
python3 geocode_battles_photon.py ../../test_sample.csv ../../test_geocoded.csv

# Import test data
python3 import_battles.py ../../test_geocoded.csv
```

---

## 📞 Support

If geocoding fails due to network restrictions:

1. **Download and run locally** - Most reliable solution
2. **Request pre-geocoded data** - I can provide manually geocoded CSV
3. **Use alternative API** - Google Geocoding API (requires paid API key)

---

**Created:** 2025-11-22
**Last Updated:** 2025-11-22
