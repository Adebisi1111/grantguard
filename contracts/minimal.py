# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *


class Minimal(gl.Contract):
    text: str = "default"

    def __init__(self):
        pass

    @gl.public.write
    def set(self, val: str):
        self.text = val

    @gl.public.view
    def get(self) -> str:
        return self.text
