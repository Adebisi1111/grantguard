import pytest
import json
from genlayer import *


@pytest.fixture
def contract(direct_deploy):
    return direct_deploy("contracts/grantguard.py")


def test_create_grant(direct_vm, contract):
    """Test grant creation."""
    grant_id = contract.create_grant(
        "Test Grant",
        "A test grant",
        "Open to all",
        "Technical merit",
        "Max 10000 GEN",
        "GitHub repo",
        "2026-12-31"
    )
    assert grant_id == 0

    grant_raw = contract.get_grant(0)
    grant = json.loads(grant_raw)
    assert grant["name"] == "Test Grant"
    assert grant["active"] == True


def test_get_all_grants(direct_vm, contract):
    """Test getting all grants."""
    contract.create_grant("Grant 1", "Desc 1", "All", "Criteria", "Budget", "Evidence", "2026-12-31")
    contract.create_grant("Grant 2", "Desc 2", "All", "Criteria", "Budget", "Evidence", "2026-12-31")

    grants_raw = contract.get_all_grants()
    grants = json.loads(grants_raw)
    assert len(grants) == 2


def test_submit_application(direct_vm, contract):
    """Test valid application submission."""
    grant_id = contract.create_grant("Test Grant", "Desc", "All", "Criteria", "Budget", "Evidence", "2026-12-31")

    app_id = contract.submit_application(
        grant_id,
        "My Project",
        "A great project",
        "Team of 5",
        "5000 GEN",
        "https://myproject.com",
        "https://github.com/myproject",
        "https://evidence1.com, https://evidence2.com",
        "Additional info"
    )
    assert app_id == 0

    app_raw = contract.get_application(0)
    app = json.loads(app_raw)
    assert app["project_name"] == "My Project"
    assert app["status"] == "SUBMITTED"


def test_submit_application_invalid_grant(direct_vm, contract):
    """Test submission to non-existent grant."""
    with pytest.raises(Exception):
        contract.submit_application(
            999,
            "My Project",
            "Desc",
            "Team",
            "5000 GEN",
            "https://site.com",
            "https://github.com/repo",
            "",
            ""
        )


def test_submit_application_missing_fields(direct_vm, contract):
    """Test submission with missing required fields."""
    grant_id = contract.create_grant("Test Grant", "Desc", "All", "Criteria", "Budget", "Evidence", "2026-12-31")

    with pytest.raises(Exception):
        contract.submit_application(
            grant_id,
            "",  # missing project name
            "Desc",
            "Team",
            "5000 GEN",
            "https://site.com",
            "https://github.com/repo",
            "",
            ""
        )


def test_submit_application_invalid_url(direct_vm, contract):
    """Test submission with invalid URL format."""
    grant_id = contract.create_grant("Test Grant", "Desc", "All", "Criteria", "Budget", "Evidence", "2026-12-31")

    with pytest.raises(Exception):
        contract.submit_application(
            grant_id,
            "Project",
            "Desc",
            "Team",
            "5000 GEN",
            "not-a-url",  # invalid
            "https://github.com/repo",
            "",
            ""
        )


def test_get_applications_for_grant(direct_vm, contract):
    """Test getting all applications for a grant."""
    grant_id = contract.create_grant("Test Grant", "Desc", "All", "Criteria", "Budget", "Evidence", "2026-12-31")

    contract.submit_application(grant_id, "Project 1", "Desc", "Team", "5000", "https://site.com", "https://github.com/repo", "", "")
    contract.submit_application(grant_id, "Project 2", "Desc", "Team", "3000", "https://site.com", "https://github.com/repo", "", "")

    apps_raw = contract.get_applications_for_grant(grant_id)
    apps = json.loads(apps_raw)
    assert len(apps) == 2


def test_evaluate_application_pass(direct_vm, contract):
    """Test PASS evaluation."""
    grant_id = contract.create_grant(
        "Test Grant",
        "A grant for testing",
        "Open to all applicants",
        "Technical feasibility and innovation",
        "Budget must be reasonable",
        "GitHub repository required",
        "2026-12-31"
    )

    app_id = contract.submit_application(
        grant_id,
        "Excellent Project",
        "A highly innovative project with strong technical foundation",
        "Experienced team of 10 developers",
        "5000 GEN",
        "https://excellent-project.com",
        "https://github.com/excellent-project",
        "https://github.com/excellent-project",
        "We have been building for 2 years"
    )

    # Mock the LLM response
    direct_vm.mock_llm(r".*", json.dumps({
        "eligibility": "PASS",
        "completeness": "PASS",
        "feasibility": "PASS",
        "budget": "PASS",
        "evidence": "PASS",
        "final": "PASS",
        "reasons": ["Strong application", "Clear technical details"],
        "evidence_used": ["https://github.com/excellent-project"],
        "evidence_unreachable": [],
        "conflicts": []
    }))

    result_raw = contract.evaluate_application(app_id)
    result = json.loads(result_raw)
    assert result["final"] == "PASS"

    # Verify status updated
    app_raw = contract.get_application(app_id)
    app = json.loads(app_raw)
    assert app["status"] == "EVALUATED"


