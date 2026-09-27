"""macchanger adapter."""
import subprocess
from nx_platform.tool_adapters.base import ToolAdapter


class MacchangerAdapter(ToolAdapter):
    name = "macchanger"
    category = "wireless"
    binary = "macchanger"

    def run(self, target, options=None):
        """target = interface name"""
        try:
            out = subprocess.run(
                ["macchanger", "-s", target],
                capture_output=True, text=True, timeout=10,
            )
            return {"stdout": out.stdout, "parsed": self.parse(out.stdout)}
        except Exception as e:
            return {"error": str(e), "parsed": {}}

    def parse(self, raw):
        info = {}
        for line in raw.splitlines():
            if "Current MAC" in line:
                info["current"] = line.split(":", 1)[-1].strip()
            elif "Permanent MAC" in line:
                info["permanent"] = line.split(":", 1)[-1].strip()
        return info
