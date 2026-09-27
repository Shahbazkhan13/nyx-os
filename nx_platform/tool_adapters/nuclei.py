"""nuclei — vulnerability scanner."""
import subprocess
from nx_platform.tool_adapters.base import ToolAdapter


class NucleiAdapter(ToolAdapter):
    name = "nuclei"
    category = "vulnerability"
    binary = "nuclei"

    def run(self, target, options=None):
        url = target if target.startswith("http") else f"https://{target}"
        try:
            out = subprocess.run(
                ["nuclei", "-u", url, "-silent", "-severity", "medium,high,critical",
                 "-timeout", "5", "-retries", "1"],
                capture_output=True, text=True, timeout=600)
            return {"stdout": out.stdout, "parsed": self.parse(out.stdout)}
        except FileNotFoundError:
            return {"error": "nuclei not installed", "parsed": {"findings": []}}
        except Exception as e:
            return {"error": str(e), "parsed": {"findings": []}}

    def parse(self, raw):
        findings = []
        for line in raw.splitlines():
            if "[" in line and "]" in line:
                findings.append({"raw": line.strip()})
        return {"findings": findings}
