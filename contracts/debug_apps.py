# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json
from genlayer import *


class GrantApps(gl.Contract):
    """Test applications TreeMap"""
    grants: TreeMap[u256, str]
    applications: TreeMap[u256, str]
    next_grant_id: u256 = u256(0)
    next_app_id: u256 = u256(0)

    def __init__(self):
        pass

    @gl.public.write
    def createGrant(self, name: str, description: str, eligibility: str, criteria: str, budget_rules: str, required_evidence: str, deadline: str) -> u256:
        grant_id = self.next_grant_id
        self.next_grant_id += u256(1)
        self.grants[grant_id] = json.dumps({"id": int(grant_id), "name": name, "active": True})
        return grant_id

    @gl.public.write
    def submitApplication(self, grant_id: u256, project_name: str, project_description: str, team_info: str, requested_amount: str, website: str, github_url: str, evidence_urls: str, additional_info: str) -> u256:
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
            "status": "SUBMITTED"
        })
        return app_id

    @gl.public.view
    def getApplication(self, app_id: u256) -> str:
        a = self.applications.get(app_id, None)
        if a is None:
            return json.dumps({"error": "not found"})
        return a

    @gl.public.view
    def getNextGrantId(self) -> str:
        return str(int(self.next_grant_id))

    @gl.public.view
    def getNextAppId(self) -> str:
        return str(int(self.next_app_id))