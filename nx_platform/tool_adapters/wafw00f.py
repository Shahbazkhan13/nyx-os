"""wafw00f — WAF detection."""
import subprocess
from nx_platform.tool_adapters.base import ToolAdapter

class WafW00fAdapter(ToolAdapter):
    name = "wafw00f"
    category = "web"
    binary = "wafw00f"
    def run(self, target, options=None):
        url = target if target.startswith("http") else f"https://{target}"
        try:
            out = subprocess.run(
                ["wafw00f", url, "-a"],
                capture_output=True, text=True, timeout=120)
            return {"stdout": out.stdout, "parsed": self.parse(out.stdout)}
        except FileNotFoundError:
            return {"error": "wafw00f not installed", "parsed": {}}
        except Exception as e:
            return {"error": str(e), "parsed": {}}
    def parse(self, raw):
        waf = None
        for line in raw.splitlines():
            if "is behind" in line:
                parts = line.split("is behind")
                if len(parts) > 1: waf = parts[1].strip()
        return {"waf": waf, "detected": waf is not None}
