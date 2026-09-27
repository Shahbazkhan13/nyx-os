"""sqlmap — SQL injection detector (safe defaults)."""
import subprocess
from nx_platform.tool_adapters.base import ToolAdapter


class SqlmapAdapter(ToolAdapter):
    name = "sqlmap"
    category = "database"
    binary = "sqlmap"

    def run(self, target, options=None):
        opts = (options or {})
        args = ["-u", target, "--batch", "--level=1", "--risk=1",
                "--timeout=10", "--retries=1", "--threads=2", "--smart"]
        if opts.get("safe_only", True):
            args.append("--technique=B")
        try:
            out = subprocess.run(["sqlmap"] + args,
                                 capture_output=True, text=True, timeout=600)
            return {"stdout": out.stdout[-5000:], "parsed": self.parse(out.stdout)}
        except FileNotFoundError:
            return {"error": "sqlmap not installed", "parsed": {"vulnerable": False}}
        except Exception as e:
            return {"error": str(e), "parsed": {"vulnerable": False}}

    def parse(self, raw):
        return {
            "vulnerable": "is vulnerable" in raw.lower() or "Parameter:" in raw,
            "raw_tail": raw[-500:],
        }
