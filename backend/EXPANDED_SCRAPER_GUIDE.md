# Expanded AI Conflict Scraper: 2,500 Years of History

## Overview

This expanded scraper searches for conflicts across **2,500 years** (500 BC - 2024 AD) within a **100km radius** of Chirac, Charente.

**Expected Results:** 90-170 conflicts
**Cost:** ~$2-3 (Claude API)
**Time:** 4-8 hours processing

---

## Coverage

### Geographic Scope
- **Center:** Chirac (45.9164°N, 0.6542°E)
- **Radius:** 100km
- **Major Sites:**
  - Cassinomagus (Chassenon) - Roman thermal/military complex ⭐
  - Angoulême (ancient Iculisma)
  - Confolens
  - Rochechouart
  - Chabanais

### Historical Periods (14 periods)

1. **Gallic Tribes Era** (500-58 BC)
   - Inter-tribal warfare, fortified oppida
   - Lemovices, Pictons, Santons territories

2. **Gallic Wars** (58-50 BC) ⚔️
   - Caesar's conquest
   - Gallic resistance, Vercingetorix era

3. **Roman Gaul** (50 BC - 410 AD) 🏛️
   - **CASSINOMAGUS** (Chassenon) - major thermal/military complex
   - Roman legions, military roads
   - Barbarian raids

4. **Late Antiquity / Barbarian Invasions** (410-800 AD)
   - Visigoths, Franks, Germanic invasions

5. **Early Medieval** (800-1000)
   - Viking raids (if any)
   - Feudal conflicts

6. **High Medieval** (1000-1337)
   - Castle warfare, seigneurial conflicts
   - Plantagenêt influence

7. **Hundred Years War** (1337-1453)
   - English occupation, battles, sieges

8. **Wars of Religion** (1562-1598)
   - Catholic-Protestant battles, massacres

9. **17th Century** (1600-1700)
   - Fronde, royal army actions

10. **French Revolution** (1789-1799)
    - Executions, battles, requisitions

11. **Napoleonic Era** (1799-1815)
    - Conscription, economic warfare

12. **19th Century** (1815-1914)
    - Franco-Prussian War, insurrections

13. **World War I** (1914-1918)
    - Mobilization, training, casualties

14. **World War II** (1939-1945)
    - Resistance, liberation, battles (expands existing 4 conflicts)

---

## Special Features

### Roman Era Focus
The scraper includes special searches for:
- **Cassinomagus (Chassenon):**
  - Thermal baths with military function
  - Legion presence
  - Strategic position on Roman roads
- **Roman military camps and fortifications**
- **Barbarian raids and invasions**
- **Archaeological evidence**

### Date Handling
- BC dates stored as negative years (e.g., -52 for 52 BC)
- AD dates in standard format (YYYY-MM-DD)
- Precision levels: day, month, year, decade, century, circa

---

## Usage

### Quick Start

```bash
cd backend
./scripts/run_expanded_scraper_chirac.sh
```

### Manual Execution

```bash
cd backend
source venv/bin/activate  # if using virtual environment

python app/scrapers/ai_conflict_scraper_expanded.py \
    --location "Chirac" \
    --department "Charente" \
    --region "Nouvelle-Aquitaine" \
    --lat 45.9164 \
    --lng 0.6542 \
    --radius 100 \
    --output "chirac_2500years_conflicts.json" \
    --delay 2.0
```

### Required Environment Variables

Create `backend/.env`:
```
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_google_cse_id
ANTHROPIC_API_KEY=your_anthropic_api_key
```

---

## Output Format

The scraper produces a JSON file with:

```json
{
  "location_name": "Chirac",
  "time_span": "500 BC - 2024 AD",
  "radius_km": 100,
  "conflict_count": 120,
  "conflicts": [
    {
      "name": "Bataille de Chirac",
      "date": "1944-07-31",
      "date_str": "1944-07-31",
      "date_precision": "day",
      "period": "ww2",
      "conflict_type": "battle",
      "participants": [...],
      "casualties": {...},
      "outcome": "...",
      "strategic_importance": "...",
      "impact_today": {
        "infrastructure": "...",
        "economy": "...",
        "tourism": "...",
        "identity": "...",
        "demographics": "...",
        "governance": "..."
      },
      "confidence_score": 85,
      "sources": [...]
    }
  ],
  "stats": {
    "conflicts_by_period": {
      "gallic_tribes": 5,
      "gallic_wars": 3,
      "roman_gaul": 12,
      "ww2": 8,
      ...
    }
  }
}
```

---

## Search Strategy

