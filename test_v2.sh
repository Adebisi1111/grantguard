#!/bin/bash
# test_v2.sh - Test GrantGuard v2 end-to-end

ADDR="0x671990450Bab8f89144F50B6A619c6382E824172"

echo "=== Step 1: Create Grant ==="
echo "test1234" | genlayer write "$ADDR" create_grant \
  --args 'test-grant-1' 'DeFi Innovation Grant' 'Supporting DeFi projects' \
  'Open to all developers' 'Technical merit and innovation' \
  'Max 10000 GEN per project' 'GitHub repo with working demo' '2026-12-31' \
  --fee-profile fee-profile.json 2>&1 | tail -5

echo ""
echo "=== Step 2: Fund Grant (1 GEN) ==="
echo "test1234" | genlayer write "$ADDR" fund_grant \
  --args 'test-grant-1' \
  --fee-profile fee-profile.json \
  --value 1000000000000000000 2>&1 | tail -5

echo ""
echo "=== Step 3: Check Grant State ==="
genlayer call "$ADDR" get_grant --args 'test-grant-1' 2>&1 | tail -15

echo ""
echo "=== Step 4: Submit Application ==="
echo "test1234" | genlayer write "$ADDR" submit_application \
  --args 'test-grant-1' 'DeFi Analytics Dashboard' \
  'A comprehensive DeFi analytics dashboard with real-time data' \
  'Team of 3 senior developers' 500000000000000000 \
  'https://defi-dashboard.example.com' \
  'https://github.com' \
  'https://github.com/ethereum/ethereum-org-website' \
  'Additional info about project' \
  --fee-profile fee-profile.json 2>&1 | tail -5

echo ""
echo "=== Step 5: Check Application State ==="
genlayer call "$ADDR" get_application --args 'app_0' 2>&1 | tail -15

echo ""
echo "=== Step 6: Evaluate Application (validators fetch evidence - 1-3 min) ==="
echo "test1234" | genlayer write "$ADDR" evaluate_application \
  --args 'app_0' \
  --fee-profile fee-profile.json 2>&1 | tail -5

echo ""
echo "=== Step 7: Check Evaluation Result ==="
genlayer call "$ADDR" get_application --args 'app_0' 2>&1 | tail -15

echo ""
echo "=== Step 8: Release Funds ==="
echo "test1234" | genlayer write "$ADDR" release_funds \
  --args 'app_0' \
  --fee-profile fee-profile.json 2>&1 | tail -5

echo ""
echo "=== Step 9: Final Grant State ==="
genlayer call "$ADDR" get_grant --args 'test-grant-1' 2>&1 | tail -15

echo ""
echo "=== Step 10: Final Application State ==="
genlayer call "$ADDR" get_application --args 'app_0' 2>&1 | tail -15