def test_evaluate_application_fail(direct_vm, contract):
    """Test FAIL evaluation."""
    grant_id = contract.create_grant(
        "Test Grant",
        "A grant for testing",
        "Must be an established project",
        "Technical feasibility",
        "Budget must be reasonable",
        "GitHub repository required",
        "2026-12-31"
    )

    app_id = contract.submit_application(
        grant_id,
        "Bad Project",
        "A project with no details",
        "No team info",
        "100000 GEN",
        "",
        "",
        "",
        ""
    )

    direct_vm.mock_lln(r".*", json.dumps({
        "eligibility": "FAIL",
        "completeness": "FAIL",
        "feasibility": "FAIL",
        "budget": "FAIL",
        "evidence": "FAIL",
        "final": "FAIL",
        "reasons": ["No evidence provided", "Unrealistic budget", "No team information"],
        "evidence_used": [],
        "evidence_unreachable": [],
        "conflicts": []
    }))

    result_raw = contract.evaluate_application(app_id)
    result = json.loads(result_raw)
    assert result["final"] == "FAIL"


def test_evaluate_application_insufficient_evidence(direct_vm, contract):
    """Test INSUFFICIENT_EVIDENCE evaluation."""
    grant_id = contract.create_grant(
        "Test Grant",
        "A grant for testing",
        "Open to all",
        "Technical feasibility",
        "Budget must be reasonable",
        "GitHub repository required",
        "2026-12-31"
    )

    app_id = contract.submit_application(
        grant_id,
        "Vague Project",
        "A project with minimal details",
        "Small team",
        "5000 GEN",
        "",
        "",
        "",
        ""
    )

    direct_vm.mock_lln(r".*", json.dumps({
        "eligibility": "INSUFFICIENT_EVIDENCE",
        "completeness": "INSUFFICIENT_EVIDENCE",
        "feasibility": "INSUFFICIENT_EVIDENCE",
        "budget": "REVIEW",
        "evidence": "INSUFFICIENT_EVIDENCE",
        "final": "INSUFFICIENT_EVIDENCE",
        "reasons": ["Not enough information to evaluate", "No evidence URLs provided"],
        "evidence_used": [],
        "evidence_unreachable": [],
        "conflicts": []
    }))

    result_raw = contract.evaluate_application(app_id)
    result = json.loads(result_raw)
    assert result["final"] == "INSUFFICIENT_EVIDENCE"


def test_evaluate_application_review(direct_vm, contract):
    """Test REVIEW evaluation."""
    grant_id = contract.create_grant(
        "Test Grant",
        "A grant for testing",
        "Open to all",
        "Technical feasibility and innovation",
        "Budget must be reasonable",
        "GitHub repository required",
        "2026-12-31"
    )

    app_id = contract.submit_application(
        grant_id,
        "Interesting Project",
        "A project with some good ideas but unclear execution plan",
        "Small team",
        "8000 GEN",
        "https://project.com",
        "https://github.com/project",
        "https://github.com/project",
        "We need more time to complete"
    )

    direct_vm.mock_lln(r".*", json.dumps({
        "eligibility": "PASS",
        "completeness": "REVIEW",
        "feasibility": "REVIEW",
        "budget": "PASS",
        "evidence": "PASS",
        "final": "REVIEW",
        "reasons": ["Technical architecture needs clarification", "Timeline unclear"],
        "evidence_used": ["https://github.com/project"],
        "evidence_unreachable": [],
        "conflicts": []
    }))

    result_raw = contract.evaluate_application(app_id)
    result = json.loads(result_raw)
    assert result["final"] == "REVIEW"


def test_evaluate_nonexistent_application(direct_vm, contract):
    """Test evaluating non-existent application."""
    with pytest.raises(Exception):
        contract.evaluate_application(999)


def test_multiple_applications_no_mix(direct_vm, contract):
    """Test that multiple applications don't mix data."""
    grant_id = contract.create_grant("Test Grant", "Desc", "All", "Criteria", "Budget", "Evidence", "2026-12-31")

    app1_id = contract.submit_application(grant_id, "Project A", "Desc A", "Team A", "5000", "https://a.com", "https://github.com/a", "", "")
    app2_id = contract.submit_application(grant_id, "Project B", "Desc B", "Team B", "3000", "https://b.com", "https://github.com/b", "", "")

    app1_raw = contract.get_application(app1_id)
    app1 = json.loads(app1_raw)
    app2_raw = contract.get_application(app2_id)
    app2 = json.loads(app2_raw)

    assert app1["project_name"] == "Project A"
    assert app2["project_name"] == "Project B"
    assert app1["id"] != app2["id"]


def test_status_transitions(direct_vm, contract):
    """Test application status transitions."""
    grant_id = contract.create_grant("Test Grant", "Desc", "All", "Criteria", "Budget", "Evidence", "2026-12-31")
    app_id = contract.submit_application(grant_id, "Project", "Desc", "Team", "5000", "https://site.com", "https://github.com/repo", "", "")

    # Initially SUBMITTED
    app = json.loads(contract.get_application(app_id))
    assert app["status"] == "SUBMITTED"

    # Mock and evaluate
    direct_vm.mock_lln(r".*", json.dumps({
        "eligibility": "PASS",
        "completeness": "PASS",
        "feasibility": "PASS",
        "budget": "PASS",
        "evidence": "PASS",
        "final": "PASS",
        "reasons": ["Good"],
        "evidence_used": [],
        "evidence_unreachable": [],
        "conflicts": []
    }))

    contract.evaluate_application(app_id)

    # Now EVALUATED
    app = json.loads(contract.get_application(app_id))
    assert app["status"] == "EVALUATED"
    assert app["evaluation"] is not None
