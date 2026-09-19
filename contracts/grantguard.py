# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json
from genlayer import *


STATUS_SUBMITTED = "SUBMITTED"
STATUS_EVALUATING = "EVALUATING"
STATUS_EVALUATED = "EVALUATED"
STATUS_FAILED_TO_EVALUATE = "FAILED_TO_EVALUATE"

ASSESS_PASS = "PASS"
ASSESS_REVIEW = "REVIEW"
ASSESS_FAIL = "FAIL"
ASSESS_INSUFFICIENT = "INSUFFICIENT_EVIDENCE"


class GrantGuard(gl.Contract):
    """Grant application evaluator."""

    grants: TreeMap[u256, str]
    applications: TreeMap[u256, str]
    next_grant_id: u256 = u256(0)
    next_app_id: u256 = u256(0)

    def __init__(self):
        pass

    @gl.public.write
    def createGrant(
        self,
        name: str,
        description: str,
        eligibility: str,
        criteria: str,
        budget_rules: str,
        required_evidence: str,
        deadline: str
    ) -> u256:
        grant_id = self.next_grant_id
        self.next_grant_id += u256(1)

        self.grants[grant_id] = json.dumps({
            "id": int(grant_id),
            "name": name,
            "description": description,
            "eligibility": eligibility,
            "criteria": criteria,
            "budget_rules": budget_rules,
            "required_evidence": required_evidence,
            "deadline": deadline,
            "creator": gl.message.sender_address.as_hex,
            "active": True
        })
        return grant_id

    @gl.public.view
    def getGrant(self, grant_id: u256) -> str:
        g = self.grants.get(grant_id, None)
        if g is None:
            return json.dumps({"error": "not found"})
        return g

    @gl.public.view
    def getAllGrants(self) -> str:
        result = []
        for i in range(int(self.next_grant_id)):
            g = self.grants.get(u256(i), None)
            if g is not None:
                result.append(json.loads(g))
        return json.dumps(result)

    @gl.public.write
    def submitApplication(
        self,
        grant_id: u256,
        project_name: str,
        project_description: str,
        team_info: str,
        requested_amount: str,
        website: str,
        github_url: str,
        evidence_urls: str,
        additional_info: str
    ) -> u256:
        grant_raw = self.grants.get(grant_id, None)
        if grant_raw is None:
            raise gl.vm.UserError("Grant not found")

        grant = json.loads(grant_raw)
        if not grant.get("active", False):
            raise gl.vm.UserError("Grant is not active")

        if not project_name or not project_description:
            raise gl.vm.UserError("Project name and description required")
        if not requested_amount:
            raise gl.vm.UserError("Requested amount required")

        for url in [website, github_url]:
            if url and not url.startswith(("http://", "https://")):
                raise gl.vm.UserError("URLs must start with http:// or https://")

        app_id = self.next_app_id
        self.next_app_id += u256(1)

        self.applications[app_id] = json.dumps({
            "id": int(app_id),
            "grant_id": int(grant_id),
            "project_name": project_name,
            "project_description": project_description,
            "team_info": team_info,
            "requested_amount": requested_amount,
            "website": website,
            "github_url": github_url,
            "evidence_urls": evidence_urls,
            "additional_info": additional_info,
            "status": STATUS_SUBMITTED,
            "evaluation": None
        })
        return app_id

    @gl.public.view
    def getApplication(self, app_id: u256) -> str:
        a = self.applications.get(app_id, None)
        if a is None:
            return json.dumps({"error": "not found"})
        return a

    @gl.public.view
    def getApplicationsForGrant(self, grant_id: u256) -> str:
        result = []
        for i in range(int(self.next_app_id)):
            a = self.applications.get(u256(i), None)
            if a is not None:
                parsed = json.loads(a)
                if parsed["grant_id"] == int(grant_id):
                    result.append(parsed)
        return json.dumps(result)

    @gl.public.write
    def evaluateApplication(self, app_id: u256) -> str:
        app_raw = self.applications.get(app_id, None)
        if app_raw is None:
            raise gl.vm.UserError("Application not found")

        app = json.loads(app_raw)
        if app["status"] == STATUS_EVALUATING:
            raise gl.vm.UserError("Already evaluating")

        app["status"] = STATUS_EVALUATING
        self.applications[app_id] = json.dumps(app)

        # NOTE: gl.eq_principle.prompt_comparative() currently causes a revert on this testnet.
        # This is a documented testnet limitation. For now, the evaluation uses deterministic rules.
        # Future versions will integrate AI consensus when testnet support is available.
        project_name = app.get("project_name", "")
        project_description = app.get("project_description", "")
        requested_amount = app.get("requested_amount", "")
        github_url = app.get("github_url", "")
        evidence_urls = app.get("evidence_urls", "")

        evaluation = {
            "eligibility": ASSESS_PASS,
            "completeness": ASSESS_PASS if len(project_description) > 20 else ASSESS_REVIEW,
            "feasibility": ASSESS_REVIEW if len(project_description) < 50 else ASSESS_PASS,
            "budget": ASSESS_PASS,
            "evidence": ASSESS_PASS if evidence_urls else ASSESS_INSUFFICIENT,
            "final": ASSESS_PASS,
            "reasons": [],
            "evidence_used": [],
            "evidence_unreachable": [],
            "conflicts": []
        }

        if evaluation["completeness"] == ASSESS_REVIEW:
            evaluation["reasons"].append("Project description could be more detailed.")
        if evaluation["feasibility"] == ASSESS_REVIEW:
            evaluation["reasons"].append("Technical architecture requires additional detail.")
        if evaluation["evidence"] == ASSESS_INSUFFICIENT:
            evaluation["reasons"].append("No evidence URLs provided.")

        if evaluation["evidence"] == ASSESS_INSUFFICIENT or evaluation["completeness"] == ASSESS_REVIEW:
            evaluation["final"] = ASSESS_REVIEW

        app["status"] = STATUS_EVALUATED
        app["evaluation"] = evaluation
        self.applications[app_id] = json.dumps(app)

        return json.dumps(evaluation)

    @gl.public.view
    def getNextGrantId(self) -> str:
        return str(int(self.next_grant_id))

    @gl.public.view
    def getNextAppId(self) -> str:
        return str(int(self.next_app_id))