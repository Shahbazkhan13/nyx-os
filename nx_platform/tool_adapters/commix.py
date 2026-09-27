"""commix — command injection exploiter."""
import subprocess
from nx_platform.tool_adapters.base import ToolAdapter

class CommixAdapter(ToolAdapter):
    name = "commix"
    category = "web"
    binary = "commix"
    def run(self, target, options=None):
        url = target if target.startswith("http") else f"http://{target}"
        try:
            out = subprocess.run(
                ["commix", "--url", url, "--batch", "--level=1"],
                capture_output=True, text=True, timeout=600)
            return {"stdout": out.stdout[-5000:], "parsed": self.parse(out.stdout)}
        except FileNotFoundError:
            return {"error": "commix not installed", "parsed": {"vulnerable": False}}
        except Exception as e:
            return {"error": str(e), "parsed": {"vulnerable": False}}
    def parse(self, raw):
        return {"vulnerable": "is vulnerable" in raw.lower()}
