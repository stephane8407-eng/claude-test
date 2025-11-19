# PostgreSQL + PostGIS Setup for SPV Treasure Map

## System: Ubuntu 24.04 LTS

### Step 1: Install PostgreSQL 16 + PostGIS

```bash
# Update package list
sudo apt update

# Install PostgreSQL 16 and PostGIS
sudo apt install -y postgresql-16 postgresql-16-postgis-3 postgresql-contrib

# Check installation
psql --version  # Should show PostgreSQL 16.x
```

### Step 2: Start PostgreSQL Service

```bash
# Start PostgreSQL
sudo systemctl start postgresql

# Enable auto-start on boot
sudo systemctl enable postgresql

# Check status
sudo systemctl status postgresql
```

### Step 3: Create Database and User

```bash
# Switch to postgres user
sudo -i -u postgres

# Create database
createdb spv_treasure_map

# Enter PostgreSQL shell
psql

# Inside psql, run these commands:
```

```sql
-- Create user with password
CREATE USER spv_admin WITH PASSWORD 'your_secure_password_here';

-- Grant privileges on database
GRANT ALL PRIVILEGES ON DATABASE spv_treasure_map TO spv_admin;

-- Connect to the database
\c spv_treasure_map

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Verify PostGIS is installed
SELECT PostGIS_version();

-- Grant schema privileges to user
GRANT ALL ON SCHEMA public TO spv_admin;
GRANT ALL ON ALL TABLES IN SCHEMA public TO spv_admin;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO spv_admin;

-- Exit psql
\q
```

```bash
# Exit postgres user shell
exit
```

### Step 4: Configure PostgreSQL for Local Development

```bash
# Edit PostgreSQL configuration to allow local connections
sudo nano /etc/postgresql/16/main/pg_hba.conf
```

Add this line after the existing `local` lines:
```
# SPV Treasure Map local access
local   spv_treasure_map    spv_admin                     md5
host    spv_treasure_map    spv_admin    127.0.0.1/32     md5
host    spv_treasure_map    spv_admin    ::1/128          md5
```

```bash
# Restart PostgreSQL to apply changes
sudo systemctl restart postgresql
```

### Step 5: Test Connection

```bash
# Test connection as spv_admin
psql -U spv_admin -d spv_treasure_map -h localhost

# If successful, you should see:
# spv_treasure_map=>

# Test PostGIS
SELECT PostGIS_version();

# Exit
\q
```

### Step 6: Create .env File for Backend

Create `backend/.env`:

```bash
# Database Configuration
DATABASE_URL=postgresql://spv_admin:your_secure_password_here@localhost:5432/spv_treasure_map

# Server Configuration
HOST=0.0.0.0
PORT=8000
RELOAD=True

# API Keys (for scrapers)
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_google_cse_id
ANTHROPIC_API_KEY=your_anthropic_api_key

# Security
SECRET_KEY=your-secret-key-for-jwt-tokens-generate-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Step 7: Install Python Dependencies

```bash
cd backend

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 8: Apply Database Schema

Once you have your Phase 1 MVP schema SQL, you can apply it:

**Option 1: Direct SQL file**
```bash
psql -U spv_admin -d spv_treasure_map -h localhost -f schema.sql
```

**Option 2: Via Python/SQLAlchemy (recommended)**
```bash
# After creating models (next step)
python -c "from app.models import Base; from app.database import engine; Base.metadata.create_all(bind=engine)"
```

**Option 3: Using Alembic migrations (best for production)**
```bash
# Initialize Alembic
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head
```

### Step 9: Verify Setup

```bash
# Connect to database
psql -U spv_admin -d spv_treasure_map -h localhost

# List tables
\dt

# Check PostGIS tables
SELECT tablename FROM pg_tables WHERE schemaname = 'public';

# Exit
\q
```

---

## Troubleshooting

### Issue: "peer authentication failed"

**Solution:** Make sure you're using `-h localhost` to force TCP/IP connection:
```bash
psql -U spv_admin -d spv_treasure_map -h localhost
```

### Issue: "password authentication failed"

**Solution:** Reset password:
```bash
sudo -u postgres psql
ALTER USER spv_admin WITH PASSWORD 'new_password';
\q
```

Update `backend/.env` with new password.

### Issue: PostGIS extension not found

**Solution:** Install PostGIS package:
```bash
sudo apt install postgresql-16-postgis-3
```

Then enable extension:
```sql
CREATE EXTENSION postgis;
```

### Issue: Permission denied on schema

**Solution:** Grant all privileges:
```sql
GRANT ALL ON SCHEMA public TO spv_admin;
GRANT ALL ON ALL TABLES IN SCHEMA public TO spv_admin;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO spv_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO spv_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO spv_admin;
```

---

## Quick Reference

**Start PostgreSQL:**
```bash
sudo systemctl start postgresql
```

**Stop PostgreSQL:**
```bash
sudo systemctl stop postgresql
```

**Restart PostgreSQL:**
```bash
sudo systemctl restart postgresql
```

**Connect to database:**
```bash
psql -U spv_admin -d spv_treasure_map -h localhost
```

**Backup database:**
```bash
pg_dump -U spv_admin -h localhost spv_treasure_map > backup_$(date +%Y%m%d).sql
```

**Restore database:**
```bash
psql -U spv_admin -d spv_treasure_map -h localhost < backup_20251119.sql
```

**Check PostGIS version:**
```sql
SELECT PostGIS_version();
```

**List spatial tables:**
```sql
SELECT f_table_name FROM geometry_columns;
```

---

## Next Steps

After PostgreSQL setup:

1. ✅ **Create database and enable PostGIS** (done)
2. **Paste your Phase 1 MVP schema SQL** - I'll help you apply it
3. **Create SQLAlchemy models** - I'll generate them based on your schema
4. **Set up FastAPI** - Basic REST API endpoints
5. **Test with sample data** - Import 3,439 battles and 3 test villages

Ready to paste your schema SQL!
