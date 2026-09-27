"""hashcat adapter — identify hash type."""
import subprocess, re, tempfile, os
from nx_platform.tool_adapters.base import ToolAdapter


class HashcatAdapter(ToolAdapter):
    name = "hashcat"
    category = "credentials"
    binary = "hashcat"

    def run(self, target, options=None):
        """target = hash string"""
        try:
            f = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".hash")
            f.write(target + "\n")
            f.close()
            out = subprocess.run(
                ["hashcat", "--identify", f.name],
                capture_output=True, text=True, timeout=30,
            )
            os.unlink(f.name)
            return {"stdout": out.stdout, "parsed": self.parse(out.stdout)}
        except FileNotFoundError:
            return {"error": "hashcat not installed", "parsed": {}}
        except Exception as e:
            return {"error": str(e), "parsed": {}}

    def parse(self, raw):
        # Extract "Hash-mode: X" or "Hash-Name: Y"
        mode = re.search(r"Hash-mode.*?:\s*(\S+)", raw)
        name = re.search(r"Hash-Name.*?:\s*(.+)", raw)
        return {
            "mode": mode.group(1) if mode else None,
            "name": name.group(1).strip() if name else None,
        }
