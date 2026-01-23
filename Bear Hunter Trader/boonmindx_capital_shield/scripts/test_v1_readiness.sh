#!/usr/bin/env bash
# V1 Readiness Test Script
# Tests all core v1 components before running full simulations

set -euo pipefail

echo "========================================="
echo "Capital Shield v1 Readiness Check"
echo "========================================="
echo ""

cd "$(dirname "$0")/.."

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass_count=0
fail_count=0

test_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((pass_count++))
}

test_fail() {
    echo -e "${RED}✗${NC} $1"
    ((fail_count++))
}

test_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

echo "1. Python Environment"
echo "---------------------"
if python3 --version > /dev/null 2>&1; then
    test_pass "Python 3 available: $(python3 --version 2>&1 | head -n1)"
else
    test_fail "Python 3 not found"
fi

echo ""
echo "2. Core Module Imports"
echo "----------------------"

# Test RSA module
if python3 -c "from live_sim.rsa import calculate_rsa; print('OK')" > /dev/null 2>&1; then
    test_pass "RSA module (live_sim/rsa.py)"
else
    test_fail "RSA module import failed"
fi

# Test Monte Carlo base
if python3 -c "from quant import run_monte_carlo_validation; print('OK')" > /dev/null 2>&1; then
    test_pass "Monte Carlo base module"
else
    test_fail "Monte Carlo base module import failed"
fi

# Test Monte Carlo Round 2
if python3 -c "from quant.run_monte_carlo_round2 import compute_metrics; print('OK')" > /dev/null 2>&1; then
    test_pass "Monte Carlo Round 2 module"
else
    test_fail "Monte Carlo Round 2 module import failed"
fi

# Test CoinGecko client (requires requests)
if python3 -c "from data.coin_gecko_client import CoinGeckoClient; print('OK')" > /dev/null 2>&1; then
    test_pass "CoinGecko client module"
else
    test_fail "CoinGecko client import failed (check 'requests' library)"
fi

echo ""
echo "3. Required Libraries"
echo "---------------------"

if python3 -c "import requests; print('OK')" > /dev/null 2>&1; then
    test_pass "requests library"
else
    test_fail "requests library not installed (pip install requests)"
fi

echo ""
echo "4. Data Files"
echo "-------------"

if [ -f "MontyCarloTest15Nov.txt" ]; then
    test_pass "Monte Carlo dataset (MontyCarloTest15Nov.txt)"
else
    test_warn "Monte Carlo dataset not found (optional for some tests)"
fi

echo ""
echo "5. Output Directories"
echo "---------------------"

mkdir -p reports/monte_carlo_round2 2>/dev/null && test_pass "reports/monte_carlo_round2/" || test_fail "Cannot create reports/monte_carlo_round2/"
mkdir -p reports/shadow_live 2>/dev/null && test_pass "reports/shadow_live/" || test_fail "Cannot create reports/shadow_live/"

echo ""
echo "6. Scripts Executable"
echo "---------------------"

if [ -x "scripts/run_shadow_live_coingecko.py" ]; then
    test_pass "scripts/run_shadow_live_coingecko.py"
else
    test_warn "scripts/run_shadow_live_coingecko.py not executable (chmod +x)"
fi

if [ -x "scripts/run_monte_carlo_round2.sh" ]; then
    test_pass "scripts/run_monte_carlo_round2.sh"
else
    test_warn "scripts/run_monte_carlo_round2.sh not executable (chmod +x)"
fi

echo ""
echo "7. RSA Formula Test"
echo "-------------------"

rsa_test=$(python3 -c "
from live_sim.rsa import calculate_rsa
# Test case: +50% return, -10% MDD
rsa = calculate_rsa(15000, 10000, 0.10)
expected = 0.7  # (0.5 * 1.0) + (0.5 * 0.9)
if abs(rsa - expected) < 0.01:
    print('PASS')
else:
    print(f'FAIL: expected {expected}, got {rsa}')
" 2>&1)

if echo "$rsa_test" | grep -q "PASS"; then
    test_pass "RSA calculation (v1 formula)"
else
    test_fail "RSA calculation: $rsa_test"
fi

echo ""
echo "========================================="
echo "Summary"
echo "========================================="
echo -e "${GREEN}Passed:${NC} $pass_count"
echo -e "${RED}Failed:${NC} $fail_count"
echo ""

if [ $fail_count -eq 0 ]; then
    echo -e "${GREEN}✓ All critical tests passed!${NC}"
    echo ""
    echo "You can now run:"
    echo "  1. Monte Carlo Round 2:"
    echo "     python3 -m quant.run_monte_carlo_round2"
    echo ""
    echo "  2. Shadow-Live (requires network):"
    echo "     python3 scripts/run_shadow_live_coingecko.py --max-iterations 3"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Fix issues before running simulations.${NC}"
    echo ""
    exit 1
fi

