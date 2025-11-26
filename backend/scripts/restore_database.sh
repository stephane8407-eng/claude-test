#!/bin/bash
# Database Restore Script
# Restores a PostgreSQL database from a backup file

# Exit on error
set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${PROJECT_ROOT}/backups"

# Load environment variables
if [ -f "${PROJECT_ROOT}/.env" ]; then
    export $(grep -v '^#' "${PROJECT_ROOT}/.env" | xargs)
fi

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if backup file is provided
if [ -z "$1" ]; then
    echo -e "${RED}Usage: $0 <backup_file>${NC}"
    echo ""
    echo "Available backups:"
    ls -lh "${BACKUP_DIR}"/spv_treasure_map_*.sql.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "${BACKUP_FILE}" ]; then
    # Try to find it in backup directory
    if [ -f "${BACKUP_DIR}/${BACKUP_FILE}" ]; then
        BACKUP_FILE="${BACKUP_DIR}/${BACKUP_FILE}"
    else
        echo -e "${RED}ERROR: Backup file not found: ${BACKUP_FILE}${NC}"
        exit 1
    fi
fi

echo -e "${YELLOW}⚠️  WARNING: This will overwrite the current database!${NC}"
echo "Backup file: ${BACKUP_FILE}"
read -p "Are you sure you want to continue? (yes/no): " -r
echo

if [[ ! $REPLY =~ ^yes$ ]]; then
    echo "Restore cancelled"
    exit 0
fi

# Extract database connection details
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}ERROR: DATABASE_URL not set${NC}"
    exit 1
fi

DB_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
DB_PASS=$(echo $DATABASE_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')

echo -e "${GREEN}Starting database restore...${NC}"
echo "Database: ${DB_NAME}"
echo "Host: ${DB_HOST}:${DB_PORT}"

# Decompress if gzipped
TEMP_FILE="${BACKUP_FILE}"
if [[ "${BACKUP_FILE}" == *.gz ]]; then
    echo "Decompressing backup..."
    TEMP_FILE="${BACKUP_FILE%.gz}"
    gunzip -c "${BACKUP_FILE}" > "${TEMP_FILE}"
fi

# Restore database
export PGPASSWORD="${DB_PASS}"

echo "Dropping existing database..."
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d postgres -c "DROP DATABASE IF EXISTS ${DB_NAME};"

echo "Creating new database..."
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d postgres -c "CREATE DATABASE ${DB_NAME};"

echo "Restoring from backup..."
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" < "${TEMP_FILE}"

# Clean up temp file if we created one
if [[ "${BACKUP_FILE}" == *.gz ]]; then
    rm "${TEMP_FILE}"
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Restore successful${NC}"
else
    echo -e "${RED}✗ Restore failed${NC}"
    exit 1
fi

echo -e "${GREEN}Database restore complete!${NC}"
