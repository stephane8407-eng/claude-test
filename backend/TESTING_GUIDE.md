# API Testing Guide

## Quick Start

### 1. Apply Database Indexes Migration

First, apply the performance indexes for optimal query speed:

```bash
cd /home/user/claude-test/backend
psql -U spv_admin -d spv_treasure_map -h localhost -f schema/migrations/001_add_performance_indexes.sql
```

Expected output:
```
CREATE INDEX
CREATE INDEX
...
INSERT 0 1
ANALYZE
```

### 2. Start the API Server

```bash
cd /home/user/claude-test/backend
python main.py
```

Expected output:
```
🚀 Starting SPV Treasure Map API...
✅ PostGIS version: 3.x.x
✅ API started successfully!
🌍 Starting server at http://0.0.0.0:8000
📚 API docs at http://0.0.0.0:8000/api/docs
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3. Open Swagger UI

Open your browser and navigate to:
```
http://localhost:8000/api/docs
```

---

## Testing Each Endpoint

### ✅ Test 1: Health Check

**Endpoint:** `GET /health`

**Steps:**
1. Click on `/health` endpoint
2. Click "Try it out"
3. Click "Execute"

**Expected Response:**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

### ✅ Test 2: Battle Statistics (Enhanced)

**Endpoint:** `GET /api/battles/stats/summary`

**Steps:**
1. Click on `/api/battles/stats/summary`
2. Click "Try it out"
3. Click "Execute"

**Expected Response:**
```json
{
  "total_battles": 28,
  "by_war_period": [
    {"war_period": "WW1", "count": 15},
    {"war_period": "WW2", "count": 10}
  ],
  "by_country": [
    {"country": "FR", "count": 20}
  ],
  "by_significance": [
    {"significance": "major", "count": 10}
  ],
  "date_range": {
    "earliest": "1914-08-04",
    "latest": "1945-05-08",
    "span_years": 31
  },
  "casualties": {
    "total_estimated": 5450000,
    "average_per_battle": 194642.9,
    "highest_single_battle": 1000000,
    "battles_with_casualty_data": 28
  }
}
```

**What to verify:**
- ✅ Total battles = 28
- ✅ Date range shows earliest and latest battles
- ✅ Casualty statistics are calculated
- ✅ Span years is calculated

---

### ✅ Test 3: List Battles with Filtering

**Endpoint:** `GET /api/battles/`

**Test Case A: List first 5 battles**

Parameters:
- `skip`: 0
- `limit`: 5

**Test Case B: Filter by WW1**

Parameters:
- `war_period`: WW1
- `limit`: 10

**Test Case C: Filter by country France**

Parameters:
- `country`: FR
- `limit`: 10

**Expected Response Structure:**
```json
{
  "total": 28,
  "skip": 0,
  "limit": 5,
  "results": [
    {
      "id": 1,
      "name": "Battle of...",
      "war_period": "WW1",
      "country": "FR",
      "latitude": 50.0203,
      "longitude": 2.6951
    }
  ]
}
```

---

### ✅ Test 4: Get Battle by ID

**Endpoint:** `GET /api/battles/{battle_id}`

**Steps:**
1. First run `/api/battles/` to see available battle IDs
2. Note the first battle ID (e.g., ID 1)
3. Click on `/api/battles/{battle_id}`
4. Enter the battle ID
5. Click "Execute"

**Expected Response:**
```json
{
  "id": 1,
  "name": "Battle of the Somme",
  "war_period": "WW1",
  "start_date": "1916-07-01",
  "end_date": "1916-11-18",
  "latitude": 50.0203,
  "longitude": 2.6951,
  "country": "FR",
  "sides_involved": ["British Empire", "French Republic", "German Empire"],
  "outcome": "Allied victory",
  "significance": "major",
  "casualties_estimated": 1000000
}
```

---

### ✅ Test 5: Nearby Battles (Radius Search)

**Endpoint:** `GET /api/battles/nearby`

**Test Case: Find battles near Paris**

Parameters:
- `lat`: 48.8566
- `lng`: 2.3522
- `radius_km`: 100
- `limit`: 10

**Expected Response:**
```json
[
  {
    "id": 5,
    "name": "Battle near Paris",
    "latitude": 48.9000,
    "longitude": 2.4000,
    "distance_km": 15.3
  }
]
```

**What to verify:**
- ✅ Results are sorted by distance (closest first)
- ✅ All results have `distance_km` field
- ✅ All distances are within the specified radius

---

### ✅ Test 6: Bounding Box Search ⭐ NEW

**Endpoint:** `GET /api/battles/spatial/bbox`

**Test Case: Northern France + Belgium**

Parameters:
- `min_lat`: 48.5
- `min_lng`: 1.5
- `max_lat`: 51.0
- `max_lng`: 4.5
- `limit`: 20

**Expected Response:**
```json
{
  "total": 15,
  "returned": 15,
  "bounding_box": {
    "min_lat": 48.5,
    "min_lng": 1.5,
    "max_lat": 51.0,
    "max_lng": 4.5
  },
  "battles": [
    {
      "id": 1,
      "name": "Battle of the Somme",
      "significance": "major",
      "latitude": 50.0203,
      "longitude": 2.6951
    }
  ]
}
```

**What to verify:**
- ✅ All battles are within the bounding box
- ✅ Results are ordered by significance (major first)
- ✅ Response includes bounding_box summary

**Test Case: Invalid bounding box (should fail)**

Parameters:
- `min_lat`: 51.0
- `min_lng`: 1.5
- `max_lat`: 48.5  ← Less than min_lat (ERROR!)
- `max_lng`: 4.5

**Expected Response:**
```json
{
  "detail": "min_lat must be less than max_lat"
}
```

---

### ✅ Test 7: Route-Based Search ⭐ NEW

**Endpoint:** `POST /api/battles/spatial/route`

**Test Case: Paris to Brussels**

Request Body:
```json
{
  "coordinates": [
    [2.3522, 48.8566],
    [4.3517, 50.8503]
  ],
  "radius_km": 50
}
```

**Steps:**
1. Click on `/api/battles/spatial/route`
2. Click "Try it out"
3. Paste the JSON into the request body
4. Click "Execute"

**Expected Response:**
```json
{
  "total": 12,
  "route": {
    "coordinates": [[2.3522, 48.8566], [4.3517, 50.8503]],
    "radius_km": 50
  },
  "battles": [
    {
      "id": 3,
      "name": "Battle of Mons",
      "war_period": "WW1",
      "latitude": 50.4541,
      "longitude": 3.9500,
      "distance_km": 5.2
    }
  ]
}
```

**What to verify:**
- ✅ Results are sorted by distance from route (closest first)
- ✅ All results have `distance_km` field
- ✅ Battles are within radius_km of the route

**Test Case: With war period filter**

Request Body:
```json
{
  "coordinates": [
    [2.3522, 48.8566],
    [4.3517, 50.8503]
  ],
  "radius_km": 50,
  "war_period": "WW1"
}
```

**What to verify:**
- ✅ Only WW1 battles are returned
- ✅ Results still sorted by distance

---

### ✅ Test 8: Basic Search

**Endpoint:** `GET /api/battles/search/`

**Test Case: Search for "Somme"**

Parameters:
- `q`: Somme
- `limit`: 10

**Expected Response:**
```json
[
  {
    "id": 1,
    "name": "Battle of the Somme",
    "war_period": "WW1"
  }
]
```

---

### ✅ Test 9: Full-Text Search ⭐ NEW

**Endpoint:** `GET /api/battles/search/fulltext`

**Test Case A: Search battle names**

Parameters:
- `q`: Somme
- `search_fields`: name
- `limit`: 10

**Expected Response:**
```json
{
  "query": "Somme",
  "search_fields": ["name"],
  "total": 1,
  "battles": [
    {
      "id": 1,
      "name": "Battle of the Somme",
      "relevance_score": 10
    }
  ]
}
```

**Test Case B: Search by participants**

Parameters:
- `q`: British
- `search_fields`: sides
- `limit`: 20

**Expected Response:**
```json
{
  "query": "British",
  "search_fields": ["sides"],
  "total": 18,
  "battles": [
    {
      "id": 1,
      "name": "Battle of the Somme",
      "sides_involved": ["British Empire", "French Republic", "German Empire"],
      "relevance_score": 3
    }
  ]
}
```

**What to verify:**
- ✅ Results are sorted by relevance_score (highest first)
- ✅ Only battles with matching sides are returned
- ✅ Each result has relevance_score field

**Test Case C: Search all fields**

Parameters:
- `q`: victory
- `search_fields`: all
- `limit`: 20

**What to verify:**
- ✅ Searches name, outcome, and sides_involved
- ✅ Results include matches from any field
- ✅ Properly scored by relevance

---

### ✅ Test 10: Cache Statistics

**Endpoint:** `GET /api/cache/stats`

**Steps:**
1. Run several other endpoints first (to generate cache activity)
2. Click on `/api/cache/stats`
3. Click "Try it out"
4. Click "Execute"

**Expected Response:**
```json
{
  "hits": 150,
  "misses": 50,
  "total_requests": 200,
  "hit_rate_percent": 75.0,
  "uptime_seconds": 3600.5
}
```

**What to verify:**
- ✅ Cache is tracking hits and misses
- ✅ Hit rate percentage is calculated correctly
- ✅ Uptime is reasonable

---

## Command-Line Testing (Alternative to Swagger)

If you prefer command-line testing:

### Test Statistics

```bash
curl "http://localhost:8000/api/battles/stats/summary" | jq
```

### Test Bounding Box

```bash
curl "http://localhost:8000/api/battles/spatial/bbox?min_lat=48.5&min_lng=1.5&max_lat=51.0&max_lng=4.5" | jq
```

### Test Route-Based Search

```bash
curl -X POST "http://localhost:8000/api/battles/spatial/route" \
  -H "Content-Type: application/json" \
  -d '{
    "coordinates": [[2.3522, 48.8566], [4.3517, 50.8503]],
    "radius_km": 50,
    "war_period": "WW1"
  }' | jq
