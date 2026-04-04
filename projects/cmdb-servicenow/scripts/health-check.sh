#!/bin/bash
#
# Health Check - Verify collectors and connections
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_pass() { echo -e "${GREEN}✓${NC} $*"; }
log_fail() { echo -e "${RED}✗${NC} $*"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $*"; }

# Check connectivity to sources
check_sources() {
    echo "Checking source connectivity..."
    
    # Source VMware vCenter
    if command -v govmomi &> /dev/null || [ -f "$PROJECT_DIR/implementation/collectors/vmware.py" ]; then
        log_pass "VMware collector available"
    else
        log_warn "VMware collector not available"
    fi
    
    # Check OpenShift
    if command -v oc &> /dev/null; then
        log_pass "OpenShift CLI available"
    else
        log_warn "OpenShift CLI not available"
    fi
    
    # Check SNMP
    if command -v snmpwalk &> /dev/null; then
        log_pass "SNMP tools available"
    else
        log_warn "SNMP tools not available"
    fi
}

# Check Python environment
check_python() {
    echo "Checking Python environment..."
    
    if command -v python3 &> /dev/null; then
        log_pass "Python3 available: $(python3 --version)"
    else
        log_fail "Python3 not available"
        exit 1
    fi
    
    # Check required modules
    local modules=("yaml" "requests" "kubernetes")
    for mod in "${modules[@]}"; do
        if python3 -c "import $mod" 2>/dev/null; then
            log_pass "Module $mod available"
        else
            log_warn "Module $mod not installed"
        fi
    done
}

# Check ServiceNow connectivity
check_servicenow() {
    echo "Checking ServiceNow connectivity..."
    
    export CONFIG_PATH="${CONFIG_PATH:-$PROJECT_DIR/config/config.yaml}"
    export SERVICENOW_USER="${SERVICENOW_USER:-}"
    export SERVICENOW_PASS="${SERVICENOW_PASS:-}"
    
    if [ -z "$SERVICENOW_USER" ] || [ -z "$SERVICENOW_PASS" ]; then
        log_warn "ServiceNow credentials not set"
        return
    fi
    
    # Quick test - just check if we can reach the API
    if python3 -c "
import requests
from requests.auth import HTTPBasicAuth
r = requests.get(
    'https://' + '$SERVICENOW_INSTANCE' + '.service-now.com/api/now/table/cmdb_ci_server',
    auth=HTTPBasicAuth('$SERVICENOW_USER', '$SERVICENOW_PASS'),
    params={'sysparm_limit': 1},
    timeout=5
)
print(r.status_code)
" 2>/dev/null; then
        log_pass "ServiceNow API reachable"
    else
        log_warn "ServiceNow API not reachable"
    fi
}

# Main
main() {
    echo "CMDB Discovery - Health Check"
    echo "=============================="
    echo ""
    
    check_python
    echo ""
    check_sources
    echo ""
    check_servicenow
    
    echo ""
    log_pass "Health check complete"
}

main "$@"