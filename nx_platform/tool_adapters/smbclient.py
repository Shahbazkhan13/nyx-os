"""smbclient — SMB shares listing."""
import subprocess
from nx_platform.tool_adapters.base import ToolAdapter

class SMBClientAdapter(ToolAdapter):
    name = "smbclient"
    category = "network"
    binary = "smbclient"
    def run(self, target, options=None):
        try:
            out = subprocess.run(
                ["smbclient", "-L", target, "-N"],
                capture_output=True, text=True, timeout=60)
            return {"stdout": out.stdout, "parsed": self.parse(out.stdout)}
        except FileNotFoundError:
            return {"error": "smbclient not installed", "parsed": {"shares": []}}
        except Exception as e:
            return {"error": str(e), "parsed": {"shares": []}}
    def parse(self, raw):
        shares = []
        for line in raw.splitlines():
            if "Disk" in line or "IPC" in line or "Printer" in line:
                shares.append(line.strip())
        return {"shares": shares}
