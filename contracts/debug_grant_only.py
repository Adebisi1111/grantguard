# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json
from genlayer import *


class GrantOnly(gl.Contract):
    """Test with only grants, no applications"""
    grants: TreeMap[u256, str]
    next_grant_id: u256 = u256(0)

    def __init__(self):
        pass

    @gl.public.write
    def createGrant(self, name: str, description: str, eligibility: str, criteria: str, budget_rules: str, required_evidence: str, deadline: str) -> u256:
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

    @gl.public.view
    def getNextGrantId(self) -> str:
        return str(int(self.next_grant_id))