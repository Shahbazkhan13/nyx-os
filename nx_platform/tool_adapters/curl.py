"""curl adapter."""
import subprocess
from nx_platform.tool_adapters.base import ToolAdapter


class CurlAdapter(ToolAdapter):
    name = "curl"
    category = "web"
    binary = "curl"

    def run(self, target, options=None):
        opts = (options or {}).get("args", ["-sI", "-m", "10"])
        try:
            out = subprocess.run([self.binary] + opts + [target],
                                 capture_output=True, text=True, timeout=30)
            return {"stdout": out.stdout, "parsed": self.parse(out.stdout)}
        except Exception as e:
            return {"error": str(e), "parsed": {}}

    def parse(self, raw):
        headers = {}
        for line in raw.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                headers[k.strip().lower()] = v.strip()
        return {"headers": headers}
