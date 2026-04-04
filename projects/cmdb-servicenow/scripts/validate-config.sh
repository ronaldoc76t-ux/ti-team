#!/bin/bash
#
# Validate Configuration
# Check all config files are valid
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="$PROJECT_DIR/config"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_pass() { echo -e "${GREEN}✓${NC} $*"; }
log_fail() { echo -e "${RED}✗${NC} $*"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $*"; }

# Validate YAML files
validate_yaml() {
    local file="$1"
    python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null
}

# Main validation
main() {
    echo "Validating CMDB Discovery Configuration..."
    echo ""
    
    local errors=0
    
    # Check config.yaml
    if [ -f "$CONFIG_DIR/config.yaml" ]; then
        if validate_yaml "$CONFIG_DIR/config.yaml"; then
            log_pass "config.yaml is valid"
        else
            log_fail "config.yaml has syntax errors"
            ((errors++))
        fi
    else
        log_fail "config.yaml not found"
        ((errors++))
    fi
    
    # Check source configs
    for source in vmware openshift baremetal; do
        if [ -f "$CONFIG_DIR/sources/${source}.yaml" ]; then
            if validate_yaml "$CONFIG_DIR/sources/${source}.yaml"; then
                log_pass "sources/${source}.yaml is valid"
            else
                log_fail "sources/${source}.yaml has syntax errors"
                ((errors++))
            fi
        else
            log_warn "sources/${source}.yaml not found"
        fi
    done
    
    # Check ServiceNow config
    if [ -f "$CONFIG_DIR/servicenow.yaml" ]; then
        if validate_yaml "$CONFIG_DIR/servicenow.yaml"; then
            log_pass "servicenow.yaml is valid"
        else
            log_fail "servicenow.yaml has syntax errors"
            ((errors++))
        fi
    else
        log_fail "servicenow.yaml not found"
        ((errors++))
    fi
    
    # Check logging config
    if [ -f "$CONFIG_DIR/logging.yaml" ]; then
        if validate_yaml "$CONFIG_DIR/logging.yaml"; then
            log_pass "logging.yaml is valid"
        else
            log_fail "logging.yaml has syntax errors"
            ((errors++))
        fi
    fi
    
    echo ""
    if [ $errors -eq 0 ]; then
        log_pass "All configurations valid"
        exit 0
    else
        log_fail "$errors error(s) found"
        exit 1
    fi
}

main "$@"