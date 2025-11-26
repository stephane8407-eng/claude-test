#!/bin/bash
# ============================================================================
# Production Health Check Script
# ============================================================================
# Comprehensive health checks for SPV Treasure Map production environment
# Can be used for monitoring, alerting, and load balancer health checks
# ============================================================================

# Exit codes
EXIT_SUCCESS=0
EXIT_WARNING=1
EXIT_CRITICAL=2
EXIT_UNKNOWN=3

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

# Health check endpoints
BACKEND_HOST="${BACKEND_HOST:-localhost:8000}"
BACKEND_HEALTH_URL="http://${BACKEND_HOST}/api/health"
BACKEND_LIVE_URL="http://${BACKEND_HOST}/api/health/live"
BACKEND_READY_URL="http://${BACKEND_HOST}/api/health/ready"
BACKEND_DB_URL="http://${BACKEND_HOST}/api/health/db"

# Thresholds
MAX_RESPONSE_TIME_MS=1000
MAX_MEMORY_PERCENT=80
MAX_DISK_PERCENT=90

# Mode
VERBOSE=false
JSON_OUTPUT=false

# ============================================================================
# Helper Functions
# ============================================================================

log() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${BLUE}[INFO]${NC} $1"
    fi
}

log_success() {
    if [ "$JSON_OUTPUT" = false ]; then
        echo -e "${GREEN}✓${NC} $1"
    fi
}

log_warning() {
    if [ "$JSON_OUTPUT" = false ]; then
        echo -e "${YELLOW}⚠${NC} $1"
    fi
}

log_error() {
    if [ "$JSON_OUTPUT" = false ]; then
        echo -e "${RED}✗${NC} $1"
    fi
}

# ============================================================================
# Health Check Functions
# ============================================================================

check_backend_liveness() {
    log "Checking backend liveness..."

    local start_time=$(date +%s%N)
    local response=$(curl -s -w "\n%{http_code}\n%{time_total}" "$BACKEND_LIVE_URL" 2>/dev/null)
    local end_time=$(date +%s%N)

    local http_code=$(echo "$response" | tail -2 | head -1)
    local time_total=$(echo "$response" | tail -1)
    local response_time_ms=$(echo "scale=0; $time_total * 1000" | bc)

    if [ "$http_code" = "200" ]; then
        log_success "Backend is alive (${response_time_ms}ms)"
        return 0
    else
        log_error "Backend liveness check failed (HTTP $http_code)"
        return 1
    fi
}

check_backend_readiness() {
    log "Checking backend readiness..."

    local response=$(curl -s -w "\n%{http_code}" "$BACKEND_READY_URL" 2>/dev/null)
    local http_code=$(echo "$response" | tail -1)

    if [ "$http_code" = "200" ]; then
        log_success "Backend is ready"
        return 0
    else
        log_warning "Backend not ready (HTTP $http_code)"
        return 1
    fi
}

check_database() {
    log "Checking database connectivity..."

    local response=$(curl -s -w "\n%{http_code}" "$BACKEND_DB_URL" 2>/dev/null)
    local http_code=$(echo "$response" | tail -1)
    local body=$(echo "$response" | head -n -1)

    if [ "$http_code" = "200" ]; then
        log_success "Database is healthy"
        return 0
    else
        log_error "Database check failed (HTTP $http_code)"
        return 1
    fi
}

check_docker_services() {
    log "Checking Docker services..."

    if ! docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        log_error "No Docker services are running"
        return 1
    fi

    local unhealthy=$(docker-compose -f "$COMPOSE_FILE" ps | grep -v "Up (healthy)\|Up [0-9]" | grep "Up" || true)

    if [ -n "$unhealthy" ]; then
        log_warning "Some services are not healthy:"
        echo "$unhealthy"
        return 1
    else
        log_success "All Docker services are healthy"
        return 0
    fi
}

check_response_time() {
    log "Checking API response time..."

    local start_time=$(date +%s%N)
    curl -s "$BACKEND_HEALTH_URL" > /dev/null 2>&1
    local end_time=$(date +%s%N)

    local response_time_ms=$(( (end_time - start_time) / 1000000 ))

    if [ $response_time_ms -lt $MAX_RESPONSE_TIME_MS ]; then
        log_success "Response time OK (${response_time_ms}ms < ${MAX_RESPONSE_TIME_MS}ms)"
        return 0
    else
        log_warning "Response time slow (${response_time_ms}ms >= ${MAX_RESPONSE_TIME_MS}ms)"
        return 1
    fi
}

check_disk_space() {
    log "Checking disk space..."

    local usage=$(df "$PROJECT_ROOT" | awk 'NR==2 {print $5}' | sed 's/%//')

    if [ "$usage" -lt $MAX_DISK_PERCENT ]; then
        log_success "Disk space OK (${usage}% < ${MAX_DISK_PERCENT}%)"
        return 0
    else
        log_warning "Disk space critical (${usage}% >= ${MAX_DISK_PERCENT}%)"
        return 1
    fi
}

