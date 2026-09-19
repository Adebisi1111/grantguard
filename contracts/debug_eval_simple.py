# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json
from genlayer import *


class GrantEvalSimple(gl.Contract):
    """Test evaluation WITHOUT eq_principle"""
    applications: TreeMap[u256, str]
    next_app_id: u256 = u256(0)

    def __init__(self):
        pass

    @gl.public.write
    def submitApplication(self, project_name: str) -> u256:
        app_id = self.next_app_id
        self.next_app_id += u256(1)
        self.applications[app_id] = json.dumps({
            "id": int(app_id),
            "project_name": project_name,
            "status": "SUBMITTED"
        })
        return app_id

    @gl.public.write
    def evaluateApplication(self, app_id: u256) -> str:
        app_raw = self.applications.get(app_id, None)
        if app_raw is None:
            raise gl.vm.UserError("Application not found")

        app = json.loads(app_raw)
        app["status"] = "EVALUATED"
        app["evaluation"] = {"final": "PASS", "reasons": ["Test evaluation"]}
        self.applications[app_id] = json.dumps(app)
        return json.dumps(app["evaluation"])

    @gl.public.view
    def getApplication(self, app_id: u256) -> str:
        a = self.applications.get(app_id, None)
        if a is None:
            return json.dumps({"error": "not found"})
        return a

    @gl.public.view
    def getNextAppId(self) -> str:
        return str(int(self.next_app_id))