```

### Test Full-Text Search

```bash
curl "http://localhost:8000/api/battles/search/fulltext?q=British&search_fields=sides" | jq
```

---

## Performance Verification

### 1. Verify Indexes Were Created

```bash
psql -U spv_admin -d spv_treasure_map -h localhost -c "SELECT indexname FROM pg_indexes WHERE tablename = 'battles' ORDER BY indexname;"
```

Expected indexes:
- `idx_battles_casualties`
- `idx_battles_country`
- `idx_battles_end_date`
- `idx_battles_lat_lng`
- `idx_battles_location`
- `idx_battles_name_lower`
- `idx_battles_outcome_lower`
- `idx_battles_period`
- `idx_battles_period_country`
- `idx_battles_period_significance`
- `idx_battles_sides_involved_gin`
- `idx_battles_significance`
- `idx_battles_start_date`

### 2. Check Query Performance

```bash
psql -U spv_admin -d spv_treasure_map -h localhost -c "EXPLAIN ANALYZE SELECT * FROM battles WHERE war_period = 'WW1';"
```

Should show:
- ✅ Index Scan (not Seq Scan)
- ✅ Execution time < 1ms

---

## Troubleshooting

### Error: "Module 'app.utils' not found"

**Solution:** Ensure the utils directory exists:
```bash
ls -la backend/app/utils/
# Should show: __init__.py, cache.py
```

### Error: "PostGIS version not found"

**Solution:** Check PostGIS is installed:
```bash
psql -U spv_admin -d spv_treasure_map -h localhost -c "SELECT PostGIS_version();"
```

### Error: "Battle not found"

**Solution:** Check battles exist in database:
```bash
psql -U spv_admin -d spv_treasure_map -h localhost -c "SELECT COUNT(*) FROM battles;"
```

Should return: `28`

### Slow Queries

**Solution:** Apply the performance indexes:
```bash
psql -U spv_admin -d spv_treasure_map -h localhost -f backend/schema/migrations/001_add_performance_indexes.sql
```

---

## Test Results Checklist

After testing all endpoints, verify:

- [ ] ✅ All 10 endpoints return 200 OK
- [ ] ✅ Statistics show correct totals (28 battles)
- [ ] ✅ Date ranges are calculated correctly
- [ ] ✅ Spatial searches return results within bounds
- [ ] ✅ Route-based search finds battles along path
- [ ] ✅ Full-text search scores relevance correctly
- [ ] ✅ Bounding box validation works (rejects invalid boxes)
- [ ] ✅ Cache statistics are tracking hits/misses
- [ ] ✅ All responses include proper JSON structure
- [ ] ✅ Error messages are clear and helpful

---

## Next Steps

Once all tests pass:

1. **Apply indexes migration** (if not already done)
2. **Monitor cache hit rates** via `/api/cache/stats`
3. **Test with real user scenarios** (map interactions)
4. **Load test** with larger datasets (3,439 battles)
5. **Frontend integration** with React + Leaflet

---

**Happy Testing! 🎯**
