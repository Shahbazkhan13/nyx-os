"""dig adapter — DNS lookups."""
import subprocess
from nx_platform.tool_adapters.base import ToolAdapter


class DigAdapter(ToolAdapter):
    name = "dig"
    category = "recon"
    binary = "dig"

    def run(self, target, options=None):
        record_type = (options or {}).get("type", "A")
        try:
            out = subprocess.run(
                [self.binary, "+short", record_type, target],
                capture_output=True, text=True, timeout=15,
            )
            return {"stdout": out.stdout, "parsed": self.parse(out.stdout)}
        except Exception as e:
            return {"error": str(e), "parsed": {"records": []}}

    def parse(self, raw):
        return {"records": [l for l in raw.strip().split("\n") if l]}
