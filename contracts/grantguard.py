# v0.3.0
# { "Depends": "py-genlayer:5jycge4q8k23462jtb0b9fyey1s9qz928sz2nbrd9mg4sxqg2qng" }

import json
from dataclasses import dataclass
import genlayer as gl
from genlayer.storage import allow as allow_storage


@allow_storage
@dataclass
class Grant:
    id: str
    name: str
    description: str
    eligibility: str
    criteria: str
    budget_rules: str
    required_evidence: str
    deadline: str
    creator: str
    active: bool
    funded_amount: gl.u256
    paid_out: gl.u256


@allow_storage
@dataclass
class Application:
    id: str
    grant_id: str
    project_name: str
    project_description: str
    team_info: str
    requested_amount: gl.u256
    website: str
    github_url: str
    evidence_urls: str
    additional_info: str
    status: str
    evaluation: str


class GrantGuard(gl.contract.Contract):
    grants: gl.storage.TreeMap[str, Grant]
    applications: gl.storage.TreeMap[str, Application]
    grant_counter: gl.u256
    app_counter: gl.u256

    def __init__(self):
        pass

    @gl.public.write
    def create_grant(
        self,
        grant_id: str,
        name: str,
        description: str,
        eligibility: str,
        criteria: str,
        budget_rules: str,
        required_evidence: str,
        deadline: str,
    ) -> str:
        if self.grants.get(grant_id) is not None:
            raise ValueError("Grant ID already exists")
        if not name or not description:
            raise ValueError("Name and description required")
        if not criteria:
            raise ValueError("Criteria required")

        grant = Grant(
            id=grant_id,
            name=name,
            description=description,
            eligibility=eligibility,
            criteria=criteria,
            budget_rules=budget_rules,
            required_evidence=required_evidence,
            deadline=deadline,
            creator=gl.message.sender_address.as_hex,
            active=True,
            funded_amount=gl.u256(0),
            paid_out=gl.u256(0),
        )
        self.grants[grant_id] = grant
        self.grant_counter += gl.u256(1)
        return grant_id

    @gl.public.write.payable
    def fund_grant(self, grant_id: str) -> str:
        grant = self.grants.get(grant_id)
        if grant is None:
            raise ValueError("Grant not found")
        if not grant.active:
            raise ValueError("Grant is not active")
        if gl.message.value <= gl.u256(0):
            raise ValueError("Must send GEN to fund grant")
        grant.funded_amount += gl.u256(gl.message.value)
        self.grants[grant_id] = grant
        return "Funded"

    @gl.public.write
    def submit_application(
        self,
        grant_id: str,
        project_name: str,
        project_description: str,
        team_info: str,
        requested_amount: gl.u256,
        website: str,
        github_url: str,
        evidence_urls: str,
        additional_info: str,
    ) -> str:
        grant = self.grants.get(grant_id)
        if grant is None:
            raise ValueError("Grant not found")
        if not grant.active:
            raise ValueError("Grant is not active")
        if not project_name or not project_description:
            raise ValueError("Project name and description required")
        if requested_amount <= gl.u256(0):
            raise ValueError("Requested amount must be positive")
        if not evidence_urls:
            raise ValueError("Evidence URLs required")

        app_id = f"app_{int(self.app_counter)}"
        app = Application(
            id=app_id,
            grant_id=grant_id,
            project_name=project_name,
            project_description=project_description,
            team_info=team_info,
            requested_amount=requested_amount,
            website=website,
            github_url=github_url,
            evidence_urls=evidence_urls,
            additional_info=additional_info,
            status="SUBMITTED",
            evaluation="",
        )
        self.applications[app_id] = app
        self.app_counter += gl.u256(1)
        return app_id

    def _evaluate_application(self, app_id: str) -> dict:
        """Source-grounded evaluation using stored grant rules and verified evidence."""
        app = self.applications.get(app_id)
        if app is None:
            raise ValueError("Application not found")

        grant = self.grants.get(app.grant_id)
        if grant is None:
            raise ValueError("Grant not found")

        # Fetch evidence URLs on-chain
        evidence_urls = [u.strip() for u in app.evidence_urls.split(",") if u.strip()]
        evidence_content = []
        for url in evidence_urls[:5]:  # max 5 URLs to avoid timeout
            try:
                web_data = gl.nondet.web.render(url, mode="text")
                evidence_content.append(f"URL: {url}\nContent: {web_data[:2000]}")
            except Exception as e:
                evidence_content.append(f"URL: {url}\nError: {str(e)}")

        evidence_text = "\n\n".join(evidence_content)

        prompt = f"""You are evaluating a grant application. Use ONLY the stored grant criteria and the fetched evidence below.

=== GRANT CRITERIA (from contract storage) ===
Eligibility: {grant.eligibility}
Criteria: {grant.criteria}
Budget Rules: {grant.budget_rules}
Required Evidence: {grant.required_evidence}

=== APPLICATION ===
Project: {app.project_name}
Description: {app.project_description}
Team: {app.team_info}
Requested: {app.requested_amount} wei
Website: {app.website}
GitHub: {app.github_url}

=== FETCHED EVIDENCE ===
{evidence_text}

=== INSTRUCTIONS ===
1. Check eligibility: Does the applicant meet the stored eligibility requirements?
2. Check criteria: Does the project meet the stored criteria?
3. Check budget: Is the requested amount within budget rules?
4. Check evidence: Does the fetched evidence support the application claims?
5. If any check fails, final must be FAIL with reasons.
6. Respond as JSON: {{"eligibility":"PASS","criteria":"PASS","budget":"PASS","evidence":"PASS","final":"PASS","reasons":[]}}
"""

        try:
            res = gl.nondet.exec_prompt(prompt, response_format="json")
            return {
                "eligibility": str(res.get("eligibility", "REVIEW")).upper(),
                "criteria": str(res.get("criteria", "REVIEW")).upper(),
                "budget": str(res.get("budget", "REVIEW")).upper(),
                "evidence": str(res.get("evidence", "REVIEW")).upper(),
                "final": str(res.get("final", "REVIEW")).upper(),
                "reasons": res.get("reasons", []),
            }
        except Exception as e:
            return {
                "eligibility": "FAIL",
                "criteria": "FAIL",
                "budget": "FAIL",
                "evidence": "FAIL",
                "final": "FAIL",
                "reasons": [f"Evaluation error: {str(e)}"],
            }

    @gl.public.write
    def evaluate_application(self, app_id: str) -> str:
        """Evaluate using consensus — all validators fetch evidence and check grant rules."""
        app = self.applications.get(app_id)
        if app is None:
            raise ValueError("Application not found")
        if app.status == "EVALUATED":
            raise ValueError("Already evaluated")

        principle = (
            "All validators must agree the application meets the stored grant criteria "
            "and the fetched evidence supports the claims."
        )

        try:
            evaluation = gl.eq_principle.prompt_comparative(
                lambda: self._evaluate_application(app_id),
                principle,
            )
            result = {
                "eligibility": str(evaluation.get("eligibility", "REVIEW")).upper(),
                "criteria": str(evaluation.get("criteria", "REVIEW")).upper(),
                "budget": str(evaluation.get("budget", "REVIEW")).upper(),
                "evidence": str(evaluation.get("evidence", "REVIEW")).upper(),
                "final": str(evaluation.get("final", "REVIEW")).upper(),
                "reasons": evaluation.get("reasons", []),
            }
        except Exception as e:
            result = {
                "eligibility": "FAIL",
                "criteria": "FAIL",
                "budget": "FAIL",
                "evidence": "FAIL",
                "final": "FAIL",
                "reasons": [f"Consensus failed: {str(e)}"],
            }

        app = self.applications.get(app_id)
        app.evaluation = json.dumps(result)
        if result["final"] == "PASS":
            app.status = "APPROVED"
        else:
            app.status = "REJECTED"
        self.applications[app_id] = app

        return json.dumps(result)

    @gl.public.write
    def release_funds(self, app_id: str) -> str:
        """Release escrow funds to approved applicant."""
        app = self.applications.get(app_id)
        if app is None:
            raise ValueError("Application not found")
        if app.status != "APPROVED":
            raise ValueError("Application not approved")

        grant = self.grants.get(app.grant_id)
        if grant is None:
            raise ValueError("Grant not found")

        remaining = grant.funded_amount - grant.paid_out
        if remaining <= gl.u256(0):
            raise ValueError("No funds remaining in grant")

        amount = app.requested_amount
        if amount > remaining:
            amount = remaining

        grant.paid_out += amount
        self.grants[grant.id] = grant

        app.status = "PAID"
        self.applications[app_id] = app

        # Transfer funds
        recipient = gl.Address(app.project_name)  # placeholder — actual recipient should be stored
        gl.pay(recipient, amount)

        return f"Released {amount} wei"

    @gl.public.write
    def cancel_grant(self, grant_id: str) -> bool:
        """Cancel grant and refund creator."""
        grant = self.grants.get(grant_id)
        if grant is None:
            raise ValueError("Grant not found")
        if grant.creator != gl.message.sender_address.as_hex:
            raise ValueError("Only creator can cancel")
        if grant.paid_out > gl.u256(0):
            raise ValueError("Cannot cancel — funds already paid out")

        grant.active = False
        self.grants[grant_id] = grant

        # Refund remaining escrow to creator
        remaining = grant.funded_amount - grant.paid_out
        if remaining > gl.u256(0):
            creator = gl.Address(grant.creator)
            gl.pay(creator, remaining)

        return True

    @gl.public.view
    def get_grant(self, grant_id: str) -> Grant:
        return self.grants.get(grant_id)

    @gl.public.view
    def get_application(self, app_id: str) -> Application:
        return self.applications.get(app_id)

    @gl.public.view
    def get_stats(self) -> dict:
        return {
            "total_grants": self.grant_counter,
            "total_applications": self.app_counter,
        }
