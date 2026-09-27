"""nmap UDP quick scan adapter."""
import subprocess
from nx_platform.tool_adapters.nmap import NmapAdapter


class NmapUdpAdapter(NmapAdapter):
    name = "nmap-udp"

    def run(self, target, options=None):
        try:
            out = subprocess.run(
                ["nmap", "-sU", "-F", "-T4", target],
                capture_output=True, text=True, timeout=600,
            )
            return {"stdout": out.stdout, "parsed": self.parse(out.stdout)}
        except Exception as e:
            return {"error": str(e), "parsed": {"hosts": []}}
