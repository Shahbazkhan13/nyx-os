"""enum4linux — SMB/Windows enumeration."""
import subprocess
from nx_platform.tool_adapters.base import ToolAdapter

class Enum4LinuxAdapter(ToolAdapter):
    name = "enum4linux"
    category = "active_directory"
    binary = "enum4linux"
    def run(self, target, options=None):
        try:
            out = subprocess.run(
                ["enum4linux", "-a", target],
                capture_output=True, text=True, timeout=600)
            return {"stdout": out.stdout[:10000], "parsed": self.parse(out.stdout)}
        except FileNotFoundError:
            return {"error": "enum4linux not installed", "parsed": {}}
        except Exception as e:
            return {"error": str(e), "parsed": {}}
    def parse(self, raw):
        info = {"shares": [], "users": [], "os": None, "domain": None}
        for line in raw.splitlines():
            if "Sharename" in line:
                info["shares"].append(line.strip())
            if "user:[" in line.lower():
                info["users"].append(line.strip())
            if "OS:" in line:
                info["os"] = line.strip()
            if "Domain:" in line:
                info["domain"] = line.strip()
        return info
