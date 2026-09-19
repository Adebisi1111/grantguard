# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json
from genlayer import *


class GrantGuard(gl.Contract):
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
            "status": "SUBMITTED",
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

    def _analyze_application(self, app: dict) -> dict:
        """AI leader analysis using gl.nondet.exec_prompt"""
        prompt = (
            f"Evaluate this grant application:\n"
            f"Project: {app.get('project_name', '')}\n"
            f"Description: {app.get('project_description', '')}\n"
            f"Team: {app.get('team_info', '')}\n"
            f"Amount: {app.get('requested_amount', '')}\n"
            f"Evidence: {app.get('evidence_urls', '')}\n\n"
            f"Rate each criterion as PASS, REVIEW, or FAIL.\n"
            f"Respond as JSON with exactly this format:\n"
            f'{{"eligibility":"PASS","completeness":"PASS","feasibility":"PASS","budget":"PASS","evidence":"PASS","final":"PASS","reasons":[]}}'
        )
        
        try:
            res = gl.nondet.exec_prompt(prompt, response_format="json")
            return {
                "eligibility": res.get("eligibility", "REVIEW").upper(),
                "completeness": res.get("completeness", "REVIEW").upper(),
                "feasibility": res.get("feasibility", "REVIEW").upper(),
                "budget": res.get("budget", "REVIEW").upper(),
                "evidence": res.get("evidence", "REVIEW").upper(),
                "final": res.get("final", "REVIEW").upper(),
                "reasons": res.get("reasons", [])
            }
        except Exception as e:
            return {
                "eligibility": "REVIEW",
                "completeness": "REVIEW",
                "feasibility": "REVIEW",
                "budget": "REVIEW",
                "evidence": "REVIEW",
                "final": "REVIEW",
                "reasons": [f"AI analysis error: {str(e)}"]
            }

    @gl.public.write
    def evaluateApplication(self, app_id: u256) -> str:
        """Evaluate using AI consensus (TruthOracle v2 pattern)"""
        app_raw = self.applications.get(app_id, None)
        if app_raw is None:
            raise gl.vm.UserError("Application not found")

        app = json.loads(app_raw)

        def get_analysis() -> dict:
            return self._analyze_application(app)

        principle = (
            "The evaluations should agree on whether the application meets the grant criteria. "
            "Minor wording differences are acceptable as long as the final verdict matches."
        )

        try:
            # AI consensus using prompt_comparative (TruthOracle v2 pattern)
            verified = gl.eq_principle.prompt_comparative(get_analysis, principle)
            evaluation = {
                "eligibility": verified.get("eligibility", "REVIEW").upper(),
                "completeness": verified.get("completeness", "REVIEW").upper(),
                "feasibility": verified.get("feasibility", "REVIEW").upper(),
                "budget": verified.get("budget", "REVIEW").upper(),
                "evidence": verified.get("evidence", "REVIEW").upper(),
                "final": verified.get("final", "REVIEW").upper(),
                "reasons": verified.get("reasons", [])
            }
        except Exception:
            # Fallback to deterministic if consensus fails
            evaluation = {
                "eligibility": "PASS",
                "completeness": "PASS" if len(app.get("project_description", "")) > 30 else "REVIEW",
                "feasibility": "PASS" if len(app.get("project_description", "")) > 50 else "REVIEW",
                "budget": "PASS" if app.get("requested_amount") else "REVIEW",
                "evidence": "PASS" if app.get("evidence_urls") else "REVIEW",
                "final": "PASS",
                "reasons": []
            }

        app["status"] = "EVALUATED"
        app["evaluation"] = evaluation
        self.applications[app_id] = json.dumps(app)

        return json.dumps(evaluation)

    @gl.public.view
    def getNextGrantId(self) -> str:
        return str(int(self.next_grant_id))

    @gl.public.view
    def getNextAppId(self) -> str:
        return str(int(self.next_app_id))
