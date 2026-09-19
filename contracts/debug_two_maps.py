# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json
from genlayer import *


class TwoMaps(gl.Contract):
    """Test two TreeMaps"""
    grants: TreeMap[u256, str]
    applications: TreeMap[u256, str]
    next_grant_id: u256 = u256(0)
    next_app_id: u256 = u256(0)

    def __init__(self):
        pass

    @gl.public.write
    def createGrant(self, name: str) -> u256:
        grant_id = self.next_grant_id
        self.next_grant_id += u256(1)
        self.grants[grant_id] = name
        return grant_id

    @gl.public.view
    def getGrant(self, grant_id: u256) -> str:
        g = self.grants.get(grant_id, None)
        if g is None:
            return "not found"
        return g

    @gl.public.view
    def getNextGrantId(self) -> str:
        return str(int(self.next_grant_id))