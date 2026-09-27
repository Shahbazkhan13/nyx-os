"""nikto adapter — web server scanner."""
import subprocess, re
from nx_platform.tool_adapters.base import ToolAdapter


class NiktoAdapter(ToolAdapter):
    name = "nikto"
    category = "web"
    binary = "nikto"

    def run(self, target, options=None):
        url = target if target.startswith("http") else f"http://{target}"
        try:
            out = subprocess.run(
                ["nikto", "-h", url, "-maxtime", "60s", "-nointeractive"],
                capture_output=True, text=True, timeout=120,
            )
            return {"stdout": out.stdout, "parsed": self.parse(out.stdout)}
        except FileNotFoundError:
            return {"error": "nikto not installed", "parsed": {"items": []}}
        except subprocess.TimeoutExpired:
            return {"error": "timeout", "parsed": {"items": []}}

    def parse(self, raw):
        items = []
        for line in raw.splitlines():
            if line.startswith("+ "):
                items.append(line[2:].strip())
        return {"items": items}