check_memory_usage() {
    log "Checking memory usage..."

    # Get memory usage of backend container
    local backend_container=$(docker-compose -f "$COMPOSE_FILE" ps -q backend)

    if [ -z "$backend_container" ]; then
        log_warning "Backend container not found"
        return 1
    fi

    local mem_stats=$(docker stats --no-stream --format "{{.MemPerc}}" "$backend_container" | sed 's/%//')

    if [ -n "$mem_stats" ]; then
        local mem_usage=$(echo "$mem_stats" | cut -d'.' -f1)

        if [ "$mem_usage" -lt $MAX_MEMORY_PERCENT ]; then
            log_success "Memory usage OK (${mem_usage}% < ${MAX_MEMORY_PERCENT}%)"
            return 0
        else
            log_warning "Memory usage high (${mem_usage}% >= ${MAX_MEMORY_PERCENT}%)"
            return 1
        fi
    else
        log_warning "Could not get memory stats"
        return 1
    fi
}

check_ssl_certificate() {
    log "Checking SSL certificate..."

    local domain="spvtreasurehunt.com"
    local cert_path="${PROJECT_ROOT}/nginx/ssl/live/${domain}/cert.pem"

    if [ ! -f "$cert_path" ]; then
        log_warning "SSL certificate not found"
        return 1
    fi

    # Check certificate expiry
    local expiry_date=$(openssl x509 -in "$cert_path" -noout -enddate 2>/dev/null | cut -d= -f2)

    if [ -n "$expiry_date" ]; then
        local expiry_epoch=$(date -d "$expiry_date" +%s 2>/dev/null || date -j -f "%b %d %T %Y %Z" "$expiry_date" +%s)
        local now_epoch=$(date +%s)
        local days_remaining=$(( (expiry_epoch - now_epoch) / 86400 ))

        if [ $days_remaining -gt 30 ]; then
            log_success "SSL certificate valid (${days_remaining} days remaining)"
            return 0
        elif [ $days_remaining -gt 7 ]; then
            log_warning "SSL certificate expires soon (${days_remaining} days)"
            return 1
        else
            log_error "SSL certificate expires very soon (${days_remaining} days)"
            return 1
        fi
    else
        log_warning "Could not check SSL certificate expiry"
        return 1
    fi
}

# ============================================================================
# JSON Output
# ============================================================================

output_json() {
    local status="$1"
    local checks="$2"

    cat <<EOF
{
  "status": "$status",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "checks": $checks
}
EOF
}

# ============================================================================
# Main Health Check
# ============================================================================

main() {
    # Parse arguments
    while [ $# -gt 0 ]; do
        case "$1" in
            -v|--verbose)
                VERBOSE=true
                ;;
            -j|--json)
                JSON_OUTPUT=true
                ;;
            *)
                echo "Usage: $0 [-v|--verbose] [-j|--json]"
                exit $EXIT_UNKNOWN
                ;;
        esac
        shift
    done

    if [ "$JSON_OUTPUT" = false ]; then
        echo "=========================================="
        echo "SPV Treasure Map - Health Check"
        echo "=========================================="
        echo ""
    fi

    # Run all health checks
    local overall_status="healthy"
    local critical_failures=0
    local warnings=0

    # Critical checks (must pass)
    check_backend_liveness || { critical_failures=$((critical_failures + 1)); overall_status="critical"; }
    check_database || { critical_failures=$((critical_failures + 1)); overall_status="critical"; }

    # Warning checks (failures are non-critical)
    check_backend_readiness || warnings=$((warnings + 1))
    check_docker_services || warnings=$((warnings + 1))
    check_response_time || warnings=$((warnings + 1))
    check_disk_space || { warnings=$((warnings + 1)); [ "$overall_status" != "critical" ] && overall_status="warning"; }
    check_memory_usage || warnings=$((warnings + 1))
    check_ssl_certificate || warnings=$((warnings + 1))

    # Output results
    if [ "$JSON_OUTPUT" = true ]; then
        output_json "$overall_status" "[]"
    else
        echo ""
        echo "=========================================="

        if [ $critical_failures -eq 0 ] && [ $warnings -eq 0 ]; then
            echo -e "${GREEN}Status: HEALTHY${NC}"
            echo "All checks passed!"
            exit $EXIT_SUCCESS
        elif [ $critical_failures -eq 0 ]; then
            echo -e "${YELLOW}Status: WARNING${NC}"
            echo "$warnings warning(s) detected"
            exit $EXIT_WARNING
        else
            echo -e "${RED}Status: CRITICAL${NC}"
            echo "$critical_failures critical failure(s)"
            exit $EXIT_CRITICAL
        fi
    fi
}

# ============================================================================
# Run Main Function
# ============================================================================

main "$@"
