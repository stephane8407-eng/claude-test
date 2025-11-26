#!/bin/bash
# ============================================================================
# Production Rollback Script
# ============================================================================
# Rolls back the SPV Treasure Map application to a previous version
# Includes database restoration and service recovery
# ============================================================================

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.prod.yml"
BACKUP_DIR="${PROJECT_ROOT}/backend/backups"
ROLLBACK_LOG="${PROJECT_ROOT}/rollback.log"

# ============================================================================
# Helper Functions
# ============================================================================

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$ROLLBACK_LOG"
}

log_success() {
    echo -e "${GREEN}✓ $1${NC}"
    echo "[SUCCESS] $1" >> "$ROLLBACK_LOG"
}

log_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
    echo "[WARNING] $1" >> "$ROLLBACK_LOG"
}

log_error() {
    echo -e "${RED}✗ $1${NC}"
    echo "[ERROR] $1" >> "$ROLLBACK_LOG"
}

# ============================================================================
# Confirmation
# ============================================================================

confirm_rollback() {
    log_warning "=========================================="
    log_warning "PRODUCTION ROLLBACK"
    log_warning "=========================================="
    log_warning "This will:"
    log_warning "1. Stop all running services"
    log_warning "2. Restore database from backup"
    log_warning "3. Revert to previous application version"
    log_warning ""

    read -p "Are you sure you want to rollback? (yes/no): " -r
    echo

    if [[ ! $REPLY =~ ^yes$ ]]; then
        log "Rollback cancelled"
        exit 0
    fi
}

# ============================================================================
# List Available Backups
# ============================================================================

list_backups() {
    log "Available database backups:"
    echo ""

    if [ ! -d "$BACKUP_DIR" ] || [ -z "$(ls -A "$BACKUP_DIR")" ]; then
        log_error "No backups found in $BACKUP_DIR"
        exit 1
    fi

    # List backups with numbering
    local i=1
    declare -g -a BACKUP_FILES

    while IFS= read -r backup; do
        BACKUP_FILES[$i]="$backup"
        local size=$(du -h "$backup" | cut -f1)
        local date=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$backup" 2>/dev/null || stat -c "%y" "$backup" | cut -d' ' -f1-2)
        echo -e "  ${BLUE}[$i]${NC} $(basename "$backup") - ${size} - ${date}"
        i=$((i + 1))
    done < <(ls -t "${BACKUP_DIR}"/spv_treasure_map_*.sql.gz)

    echo ""
}

select_backup() {
    list_backups

    # Check if last_backup marker exists
    if [ -f "${PROJECT_ROOT}/.last_backup" ]; then
        SUGGESTED_BACKUP=$(cat "${PROJECT_ROOT}/.last_backup")
        log_warning "Suggested backup (pre-deployment): $(basename "$SUGGESTED_BACKUP")"
        echo ""
    fi

    read -p "Select backup number to restore (or 'q' to quit): " -r BACKUP_NUM

    if [[ $BACKUP_NUM == "q" ]]; then
        log "Rollback cancelled"
        exit 0
    fi

    if [[ ! $BACKUP_NUM =~ ^[0-9]+$ ]] || [ -z "${BACKUP_FILES[$BACKUP_NUM]}" ]; then
        log_error "Invalid selection"
        exit 1
    fi

    SELECTED_BACKUP="${BACKUP_FILES[$BACKUP_NUM]}"
    log "Selected backup: $(basename "$SELECTED_BACKUP")"
}

# ============================================================================
# Stop Services
# ============================================================================

stop_services() {
    log "Stopping all services..."

    if docker-compose -f "$COMPOSE_FILE" down; then
        log_success "Services stopped"
    else
        log_error "Failed to stop services"
        exit 1
    fi
}

# ============================================================================
# Restore Database
# ============================================================================

restore_database() {
    log "Restoring database from backup..."
    log "Backup file: $(basename "$SELECTED_BACKUP")"

    # Start only postgres for restoration
    docker-compose -f "$COMPOSE_FILE" up -d postgres
    sleep 10  # Wait for postgres to be ready

    # Restore database
    if bash "${PROJECT_ROOT}/backend/scripts/restore_database.sh" "$SELECTED_BACKUP" <<< "yes"; then
        log_success "Database restored successfully"
    else
        log_error "Database restoration failed"
        exit 1
    fi
}

# ============================================================================
# Revert Application
# ============================================================================

checkout_previous_version() {
    log "Checking git for previous version..."

    if [ ! -d "${PROJECT_ROOT}/.git" ]; then
        log_warning "Not a git repository, skipping version checkout"
        return 0
    fi

    # Show recent commits
    echo ""
    log "Recent commits:"
    git -C "$PROJECT_ROOT" log --oneline -10
    echo ""

    read -p "Enter commit hash to rollback to (or 'skip' to keep current): " -r COMMIT_HASH

    if [[ $COMMIT_HASH == "skip" ]]; then
        log "Keeping current application version"
        return 0
    fi

    if git -C "$PROJECT_ROOT" checkout "$COMMIT_HASH"; then
        log_success "Checked out commit: $COMMIT_HASH"
    else
        log_error "Failed to checkout commit"
        exit 1
    fi
}

rebuild_images() {
    log "Rebuilding Docker images..."

    if docker-compose -f "$COMPOSE_FILE" build --no-cache backend; then
        log_success "Images rebuilt"
    else
        log_error "Failed to rebuild images"
        exit 1
    fi
}

# ============================================================================
# Start Services
# ============================================================================

start_services() {
    log "Starting services..."

    if docker-compose -f "$COMPOSE_FILE" up -d; then
        log_success "Services started"
    else
        log_error "Failed to start services"
        exit 1
    fi
}

# ============================================================================
# Health Checks
# ============================================================================

verify_services() {
    log "Verifying services are healthy..."

    local retries=0
    local max_retries=30
    local healthy=false

    while [ $retries -lt $max_retries ]; do
        if curl -f -s http://localhost:8000/api/health/live > /dev/null 2>&1; then
            healthy=true
            break
        fi

        retries=$((retries + 1))
        log "Health check attempt $retries/$max_retries..."
        sleep 5
    done

    if [ "$healthy" = true ]; then
        log_success "Services are healthy"
        return 0
    else
        log_error "Services failed health checks"
        return 1
    fi
}

# ============================================================================
# Main Rollback Flow
# ============================================================================

main() {
    log "=========================================="
    log "Starting Production Rollback"
    log "=========================================="

    # Confirm rollback
    confirm_rollback

    # Select backup
    select_backup

    # Stop services
    stop_services

    # Restore database
    restore_database

    # Revert application (optional)
    checkout_previous_version
    rebuild_images

    # Start services
    start_services

    # Verify
    if verify_services; then
        log_success "=========================================="
        log_success "Rollback completed successfully!"
        log_success "=========================================="

        # Display service status
        log "Service status:"
        docker-compose -f "$COMPOSE_FILE" ps

        log "\nRollback log: $ROLLBACK_LOG"
    else
        log_error "Rollback completed but services are unhealthy"
        log_error "Please investigate manually"
        exit 1
    fi
}

# ============================================================================
# Run Main Function
# ============================================================================

main "$@"
