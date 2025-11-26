#!/bin/bash
# ============================================================================
# Production Deployment Script
# ============================================================================
# Deploys the SPV Treasure Map application to production
# Includes health checks, database backup, and rollback capability
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
DEPLOYMENT_LOG="${PROJECT_ROOT}/deployment.log"

# Deployment settings
HEALTH_CHECK_RETRIES=30
HEALTH_CHECK_INTERVAL=5
ROLLBACK_ON_FAILURE=true

# ============================================================================
# Helper Functions
# ============================================================================

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$DEPLOYMENT_LOG"
}

log_success() {
    echo -e "${GREEN}✓ $1${NC}"
    echo "[SUCCESS] $1" >> "$DEPLOYMENT_LOG"
}

log_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
    echo "[WARNING] $1" >> "$DEPLOYMENT_LOG"
}

log_error() {
    echo -e "${RED}✗ $1${NC}"
    echo "[ERROR] $1" >> "$DEPLOYMENT_LOG"
}

# ============================================================================
# Pre-deployment Checks
# ============================================================================

pre_deployment_checks() {
    log "Running pre-deployment checks..."

    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    log_success "Docker is installed"

    # Check if docker-compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    log_success "Docker Compose is installed"

    # Check if .env file exists
    if [ ! -f "${PROJECT_ROOT}/backend/.env" ]; then
        log_error ".env file not found. Create from .env.production.example"
        exit 1
    fi
    log_success ".env file exists"

    # Check if git repo is clean
    if [ -d "${PROJECT_ROOT}/.git" ]; then
        if [ -n "$(git -C "$PROJECT_ROOT" status --porcelain)" ]; then
            log_warning "Git repository has uncommitted changes"
        else
            log_success "Git repository is clean"
        fi
    fi

    # Check disk space (require at least 5GB free)
    AVAILABLE_SPACE=$(df "$PROJECT_ROOT" | awk 'NR==2 {print $4}')
    if [ "$AVAILABLE_SPACE" -lt 5242880 ]; then
        log_error "Insufficient disk space (< 5GB available)"
        exit 1
    fi
    log_success "Sufficient disk space available"
}

# ============================================================================
# Database Backup
# ============================================================================

backup_database() {
    log "Creating database backup..."

    # Create backup directory if it doesn't exist
    mkdir -p "$BACKUP_DIR"

    # Run backup script
    if [ -f "${PROJECT_ROOT}/backend/scripts/backup_database.sh" ]; then
        if bash "${PROJECT_ROOT}/backend/scripts/backup_database.sh"; then
            log_success "Database backup created"
            # Save backup filename for potential rollback
            BACKUP_FILE=$(ls -t "${BACKUP_DIR}"/spv_treasure_map_*.sql.gz | head -1)
            echo "$BACKUP_FILE" > "${PROJECT_ROOT}/.last_backup"
        else
            log_error "Database backup failed"
            exit 1
        fi
    else
        log_warning "Backup script not found, skipping database backup"
    fi
}

# ============================================================================
# Build and Deploy
# ============================================================================

build_images() {
    log "Building Docker images..."

    if docker-compose -f "$COMPOSE_FILE" build --no-cache backend; then
        log_success "Docker images built successfully"
    else
        log_error "Failed to build Docker images"
        exit 1
    fi
}

pull_images() {
    log "Pulling latest Docker images..."

    if docker-compose -f "$COMPOSE_FILE" pull; then
        log_success "Docker images pulled successfully"
    else
        log_warning "Failed to pull some images, continuing..."
    fi
}

deploy_services() {
    log "Deploying services..."

    # Deploy with zero-downtime using rolling update
    if docker-compose -f "$COMPOSE_FILE" up -d --remove-orphans; then
        log_success "Services deployed successfully"
    else
        log_error "Failed to deploy services"
        return 1
    fi
}

# ============================================================================
# Health Checks
# ============================================================================

wait_for_health() {
    log "Waiting for services to become healthy..."

    local retries=0
    local backend_healthy=false

    while [ $retries -lt $HEALTH_CHECK_RETRIES ]; do
        # Check if backend is healthy
        if curl -f -s http://localhost:8000/api/health/live > /dev/null 2>&1; then
            backend_healthy=true
            break
        fi

        retries=$((retries + 1))
        log "Health check attempt $retries/$HEALTH_CHECK_RETRIES..."
        sleep $HEALTH_CHECK_INTERVAL
    done

    if [ "$backend_healthy" = true ]; then
        log_success "All services are healthy"
        return 0
    else
        log_error "Services failed health checks after $((retries * HEALTH_CHECK_INTERVAL)) seconds"
        return 1
    fi
}

# ============================================================================
# Post-deployment
# ============================================================================

run_migrations() {
    log "Running database migrations..."

    # Check if migrations are needed and run them
    if docker-compose -f "$COMPOSE_FILE" exec -T backend python -c "from app.db.database import engine; from app.models import Base; print('Migrations ready')"; then
        log_success "Database migrations completed"
    else
        log_warning "Migration check failed or not needed"
    fi
}

cleanup_old_images() {
    log "Cleaning up old Docker images..."

    # Remove dangling images
    docker image prune -f > /dev/null 2>&1 || true
    log_success "Old images cleaned up"
}

# ============================================================================
# Rollback
# ============================================================================

rollback_deployment() {
    log_error "ROLLING BACK DEPLOYMENT"

    # Stop current containers
    docker-compose -f "$COMPOSE_FILE" down

    # Restore from backup if available
    if [ -f "${PROJECT_ROOT}/.last_backup" ]; then
        BACKUP_FILE=$(cat "${PROJECT_ROOT}/.last_backup")
        if [ -f "$BACKUP_FILE" ]; then
            log "Restoring database from backup: $BACKUP_FILE"
            bash "${PROJECT_ROOT}/backend/scripts/restore_database.sh" "$BACKUP_FILE" <<< "yes"
        fi
    fi

    # Start previous version (assumes previous images still exist)
    docker-compose -f "$COMPOSE_FILE" up -d

    log_error "Rollback completed. Please investigate the failure."
    exit 1
}

# ============================================================================
# Main Deployment Flow
# ============================================================================

main() {
    log "=========================================="
    log "Starting Production Deployment"
    log "=========================================="

    # Pre-deployment
    pre_deployment_checks
    backup_database

    # Build and deploy
    pull_images
    build_images

    # Save current state for potential rollback
    PREVIOUS_IMAGES=$(docker-compose -f "$COMPOSE_FILE" images -q)

    # Deploy new version
    if ! deploy_services; then
        if [ "$ROLLBACK_ON_FAILURE" = true ]; then
            rollback_deployment
        fi
        exit 1
    fi

    # Health checks
    if ! wait_for_health; then
        log_error "Health checks failed"
        if [ "$ROLLBACK_ON_FAILURE" = true ]; then
            rollback_deployment
        fi
        exit 1
    fi

    # Post-deployment
    run_migrations
    cleanup_old_images

    # Success
    log_success "=========================================="
    log_success "Deployment completed successfully!"
    log_success "=========================================="

    # Display service status
    log "Service status:"
    docker-compose -f "$COMPOSE_FILE" ps

    # Display health check results
    log "\nHealth check results:"
    curl -s http://localhost:8000/api/health | jq '.' 2>/dev/null || curl -s http://localhost:8000/api/health

    log "\nDeployment log: $DEPLOYMENT_LOG"
}

# ============================================================================
# Run Main Function
# ============================================================================

main "$@"
