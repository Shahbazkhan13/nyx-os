"""Nmap adapter example"""
from .base import ToolAdapter
import re

class NmapAdapter(ToolAdapter):
    name = "nmap"
    category = "network"
    binary = "nmap"
    version = "7.x"

    def run(self, target, options=None):
        opts = options or ["-sV", "-T4"]
        res = self.execute(opts + [target], timeout=600)
        res["parsed"] = self.parse(res["stdout"])
        return res

    def parse(self, raw):
        hosts = []
        current = None
        for line in raw.splitlines():
            if line.startswith("Nmap scan report for"):
                if current: hosts.append(current)
                ip = re.search(r"for (.+)$", line)
                current = {"target": ip.group(1) if ip else "?", "ports": []}
            elif current and re.match(r"^\d+/tcp", line):
                parts = line.split()
                current["ports"].append({
                    "port": parts[0].split("/")[0],
                    "state": parts[1],
                    "service": parts[2] if len(parts) > 2 else "?",
                })
        if current: hosts.append(current)
        return {"hosts": hosts}
