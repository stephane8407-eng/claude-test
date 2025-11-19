# SPV Treasure Map - Backend

FastAPI + PostgreSQL + PostGIS backend for historical treasure hunting intelligence platform.

## Quick Start

### 1. Setup PostgreSQL

Follow **[POSTGRES_SETUP.md](./POSTGRES_SETUP.md)** for detailed instructions:

```bash
# Install PostgreSQL 16 + PostGIS (Ubuntu)
sudo apt install postgresql-16 postgresql-16-postgis-3

# Create database
sudo -u postgres createdb spv_treasure_map

# Create user and enable PostGIS
sudo -u postgres psql
CREATE USER spv_admin WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE spv_treasure_map TO spv_admin;
\c spv_treasure_map
CREATE EXTENSION postgis;
\q
```

### 2. Setup Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env
# Edit .env with your database password and API keys
nano .env
```

### 3. Apply Database Schema

**Option A: Paste your Phase 1 MVP schema SQL**
```bash
# Save your schema to schema.sql, then:
psql -U spv_admin -d spv_treasure_map -h localhost -f schema.sql
```

**Option B: Use SQLAlchemy models**
```bash
# After creating models (see next section)
python -c "from app.database import init_db; init_db()"
```

**Option C: Use Alembic migrations (recommended)**
```bash
# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head
```

### 4. Start Development Server

```bash
# Start FastAPI server
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**API will be available at:**
- API: http://localhost:8000
- Docs: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

---

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── database.py          # Database configuration
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── battle.py        # Battle model
│   │   ├── place.py         # Place model
│   │   ├── place_context.py # AI scraper output
│   │   └── user.py          # User model
│   ├── api/                 # FastAPI routes
│   │   ├── __init__.py
│   │   ├── battles.py       # Battle endpoints
│   │   ├── places.py        # Place endpoints
│   │   └── users.py         # User endpoints
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── battle_service.py
│   │   └── place_service.py
│   └── scrapers/            # AI scrapers
│       ├── __init__.py
│       └── ai_led_village_scraper.py
├── alembic/                 # Database migrations
│   ├── versions/
│   └── env.py
├── main.py                  # FastAPI app entry point
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
└── POSTGRES_SETUP.md        # PostgreSQL setup guide
```

---

## Database Schema (Phase 1 MVP)

### Tables

**battles**
- Battle data (3,439 battles ready to import)
- PostGIS geometry for locations
- Date, location, participants, outcome

**places**
- Villages/towns (100 test villages planned)
- PostGIS point geometry
- Basic identity data

**place_contexts**
- AI scraper output (JSON)
- Linked to places
- Treasure probability scores
- Historical events, economics, archaeology

**users**
- Basic admin authentication
- Partnership tracking (villages contacted)

**usage_events**
- Analytics tracking
- User activity, searches, exports

---

## API Endpoints (Coming Soon)

### Battles
- `GET /api/battles` - List all battles
- `GET /api/battles/{id}` - Get battle details
- `GET /api/battles/nearby?lat=X&lng=Y&radius=10` - Battles near location
- `GET /api/battles/search?query=...` - Search battles

### Places
- `GET /api/places` - List all places
- `GET /api/places/{id}` - Get place details
- `GET /api/places/{id}/context` - Get AI-generated context
- `GET /api/places/nearby?lat=X&lng=Y&radius=10` - Places near location

### Admin
- `POST /api/admin/import-battles` - Import battles from CSV
- `POST /api/admin/scrape-village` - Run AI scraper on village

---

## Development

### Run Tests

```bash
pytest
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Check Database

```bash
# Connect to database
psql -U spv_admin -d spv_treasure_map -h localhost

# List tables
\dt

# Check PostGIS
SELECT PostGIS_version();

# Exit
\q
```

---

## Data Import

### Import Battles CSV (3,439 battles)

```bash
# Use import script (to be created)
python ../scripts/import_battles.py --file comprehensive_battles.csv
```

### Run AI Scraper on Village

```bash
# Use AI-led scraper
python app/scrapers/ai_led_village_scraper.py \
  --village "Manot" \
  --department "Charente" \
  --lat 45.75 \
  --lng 0.7833

# Import result to database
python ../scripts/import_village_context.py manot_ai_led.json
```

---

## Environment Variables

See `.env.example` for all configuration options:

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `GOOGLE_API_KEY` | Google Custom Search API key | For scrapers |
| `GOOGLE_CSE_ID` | Google Custom Search Engine ID | For scrapers |
| `ANTHROPIC_API_KEY` | Claude API key for AI processing | For scrapers |
| `SECRET_KEY` | JWT secret key | For auth |

---

## Next Steps

1. ✅ **PostgreSQL setup** - Follow POSTGRES_SETUP.md
2. **Paste Phase 1 schema** - Apply your designed schema
3. **Create SQLAlchemy models** - Will generate based on schema
4. **Create API routes** - Battles, places, contexts
5. **Import data** - 3,439 battles + 3 test villages
6. **Test API** - Use /api/docs to test endpoints
7. **Build frontend** - React + Leaflet map (next phase)

---

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL 16
- **Spatial**: PostGIS 3
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **AI**: Anthropic Claude
- **Search**: Google Custom Search API
- **Python**: 3.10+

---

## Support

For issues or questions:
1. Check POSTGRES_SETUP.md troubleshooting section
2. Check FastAPI docs: https://fastapi.tiangolo.com/
3. Check PostGIS docs: https://postgis.net/documentation/

---

**Ready to paste your Phase 1 MVP schema!** 🚀
