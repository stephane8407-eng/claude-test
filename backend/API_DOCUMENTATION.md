# SPV Treasure Map API Documentation

**Version:** 1.0.0
**Base URL:** `http://localhost:8000`
**Interactive Docs:** `http://localhost:8000/api/docs`
**ReDoc:** `http://localhost:8000/api/redoc`

## Overview

The SPV Treasure Map API provides comprehensive access to historical battle data across France, UK, and Belgium. The API features:

- ✅ **28 battles** in database (expandable to 3,439+)
- 🗺️ **PostGIS spatial queries** for location-based search
- 🔍 **Full-text search** with relevance scoring
- 📊 **Statistics and analytics** endpoints
- ⚡ **In-memory caching** for performance
- 📍 **Route-based search** for travel planning

---

## Table of Contents

1. [Authentication](#authentication)
2. [Core Endpoints](#core-endpoints)
3. [Spatial Search](#spatial-search)
4. [Full-Text Search](#full-text-search)
5. [Statistics](#statistics)
6. [Performance & Caching](#performance--caching)
7. [Response Formats](#response-formats)
8. [Error Handling](#error-handling)
9. [Examples](#examples)

---

## Authentication

**Current Status:** No authentication required (MVP)
**Phase 2:** JWT-based authentication for user-specific features

---

## Core Endpoints

### 1. List Battles

**GET** `/api/battles/`

List all battles with optional filtering and pagination.

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `skip` | integer | No | 0 | Pagination offset |
| `limit` | integer | No | 100 | Max results (1-1000) |
| `war_period` | string | No | - | Filter by period (WW1, WW2, Napoleonic, etc.) |
| `country` | string | No | - | Filter by country (FR, UK, BE) |
| `significance` | string | No | - | Filter by significance (minor, moderate, major) |

#### Example Request

```bash
curl "http://localhost:8000/api/battles/?war_period=WW1&country=FR&limit=10"
```

#### Example Response

```json
{
  "total": 28,
  "skip": 0,
  "limit": 10,
  "results": [
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
      "casualties_estimated": 1000000,
      "sources": ["https://en.wikipedia.org/wiki/Battle_of_the_Somme"]
    }
  ]
}
```

---

### 2. Get Battle by ID

**GET** `/api/battles/{battle_id}`

Get detailed information about a specific battle.

#### Example Request

```bash
curl "http://localhost:8000/api/battles/1"
```

#### Example Response

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
  "casualties_estimated": 1000000,
  "sources": ["https://en.wikipedia.org/wiki/Battle_of_the_Somme"]
}
```

---

## Spatial Search

### 3. Nearby Battles (Radius Search)

**GET** `/api/battles/nearby`

Find battles near a specific location within a given radius.

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `lat` | float | Yes | Latitude (-90 to 90) |
| `lng` | float | Yes | Longitude (-180 to 180) |
| `radius_km` | float | No | Search radius in km (1-500, default 50) |
| `limit` | integer | No | Max results (1-100, default 20) |

#### Example Request

```bash
# Find battles within 50km of Paris
curl "http://localhost:8000/api/battles/nearby?lat=48.8566&lng=2.3522&radius_km=50"
```

#### Example Response

```json
[
  {
    "id": 5,
    "name": "Battle of Paris",
    "war_period": "WW2",
    "latitude": 48.8566,
    "longitude": 2.3522,
    "country": "FR",
    "significance": "major",
    "distance_km": 12.5
  }
]
```

---

### 4. Bounding Box Search

**GET** `/api/battles/spatial/bbox`

Find all battles within a rectangular area (map viewport).

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `min_lat` | float | Yes | Southwest corner latitude |
| `min_lng` | float | Yes | Southwest corner longitude |
| `max_lat` | float | Yes | Northeast corner latitude |
| `max_lng` | float | Yes | Northeast corner longitude |
| `war_period` | string | No | Filter by war period |
| `limit` | integer | No | Max results (1-1000, default 100) |

#### Example Request

```bash
# Find WW1 battles in northern France
curl "http://localhost:8000/api/battles/spatial/bbox?min_lat=48.5&min_lng=1.5&max_lat=51.0&max_lng=4.5&war_period=WW1"
```

#### Example Response

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

---

### 5. Route-Based Search ⭐ NEW

**POST** `/api/battles/spatial/route`

Find battles along a travel route within a given radius.

**Perfect for:** "Show me all WW1 battles within 50km of my Paris→Brussels road trip"

#### Request Body

```json
{
  "coordinates": [
    [2.3522, 48.8566],  // Paris [lng, lat]
    [4.3517, 50.8503]   // Brussels [lng, lat]
  ],
  "radius_km": 50,
  "war_period": "WW1"  // Optional
}
```

#### Example Request

```bash
curl -X POST "http://localhost:8000/api/battles/spatial/route" \
  -H "Content-Type: application/json" \
  -d '{
    "coordinates": [[2.3522, 48.8566], [4.3517, 50.8503]],
    "radius_km": 50,
    "war_period": "WW1"
  }'
```

#### Example Response

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
    },
    {
      "id": 7,
      "name": "Battle of Charleroi",
      "war_period": "WW1",
      "latitude": 50.4108,
      "longitude": 4.4446,
      "distance_km": 15.8
    }
  ]
}
```

---

## Full-Text Search

### 6. Basic Search

**GET** `/api/battles/search/`

Simple text search in battle names and outcomes.

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | Yes | Search query (min 2 chars) |
| `limit` | integer | No | Max results (1-100, default 50) |

#### Example Request

```bash
curl "http://localhost:8000/api/battles/search/?q=Somme"
```

---

### 7. Advanced Full-Text Search ⭐ NEW

**GET** `/api/battles/search/fulltext`

Full-text search with field selection and relevance scoring.

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `q` | string | Yes | - | Search query (min 2 chars) |
| `search_fields` | string | No | `name,outcome,sides` | Fields to search (comma-separated) |
| `limit` | integer | No | 50 | Max results (1-200) |

#### Search Fields Options

- `name` - Search battle names only
- `outcome` - Search battle outcomes only
- `sides` - Search participating sides (array field)
- `all` - Search all fields

#### Example Requests

```bash
# Find battles with "Somme" in name
curl "http://localhost:8000/api/battles/search/fulltext?q=Somme&search_fields=name"

# Find battles involving "British"
curl "http://localhost:8000/api/battles/search/fulltext?q=British&search_fields=sides"

# Search all fields
curl "http://localhost:8000/api/battles/search/fulltext?q=victory&search_fields=all"
```

#### Example Response

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
    },
    {
      "id": 4,
      "name": "Battle of Ypres",
      "sides_involved": ["British Empire", "German Empire"],
      "relevance_score": 3
    }
  ]
}
```

**Relevance Scoring:**
- Exact name match: 10 points
- Name contains query: 5 points
- Outcome contains query: 5 points
- Side contains query: 3 points per match

---

## Statistics

### 8. Battle Statistics ⭐ ENHANCED

**GET** `/api/battles/stats/summary`

Comprehensive statistics about battles in the database.

#### Example Request

```bash
curl "http://localhost:8000/api/battles/stats/summary"
```

#### Example Response

```json
{
  "total_battles": 28,
  "by_war_period": [
    {"war_period": "WW1", "count": 15},
    {"war_period": "WW2", "count": 10},
    {"war_period": "Napoleonic", "count": 3}
  ],
  "by_country": [
    {"country": "FR", "count": 20},
    {"country": "BE", "count": 5},
    {"country": "UK", "count": 3}
  ],
  "by_significance": [
    {"significance": "major", "count": 10},
    {"significance": "moderate", "count": 12},
    {"significance": "minor", "count": 6}
  ],
  "date_range": {
    "earliest": "1805-12-02",
    "latest": "1945-05-08",
    "span_years": 140
  },
  "casualties": {
    "total_estimated": 5450000,
    "average_per_battle": 194642.9,
    "highest_single_battle": 1000000,
    "battles_with_casualty_data": 28
  }
}
```

---

## Performance & Caching

### 9. Cache Statistics

**GET** `/api/cache/stats`

Get cache performance metrics.

#### Example Request

```bash
curl "http://localhost:8000/api/cache/stats"
```

#### Example Response

```json
{
  "hits": 150,
  "misses": 50,
  "total_requests": 200,
  "hit_rate_percent": 75.0,
  "uptime_seconds": 3600.5
}
```

---

## Response Formats

### Success Response

All successful responses return HTTP 200 with JSON data.

### Error Response

```json
{
  "detail": "Battle 999 not found"
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request (invalid parameters) |
| 404 | Not Found (battle doesn't exist) |
| 422 | Validation Error (missing required fields) |
| 500 | Internal Server Error |

---

## Error Handling

### Example: Invalid Battle ID

**Request:**
```bash
curl "http://localhost:8000/api/battles/999"
```

**Response:**
```json
{
  "detail": "Battle 999 not found"
}
```

### Example: Invalid Bounding Box

**Request:**
```bash
curl "http://localhost:8000/api/battles/spatial/bbox?min_lat=50&min_lng=2&max_lat=48&max_lng=4"
```

**Response:**
```json
{
  "detail": "min_lat must be less than max_lat"
}
```

---

## Examples

### Example 1: Find WW1 Battles Near Current Location

```bash
# Get battles within 30km of Amiens, France
curl "http://localhost:8000/api/battles/nearby?lat=49.8941&lng=2.2958&radius_km=30&war_period=WW1"
```

### Example 2: Road Trip Battle Finder

```bash
# Find WW2 battles along Paris → Lyon route (within 50km)
curl -X POST "http://localhost:8000/api/battles/spatial/route" \
  -H "Content-Type: application/json" \
  -d '{
    "coordinates": [
      [2.3522, 48.8566],
      [4.8357, 45.7640]
    ],
    "radius_km": 50,
    "war_period": "WW2"
  }'
```

### Example 3: Map Viewport Battles

```bash
# Get all battles visible in current map view
# (e.g., northern France + Belgium)
curl "http://localhost:8000/api/battles/spatial/bbox?min_lat=49.5&min_lng=2.0&max_lat=51.5&max_lng=5.0"
```

### Example 4: Search Battles by Participants

```bash
# Find all battles involving German forces
curl "http://localhost:8000/api/battles/search/fulltext?q=German&search_fields=sides"
```

### Example 5: Get Dashboard Statistics

```bash
# Get overview stats for admin dashboard
curl "http://localhost:8000/api/battles/stats/summary"
```

---

## Database Indexes

For optimal performance, the following indexes are created:

**Spatial Indexes:**
- `idx_battles_location` - GIST index on (longitude, latitude)
- `idx_battles_lat_lng` - Composite index for bounding box queries

**Filter Indexes:**
- `idx_battles_period` - War period filtering
- `idx_battles_country` - Country filtering
- `idx_battles_significance` - Significance filtering

**Search Indexes:**
- `idx_battles_sides_involved_gin` - GIN index for array search
- `idx_battles_name_lower` - Case-insensitive name search
- `idx_battles_outcome_lower` - Case-insensitive outcome search

**Statistics Indexes:**
- `idx_battles_start_date` - Date range queries
- `idx_battles_casualties` - Casualty statistics

To apply these indexes:
```bash
psql -U spv_admin -d spv_treasure_map -f backend/schema/migrations/001_add_performance_indexes.sql
```

---

## Testing in Swagger UI

1. **Start the API:**
   ```bash
   cd backend
   python main.py
   ```

2. **Open Swagger UI:**
   ```
   http://localhost:8000/api/docs
   ```

3. **Test Each Endpoint:**
   - Click on any endpoint to expand
   - Click "Try it out"
   - Fill in parameters
   - Click "Execute"
   - View response

4. **Example Test Flow:**
   - GET `/api/battles/stats/summary` - See overview
   - GET `/api/battles/?limit=10` - List battles
   - GET `/api/battles/1` - View specific battle
   - GET `/api/battles/nearby?lat=50&lng=3&radius_km=50` - Spatial search
   - POST `/api/battles/spatial/route` - Route-based search

---

## Performance Tips

1. **Use Pagination:** Always set reasonable `limit` values
2. **Cache Stats:** Monitor `/api/cache/stats` for hit rates
3. **Bounding Box:** Prefer bbox over radius for map viewports
4. **Indexes:** Apply all migrations for optimal query speed
5. **Production:** Use Redis for distributed caching

---

## Next Steps (Phase 2)

- [ ] JWT authentication
- [ ] User-specific battle lists (favorites)
- [ ] Battle comments and ratings
- [ ] Place context integration
- [ ] Export to GPX/KML for GPS devices
- [ ] WebSocket for real-time updates

---

## Support

- **GitHub Issues:** [github.com/stephane8407-eng/claude-test/issues](https://github.com/stephane8407-eng/claude-test/issues)
- **API Docs:** http://localhost:8000/api/docs
- **Database Schema:** `backend/schema/phase_1_mvp_schema.sql`

---

**Last Updated:** 2025-11-21
**API Version:** 1.0.0
**Database:** PostgreSQL 17 + PostGIS 3
