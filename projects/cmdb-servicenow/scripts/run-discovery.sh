#!/bin/bash
#
# CMDB Discovery - Main Execution Script
# Run full discovery cycle for all sources
#

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_PATH="${CONFIG_PATH:-$PROJECT_DIR/config/config.yaml}"
LOG_FILE="${LOG_FILE:-/var/log/cmdb-discovery.log}"
ENV_FILE="${ENV_FILE:-$PROJECT_DIR/config/.env}"

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

# Load environment variables
load_env() {
    if [ -f "$ENV_FILE" ]; then
        log "INFO" "Loading environment from $ENV_FILE"
        set -a
        source "$ENV_FILE"
        set +a
    else
        log "WARN" "Environment file not found: $ENV_FILE"
    fi
}

# Validate configuration
validate_config() {
    log "INFO" "Validating configuration..."
    
    if [ ! -f "$CONFIG_PATH" ]; then
        log "ERROR" "Configuration file not found: $CONFIG_PATH"
        exit 1
    fi
    
    # Check required environment variables
    local required_vars=("SERVICENOW_USER" "SERVICENOW_PASS")
    for var in "${required_vars[@]}"; do
        if [ -z "${!var:-}" ]; then
            log "ERROR" "Required environment variable not set: $var"
            exit 1
        fi
    done
    
    log "INFO" "Configuration validated"
}

# Check Python dependencies
check_dependencies() {
    log "INFO" "Checking Python dependencies..."
    
    if ! command -v python3 &> /dev/null; then
        log "ERROR" "Python3 not found"
        exit 1
    fi
    
    # Try to import required modules
    if ! python3 -c "import yaml, requests" 2>/dev/null; then
        log "INFO" "Installing Python dependencies..."
        pip3 install -r "$PROJECT_DIR/implementation/requirements.txt"
    fi
    
    log "INFO" "Dependencies OK"
}

# Run discovery
run_discovery() {
    log "INFO" "Starting CMDB discovery..."
    
    cd "$PROJECT_DIR/implementation"
    
    python3 main.py "$CONFIG_PATH" 2>&1 | tee -a "$LOG_FILE"
    
    local exit_code=${PIPESTATUS[0]}
    
    if [ $exit_code -eq 0 ]; then
        log "INFO" "Discovery completed successfully"
    else
        log "ERROR" "Discovery failed with exit code: $exit_code"
    fi
    
    return $exit_code
}

# Main execution
main() {
    log "INFO" "=========================================="
    log "INFO" "CMDB Discovery - Starting"
    log "INFO" "=========================================="
    
    load_env
    validate_config
    check_dependencies
    
    if run_discovery; then
        log "INFO" "Discovery cycle completed"
        exit 0
    else
        log "ERROR" "Discovery cycle failed"
        exit 1
    fi
}

# Handle arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help     Show this help"
        echo "  --validate Validate configuration only"
        echo ""
        echo "Environment:"
        echo "  CONFIG_PATH    Path to config file"
        echo "  LOG_FILE       Path to log file"
        echo "  ENV_FILE       Path to environment file"
        exit 0
        ;;
    --validate)
        load_env
        validate_config
        exit 0
        ;;
    *)
        main
        ;;
esac