### Phase 1: Comprehensive Period-by-Period Search
- Execute 6 queries per historical period
- Special Roman site searches (Cassinomagus, etc.)
- Total: ~120-150 Google searches
- Collect text from top 5 results per query

### Phase 2: AI Conflict Extraction
- Claude Sonnet 4 analyzes all collected text
- Extracts structured ConflictEvent objects
- Handles BC/AD dates correctly
- Includes confidence scoring
- Deduplicates conflicts

---

## Database Import

After scraping, import to PostgreSQL:

```bash
cd backend
python scripts/import_conflicts.py chirac_2500years_conflicts.json
```

This will:
1. Parse the JSON output
2. Insert conflicts into `local_conflicts` table
3. Handle BC dates (stored as negative years or date strings)
4. Validate coordinates and data quality

---

## Sample Search Queries

### Gallic Tribes Era (500-58 BC)
```
- "peuples gaulois Charente"
- "oppida Lemovices Pictons"
- "conflits celtes Aquitaine"
```

### Gallic Wars (58-50 BC)
```
- "guerre des Gaules Charente"
- "César Aquitaine bataille"
- "Lemovices résistance romaine"
```

### Roman Gaul (50 BC - 410 AD)
```
- "Cassinomagus bataille"
- "Cassinomagus fonction militaire"
- "légion romaine Charente"
- "thermes Chassenon militaire"
- "voie romaine Aquitaine conflit"
```

### Hundred Years War (1337-1453)
```
- "bataille Angoulême anglais"
- "siège Confolens 14e siècle"
- "guerre cent ans Charente"
```

### Wars of Religion (1562-1598)
```
- "guerres religion Charente"
- "bataille protestants Angoulême"
- "massacre Confolens"
```

---

## Performance & Costs

### Expected Metrics
- **Total searches:** 120-150
- **URLs fetched:** 600-750
- **Text collected:** 4-6 million characters
- **Claude API calls:** 8-12
- **Processing time:** 4-8 hours
- **Total cost:** $2-3 (mostly Claude API)

### API Usage
- **Google Custom Search:** ~$0 (100 free searches/day)
- **Claude Sonnet 4:** ~$2-3 for text analysis
  - Input: ~1-2M tokens
  - Output: ~50K tokens

---

## Quality & Confidence

### Confidence Score Levels
- **90-100:** Multiple reliable sources, specific details, dates, commanders
- **70-89:** Good sources, most key details present
- **50-69:** Limited sources or missing key details
- **Below 50:** Vague mentions, folklore, unverified

### Expected Distribution
- Ancient conflicts (500 BC - 800 AD): Lower confidence (50-70)
  - Based on archaeological evidence and sparse records
- Medieval conflicts (800-1453): Medium confidence (60-80)
  - Castle records, chroniclers
- Modern conflicts (1789-1945): High confidence (80-95)
  - Detailed records, eyewitnesses, official documents

---

## Troubleshooting

### "Google API not configured"
- Check `.env` file exists in `backend/` directory
- Verify `GOOGLE_API_KEY` and `GOOGLE_CSE_ID` are set

### "Claude API not configured"
- Verify `ANTHROPIC_API_KEY` in `.env`
- Check API key has sufficient credits

### Slow execution
- Normal! 4-8 hours is expected for 2,500 years
- Monitor progress in console output
- Check `search_count` and `claude_calls` stats

### Few results
- Check internet connection
- Verify Google CSE is configured for French sites
- Review console output for search errors

---

## Next Steps After Scraping

1. **Review output JSON:**
   ```bash
   cat chirac_2500years_conflicts.json | jq '.conflicts[] | {name, date, period, confidence_score}'
   ```

2. **Check statistics:**
   ```bash
   cat chirac_2500years_conflicts.json | jq '.stats'
   ```

3. **Import to database:**
   ```bash
   python scripts/import_conflicts.py chirac_2500years_conflicts.json
   ```

4. **Verify in database:**
   ```sql
   SELECT period, COUNT(*)
   FROM local_conflicts
   GROUP BY period
   ORDER BY period;
   ```

5. **View on map:**
   - Start frontend: `cd frontend && npm start`
   - Visit: http://localhost:3000
   - Orange markers = AI-discovered conflicts

---

## Files

- **Scraper:** `backend/app/scrapers/ai_conflict_scraper_expanded.py`
- **Run script:** `backend/scripts/run_expanded_scraper_chirac.sh`
- **Import script:** `backend/scripts/import_conflicts.py`
- **Output:** `backend/chirac_2500years_conflicts.json`

---

## Support

For issues or questions:
1. Check console output for error messages
2. Review this guide's troubleshooting section
3. Verify API keys and environment setup
4. Check API rate limits and quotas
