"""sslscan — SSL/TLS scanner."""
import subprocess
from nx_platform.tool_adapters.base import ToolAdapter

class SSLScanAdapter(ToolAdapter):
    name = "sslscan"
    category = "crypto"
    binary = "sslscan"
    def run(self, target, options=None):
        host = target.split(":")[0]
        try:
            out = subprocess.run(
                ["sslscan", "--no-colour", f"{host}:443"],
                capture_output=True, text=True, timeout=120)
            return {"stdout": out.stdout[:8000], "parsed": self.parse(out.stdout)}
        except FileNotFoundError:
            return {"error": "sslscan not installed", "parsed": {}}
        except Exception as e:
            return {"error": str(e), "parsed": {}}
    def parse(self, raw):
        info = {"weak_protocols": [], "cert": {}}
        for line in raw.splitlines():
            low = line.lower()
            if ("sslv2" in low or "sslv3" in low or "tlsv1.0" in low) and "enabled" in low:
                info["weak_protocols"].append(line.strip())
            if "subject:" in low or "issuer:" in low:
                info["cert"][line.split(":")[0].strip()] = line.split(":",1)[1].strip()
        return info
