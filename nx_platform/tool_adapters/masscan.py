"""masscan — high-speed port scanner."""
import subprocess, re
from nx_platform.tool_adapters.base import ToolAdapter

class MasscanAdapter(ToolAdapter):
    name = "masscan"
    category = "network"
    binary = "masscan"
    def run(self, target, options=None):
        rate = (options or {}).get("rate", 1000)
        ports = (options or {}).get("ports", "1-1000")
        try:
            out = subprocess.run(
                ["masscan", target, "-p", ports, "--rate", str(rate)],
                capture_output=True, text=True, timeout=300)
            return {"stdout": out.stdout, "parsed": self.parse(out.stdout)}
        except FileNotFoundError:
            return {"error": "masscan not installed", "parsed": {"ports": []}}
        except Exception as e:
            return {"error": str(e), "parsed": {"ports": []}}
    def parse(self, raw):
        ports = []
        for line in raw.splitlines():
            if "open" in line and "port" in line:
                ports.append(line.strip())
        return {"ports": ports}
