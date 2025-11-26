#!/bin/bash
# Database Backup Script
# Creates a timestamped backup of the PostgreSQL database

# Exit on error
set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${PROJECT_ROOT}/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/spv_treasure_map_${TIMESTAMP}.sql"
RETENTION_DAYS=7

# Load environment variables
if [ -f "${PROJECT_ROOT}/.env" ]; then
    export $(grep -v '^#' "${PROJECT_ROOT}/.env" | xargs)
fi

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting database backup...${NC}"

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Extract database connection details from DATABASE_URL
# Format: postgresql://username:password@host:port/database
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}ERROR: DATABASE_URL not set${NC}"
    exit 1
fi

# Parse DATABASE_URL
DB_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
DB_PASS=$(echo $DATABASE_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')

echo "Database: ${DB_NAME}"
echo "Host: ${DB_HOST}:${DB_PORT}"
echo "Backup file: ${BACKUP_FILE}"

# Create backup
export PGPASSWORD="${DB_PASS}"
pg_dump -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" "${DB_NAME}" > "${BACKUP_FILE}"

if [ $? -eq 0 ]; then
    # Compress backup
    gzip "${BACKUP_FILE}"
    BACKUP_FILE="${BACKUP_FILE}.gz"
    
    BACKUP_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
    echo -e "${GREEN}✓ Backup successful: ${BACKUP_FILE} (${BACKUP_SIZE})${NC}"
else
    echo -e "${RED}✗ Backup failed${NC}"
    exit 1
fi

# Cleanup old backups (keep last RETENTION_DAYS days)
echo -e "${YELLOW}Cleaning up old backups (keeping last ${RETENTION_DAYS} days)...${NC}"
find "${BACKUP_DIR}" -name "spv_treasure_map_*.sql.gz" -type f -mtime +${RETENTION_DAYS} -delete

# List remaining backups
BACKUP_COUNT=$(find "${BACKUP_DIR}" -name "spv_treasure_map_*.sql.gz" -type f | wc -l)
echo -e "${GREEN}${BACKUP_COUNT} backups remaining${NC}"

echo -e "${GREEN}Backup complete!${NC}"
