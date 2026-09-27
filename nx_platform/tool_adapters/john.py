"""john adapter — identify hash type."""
import subprocess, re
from nx_platform.tool_adapters.base import ToolAdapter


class JohnAdapter(ToolAdapter):
    name = "john"
    category = "credentials"
    binary = "john"

    def run(self, target, options=None):
        import tempfile, os
        try:
            f = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".hash")
            f.write(target + "\n")
            f.close()
            out = subprocess.run(
                ["john", "--list=formats"],
                capture_output=True, text=True, timeout=15,
            )
            os.unlink(f.name)
            return {"stdout": out.stdout[:2000], "parsed": {"formats_available": True}}
        except FileNotFoundError:
            return {"error": "john not installed", "parsed": {}}
        except Exception as e:
            return {"error": str(e), "parsed": {}}

    def parse(self, raw):
        return {}
