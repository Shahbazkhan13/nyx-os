"""whois adapter."""
import subprocess
from nx_platform.tool_adapters.base import ToolAdapter


class WhoisAdapter(ToolAdapter):
    name = "whois"
    category = "recon"
    binary = "whois"

    def run(self, target, options=None):
        try:
            out = subprocess.run(
                [self.binary, target],
                capture_output=True, text=True, timeout=30,
            )
            return {"stdout": out.stdout, "parsed": self.parse(out.stdout)}
        except Exception as e:
            return {"error": str(e), "parsed": {}}

    def parse(self, raw):
        info = {}
        for line in raw.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                k = k.strip().lower()
                v = v.strip()
                if k and v:
                    info.setdefault(k, v)
        return info
