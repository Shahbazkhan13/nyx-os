"""openssl cert inspection adapter."""
import subprocess
from nx_platform.tool_adapters.base import ToolAdapter


class OpenSSLCertAdapter(ToolAdapter):
    name = "openssl-cert"
    category = "crypto"
    binary = "openssl"

    def run(self, target, options=None):
        try:
            out = subprocess.run(
                ["openssl", "s_client", "-connect", f"{target}:443",
                 "-servername", target, "-showcerts"],
                input="", capture_output=True, text=True, timeout=20,
            )
            return {"stdout": out.stdout, "parsed": self.parse(out.stdout)}
        except Exception as e:
            return {"error": str(e), "parsed": {}}

    def parse(self, raw):
        info = {}
        for line in raw.splitlines():
            line = line.strip()
            for key in ["subject=", "issuer=", "notBefore=", "notAfter="]:
                if line.startswith(key):
                    info[key.strip("=")] = line[len(key):].strip()
        return info
