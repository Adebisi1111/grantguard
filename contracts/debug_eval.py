# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json
from genlayer import *


class GrantEval(gl.Contract):
    """Test evaluation with eq_principle"""
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

        def evaluate() -> dict:
            prompt = f"Evaluate: {app['project_name']}. Respond as JSON: {{\"score\": 1-10, \"reasoning\": \"explanation\"}}"
            try:
                res = gl.nondet.exec_prompt(prompt, response_format="json")
                return res
            except Exception as e:
                return {"error": str(e)}

        principle = "Evaluate honestly based on the criteria."

        try:
            result = gl.eq_principle.prompt_comparative(evaluate, principle)
            app["status"] = "EVALUATED"
            app["evaluation"] = result
            self.applications[app_id] = json.dumps(app)
            return json.dumps(result)
        except gl.vm.UserError as e:
            app["status"] = "FAILED_TO_EVALUATE"
            self.applications[app_id] = json.dumps(app)
            raise gl.vm.UserError("Evaluation failed: " + str(e))

    @gl.public.view
    def getApplication(self, app_id: u256) -> str:
        a = self.applications.get(app_id, None)
        if a is None:
            return json.dumps({"error": "not found"})
        return a

    @gl.public.view
    def getNextAppId(self) -> str:
        return str(int(self.next_app_id))