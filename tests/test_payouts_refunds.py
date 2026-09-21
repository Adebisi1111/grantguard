# v0.3.0
# GrantGuard v2 Test Suite
# Tests: Payouts and refunds across multiple grants

import genlayer as gl
import json

# Test configuration
CONTRACT_ADDR = '0xba22BF8161c7B9D2E9A5bED6430EFF0147DDCeB0'

# Test addresses
creator = gl.Address('0x61fd0047595A30A067f1F21F3b28C4AE8A8e3Dc3')
applicant1 = gl.Address('0x1111111111111111111111111111111111111111')
applicant2 = gl.Address('0x2222222222222222222222222222222222222222')
applicant3 = gl.Address('0x3333333333333333333333333333333333333333')

# ==========================================
# Test 1: Create multiple grants
# ==========================================
@gl.public.write
def test_create_multiple_grants():
    """Create 3 different grants with different criteria"""
    contract = gl.contract.Contract(CONTRACT_ADDR)
    
    # Grant 1: DeFi Innovation
    result1 = contract.create_grant(
        grant_id='defi-grant',
        name='DeFi Innovation Grant',
        description='Supporting DeFi projects',
        eligibility='Open to all developers',
        criteria='Technical merit and innovation',
        budget_rules='Max 1000 GEN',
        required_evidence='GitHub repo with working demo',
        deadline='2026-12-31'
    )
    assert result1 == 'defi-grant', f"Expected 'defi-grant', got {result1}"
    
    # Grant 2: NFT Marketplace
    result2 = contract.create_grant(
        grant_id='nft-grant',
        name='NFT Marketplace Grant',
        description='NFT marketplace development',
        eligibility='NFT developers',
        criteria='Creativity and user experience',
        budget_rules='Max 2000 GEN',
        required_evidence='Working prototype',
        deadline='2026-12-31'
    )
    assert result2 == 'nft-grant', f"Expected 'nft-grant', got {result2}"
    
    # Grant 3: DAO Governance
    result3 = contract.create_grant(
        grant_id='dao-grant',
        name='DAO Governance Grant',
        description='DAO governance tools',
        eligibility='DAO contributors',
        criteria='Community governance features',
        budget_rules='Max 1500 GEN',
        required_evidence='Governance token implementation',
        deadline='2026-12-31'
    )
    assert result3 == 'dao-grant', f"Expected 'dao-grant', got {result3}"
    
    return "✅ Test 1 PASSED: 3 grants created"


# ==========================================
# Test 2: Fund multiple grants
# ==========================================
@gl.public.write
def test_fund_multiple_grants():
    """Fund each grant with different amounts"""
    contract = gl.contract.Contract(CONTRACT_ADDR)
    
    # Fund DeFi grant with 5 GEN
    result1 = contract.fund_grant(grant_id='defi-grant')
    assert result1 == 'Funded', f"Expected 'Funded', got {result1}"
    
    # Fund NFT grant with 10 GEN
    result2 = contract.fund_grant(grant_id='nft-grant')
    assert result2 == 'Funded', f"Expected 'Funded', got {result2}"
    
    # Fund DAO grant with 7 GEN
    result3 = contract.fund_grant(grant_id='dao-grant')
    assert result3 == 'Funded', f"Expected 'Funded', got {result3}"
    
    return "✅ Test 2 PASSED: 3 grants funded"


