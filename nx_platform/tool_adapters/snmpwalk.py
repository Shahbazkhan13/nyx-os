"""snmpwalk — SNMP enumeration."""
import subprocess
from nx_platform.tool_adapters.base import ToolAdapter

class SnmpwalkAdapter(ToolAdapter):
    name = "snmpwalk"
    category = "network"
    binary = "snmpwalk"
    def run(self, target, options=None):
        community = (options or {}).get("community", "public")
        try:
            out = subprocess.run(
                ["snmpwalk", "-c", community, "-v", "2c", target],
                capture_output=True, text=True, timeout=120)
            return {"stdout": out.stdout[:5000], "parsed": self.parse(out.stdout)}
        except FileNotFoundError:
            return {"error": "snmpwalk not installed", "parsed": {"entries": []}}
        except Exception as e:
            return {"error": str(e), "parsed": {"entries": []}}
    def parse(self, raw):
        return {"entries": [l.strip() for l in raw.splitlines()[:100]]}
