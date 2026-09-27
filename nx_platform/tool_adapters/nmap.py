"""Nmap adapter — real, parses Nmap output into NyxOS model."""
import subprocess
import re
from nx_platform.tool_adapters.base import ToolAdapter


class NmapAdapter(ToolAdapter):
    name = "nmap"
    category = "network"
    binary = "nmap"

    def run(self, target, options=None):
        opts = options or ["-sV", "-T4", "-F"]
        try:
            out = subprocess.run(
                [self.binary] + opts + [target],
                capture_output=True, text=True, timeout=600,
            )
            return {"stdout": out.stdout, "stderr": out.stderr,
                    "returncode": out.returncode,
                    "parsed": self.parse(out.stdout)}
        except FileNotFoundError:
            return {"error": "nmap not installed", "parsed": {"hosts": []}}
        except subprocess.TimeoutExpired:
            return {"error": "timeout", "parsed": {"hosts": []}}

    def parse(self, raw):
        hosts = []
        current = None
        for line in raw.splitlines():
            m = re.match(r"Nmap scan report for (.+)$", line)
            if m:
                if current:
                    hosts.append(current)
                current = {"target": m.group(1), "ports": []}
            elif current and re.match(r"^\d+/tcp", line):
                parts = line.split()
                current["ports"].append({
                    "port": int(parts[0].split("/")[0]),
                    "state": parts[1],
                    "service": parts[2] if len(parts) > 2 else "unknown",
                })
        if current:
            hosts.append(current)
        return {"hosts": hosts}