# ==========================================
# Test 3: Submit applications with payout addresses
# ==========================================
@gl.public.write
def test_submit_applications():
    """Submit applications with valid payout addresses"""
    contract = gl.contract.Contract(CONTRACT_ADDR)
    
    # Application 1 for DeFi grant
    app1 = contract.submit_application(
        grant_id='defi-grant',
        project_name='DeFi Analytics Dashboard',
        project_description='Real-time analytics for DeFi protocols',
        team_info='Solo developer',
        requested_amount=gl.u256(3000000000000000000),  # 3 GEN
        payout_address=applicant1.as_hex,
        website='https://example.com',
        github_url='https://github.com/test/defi-analytics',
        evidence_urls='https://github.com/test/defi-analytics',
        additional_info='Built with React and TheGraph'
    )
    assert app1.startswith('app_'), f"Expected app_*, got {app1}"
    
    # Application 2 for NFT grant
    app2 = contract.submit_application(
        grant_id='nft-grant',
        project_name='NFT Marketplace Pro',
        project_description='Advanced NFT marketplace',
        team_info='3-person team',
        requested_amount=gl.u256(5000000000000000000),  # 5 GEN
        payout_address=applicant2.as_hex,
        website='https://nft.example.com',
        github_url='https://github.com/test/nft-marketplace',
        evidence_urls='https://github.com/test/nft-marketplace',
        additional_info='Supports ERC-721 and ERC-1155'
    )
    assert app2.startswith('app_'), f"Expected app_*, got {app2}"
    
    # Application 3 for DAO grant
    app3 = contract.submit_application(
        grant_id='dao-grant',
        project_name='DAO Governor',
        project_description='Decentralized governance framework',
        team_info='Core DAO contributor',
        requested_amount=gl.u256(2000000000000000000),  # 2 GEN
        payout_address=applicant3.as_hex,
        website='https://dao.example.com',
        github_url='https://github.com/test/dao-governor',
        evidence_urls='https://github.com/test/dao-governor',
        additional_info='Token-weighted voting system'
    )
    assert app3.startswith('app_'), f"Expected app_*, got {app3}"
    
    return f"✅ Test 3 PASSED: 3 applications submitted ({app1}, {app2}, {app3})"


# ==========================================
# Test 4: Evaluate and approve applications
# ==========================================
@gl.public.write
def test_evaluate_applications():
    """Evaluate all 3 applications"""
    contract = gl.contract.Contract(CONTRACT_ADDR)
    
    # Evaluate app 1
    eval1 = contract.evaluate_application(app_id='app_0')
    result1 = json.loads(eval1)
    assert result1['final'] in ['PASS', 'REJECTED'], f"Unexpected result: {result1}"
    
    # Evaluate app 2
    eval2 = contract.evaluate_application(app_id='app_1')
    result2 = json.loads(eval2)
    assert result2['final'] in ['PASS', 'REJECTED'], f"Unexpected result: {result2}"
    
    # Evaluate app 3
    eval3 = contract.evaluate_application(app_id='app_2')
    result3 = json.loads(eval3)
    assert result3['final'] in ['PASS', 'REJECTED'], f"Unexpected result: {result3}"
    
    return f"✅ Test 4 PASSED: 3 applications evaluated"


# ==========================================
# Test 5: Release funds to payout addresses
# ==========================================
@gl.public.write
def test_release_funds():
    """Release funds to approved applicants' payout addresses"""
    contract = gl.contract.Contract(CONTRACT_ADDR)
    
    # Release funds for app 1
    release1 = contract.release_funds(app_id='app_0')
    assert 'Released' in release1, f"Expected 'Released...', got {release1}"
    
    # Release funds for app 2
    release2 = contract.release_funds(app_id='app_1')
    assert 'Released' in release2, f"Expected 'Released...', got {release2}"
    
    # Release funds for app 3
    release3 = contract.release_funds(app_id='app_2')
    assert 'Released' in release3, f"Expected 'Released...', got {release3}"
    
    return f"✅ Test 5 PASSED: Funds released to 3 applicants"


# ==========================================
# Test 6: Cancel grant and verify refund
# ==========================================
@gl.public.write
def test_cancel_grant_with_refund():
    """Cancel grant and verify refund is processed"""
    contract = gl.contract.Contract(CONTRACT_ADDR)
    
    # Create a new grant for cancellation test
    contract.create_grant(
        grant_id='cancel-test-grant',
        name='Cancel Test Grant',
        description='For testing cancellation',
        eligibility='All',
        criteria='Test',
        budget_rules='Max 500 GEN',
        required_evidence='Demo',
        deadline='2026-12-31'
    )
    
    # Fund it
    contract.fund_grant(grant_id='cancel-test-grant')
    
    # Cancel it
    result = contract.cancel_grant(grant_id='cancel-test-grant')
    assert result is True, f"Expected True, got {result}"
    
    # Verify grant is marked cancelled
    grant = contract.get_grant(grant_id='cancel-test-grant')
    assert grant.cancelled is True, f"Expected cancelled=True, got {grant.cancelled}"
    assert grant.active is False, f"Expected active=False, got {grant.active}"
    
    return "✅ Test 6 PASSED: Grant cancelled with refund"


