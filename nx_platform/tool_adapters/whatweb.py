"""whatweb — web tech fingerprint."""
import subprocess
from nx_platform.tool_adapters.base import ToolAdapter


class WhatWebAdapter(ToolAdapter):
    name = "whatweb"
    category = "web"
    binary = "whatweb"

    def run(self, target, options=None):
        url = target if target.startswith("http") else f"http://{target}"
        try:
            out = subprocess.run(["whatweb", url, "--no-errors", "-q"],
                                 capture_output=True, text=True, timeout=60)
            return {"stdout": out.stdout, "parsed": self.parse(out.stdout)}
        except FileNotFoundError:
            return {"error": "whatweb not installed", "parsed": {"tech": []}}
        except Exception as e:
            return {"error": str(e), "parsed": {"tech": []}}

    def parse(self, raw):
        # whatweb output: URL [status] TECH1, TECH2, ...
        tech = []
        for line in raw.splitlines():
            if "[" in line and "]" in line:
                inner = line[line.find("[")+1:line.find("]")]
                tech.extend([t.strip() for t in inner.split(",") if t.strip()])
        return {"tech": tech}
