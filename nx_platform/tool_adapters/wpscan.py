"""wpscan — WordPress vulnerability scanner."""
import subprocess
from nx_platform.tool_adapters.base import ToolAdapter

class WPScanAdapter(ToolAdapter):
    name = "wpscan"
    category = "web"
    binary = "wpscan"
    def run(self, target, options=None):
        url = target if target.startswith("http") else f"http://{target}"
        opts = (options or {})
        args = ["wpscan", "--url", url, "--no-banner", "--random-user-agent"]
        if opts.get("enumerate"):
            args += ["-e", "vp,vt,u"]
        if opts.get("api_token"):
            args += ["--api-token", opts["api_token"]]
        try:
            out = subprocess.run(args, capture_output=True, text=True, timeout=600)
            return {"stdout": out.stdout[:8000], "parsed": self.parse(out.stdout)}
        except FileNotFoundError:
            return {"error": "wpscan not installed", "parsed": {}}
        except Exception as e:
            return {"error": str(e), "parsed": {}}
    def parse(self, raw):
        info = {"version": None, "vulnerabilities": [], "users": []}
        for line in raw.splitlines():
            if "WordPress version" in line:
                m = line.split("version")
                if len(m) > 1: info["version"] = m[1].strip()
            if "[!]" in line:
                info["vulnerabilities"].append(line.strip())
            if "User(s) Identified" in line:
                info["users"].append(line.strip())
        return info
