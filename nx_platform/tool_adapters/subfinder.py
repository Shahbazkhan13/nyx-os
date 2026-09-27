"""subfinder — subdomain discovery."""
import subprocess
from nx_platform.tool_adapters.base import ToolAdapter


class SubfinderAdapter(ToolAdapter):
    name = "subfinder"
    category = "recon"
    binary = "subfinder"

    def run(self, target, options=None):
        try:
            out = subprocess.run(["subfinder", "-d", target, "-silent"],
                                 capture_output=True, text=True, timeout=120)
            return {"stdout": out.stdout, "parsed": self.parse(out.stdout)}
        except FileNotFoundError:
            return {"error": "subfinder not installed",
                    "parsed": {"subdomains": []}}
        except Exception as e:
            return {"error": str(e), "parsed": {"subdomains": []}}

    def parse(self, raw):
        return {"subdomains": [l.strip() for l in raw.splitlines() if l.strip()]}
