"""dnsrecon — DNS enumeration."""
import subprocess
from nx_platform.tool_adapters.base import ToolAdapter

class DnsReconAdapter(ToolAdapter):
    name = "dnsrecon"
    category = "recon"
    binary = "dnsrecon"
    def run(self, target, options=None):
        try:
            out = subprocess.run(
                ["dnsrecon", "-d", target, "-t", "std"],
                capture_output=True, text=True, timeout=120)
            return {"stdout": out.stdout, "parsed": self.parse(out.stdout)}
        except FileNotFoundError:
            return {"error": "dnsrecon not installed", "parsed": {}}
        except Exception as e:
            return {"error": str(e), "parsed": {}}
    def parse(self, raw):
        records = []
        for line in raw.splitlines():
            if "[+]" in line or "A " in line or "MX " in line:
                records.append(line.strip())
        return {"records": records[:100]}