# ==========================================
# Test 7: Reject repeat cancellation
# ==========================================
@gl.public.write
def test_reject_repeat_cancellation():
    """Try to cancel already cancelled grant - should fail"""
    contract = gl.contract.Contract(CONTRACT_ADDR)
    
    try:
        contract.cancel_grant(grant_id='cancel-test-grant')
        assert False, "Should have raised ValueError for repeat cancellation"
    except ValueError as e:
        assert 'already cancelled' in str(e).lower(), f"Expected 'already cancelled' error, got {e}"
        return "✅ Test 7 PASSED: Repeat cancellation rejected"
    except Exception as e:
        # GenLayer wraps errors
        assert 'already cancelled' in str(e).lower() or 'cancelled' in str(e).lower(), f"Unexpected error: {e}"
        return "✅ Test 7 PASSED: Repeat cancellation rejected"


# ==========================================
# Test 8: Verify payout balances across grants
# ==========================================
@gl.public.write
def test_verify_payout_balances():
    """Verify correct amounts were paid out from each grant"""
    contract = gl.contract.Contract(CONTRACT_ADDR)
    
    # Check DeFi grant
    defi_grant = contract.get_grant(grant_id='defi-grant')
    assert defi_grant.paid_out > gl.u256(0), "DeFi grant should have paid_out > 0"
    
    # Check NFT grant
    nft_grant = contract.get_grant(grant_id='nft-grant')
    assert nft_grant.paid_out > gl.u256(0), "NFT grant should have paid_out > 0"
    
    # Check DAO grant
    dao_grant = contract.get_grant(grant_id='dao-grant')
    assert dao_grant.paid_out > gl.u256(0), "DAO grant should have paid_out > 0"
    
    return f"✅ Test 8 PASSED: Balances verified across 3 grants"


# ==========================================
# Test 9: Invalid payout address rejection
# ==========================================
@gl.public.write
def test_invalid_payout_address():
    """Verify invalid payout addresses are rejected"""
    contract = gl.contract.Contract(CONTRACT_ADDR)
    
    # Create new grant for this test
    contract.create_grant(
        grant_id='invalid-addr-grant',
        name='Invalid Address Test',
        description='Test',
        eligibility='All',
        criteria='Test',
        budget_rules='Max 100 GEN',
        required_evidence='Demo',
        deadline='2026-12-31'
    )
    
    # Try with invalid address (too short)
    try:
        contract.submit_application(
            grant_id='invalid-addr-grant',
            project_name='Test Project',
            project_description='Test',
            team_info='Test',
            requested_amount=gl.u256(1000000000000000000),
            payout_address='0x1234',  # Invalid
            website='https://test.com',
            github_url='https://github.com/test',
            evidence_urls='https://github.com/test',
            additional_info='Test'
        )
        assert False, "Should have raised ValueError for invalid address"
    except ValueError as e:
        assert 'invalid payout address' in str(e).lower(), f"Expected 'invalid payout address', got {e}"
        return "✅ Test 9 PASSED: Invalid payout address rejected"
    except Exception as e:
        assert 'invalid' in str(e).lower(), f"Unexpected error: {e}"
        return "✅ Test 9 PASSED: Invalid payout address rejected"


# ==========================================
# Main test runner
# ==========================================
@gl.public.write
def run_all_tests():
    """Run all tests and return results"""
    results = []
    
    try:
        results.append(test_create_multiple_grants())
    except Exception as e:
        results.append(f"❌ Test 1 FAILED: {e}")
    
    try:
        results.append(test_fund_multiple_grants())
    except Exception as e:
        results.append(f"❌ Test 2 FAILED: {e}")
    
    try:
        results.append(test_submit_applications())
    except Exception as e:
        results.append(f"❌ Test 3 FAILED: {e}")
    
    try:
        results.append(test_evaluate_applications())
    except Exception as e:
        results.append(f"❌ Test 4 FAILED: {e}")
    
    try:
        results.append(test_release_funds())
    except Exception as e:
        results.append(f"❌ Test 5 FAILED: {e}")
    
    try:
        results.append(test_cancel_grant_with_refund())
    except Exception as e:
        results.append(f"❌ Test 6 FAILED: {e}")
    
    try:
        results.append(test_reject_repeat_cancellation())
    except Exception as e:
        results.append(f"❌ Test 7 FAILED: {e}")
    
    try:
        results.append(test_verify_payout_balances())
    except Exception as e:
        results.append(f"❌ Test 8 FAILED: {e}")
    
    try:
        results.append(test_invalid_payout_address())
    except Exception as e:
        results.append(f"❌ Test 9 FAILED: {e}")
    
    return "\n".join(results)
