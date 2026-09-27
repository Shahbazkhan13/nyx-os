"""sslyze — SSL/TLS scanner."""
import subprocess
from nx_platform.tool_adapters.base import ToolAdapter


class SSLyzeAdapter(ToolAdapter):
    name = "sslyze"
    category = "crypto"
    binary = "sslyze"

    def run(self, target, options=None):
        host = target.split(":")[0]
        try:
            out = subprocess.run(
                ["sslyze", "--regular", f"{host}:443"],
                capture_output=True, text=True, timeout=180)
            return {"stdout": out.stdout[:8000], "parsed": self.parse(out.stdout)}
        except FileNotFoundError:
            return {"error": "sslyze not installed", "parsed": {}}
        except Exception as e:
            return {"error": str(e), "parsed": {}}

    def parse(self, raw):
        info = {"weak_protocols": [], "cert_info": {}}
        for line in raw.splitlines():
            low = line.lower()
            if "sslv2" in low or "sslv3" in low or "tls 1.0" in low:
                if "accepted" in low or "supported" in low:
                    info["weak_protocols"].append(line.strip())
        return info
