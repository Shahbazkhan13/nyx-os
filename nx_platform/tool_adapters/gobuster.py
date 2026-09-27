"""gobuster — directory bruteforce."""
import subprocess
from nx_platform.tool_adapters.base import ToolAdapter


class GobusterAdapter(ToolAdapter):
    name = "gobuster"
    category = "web"
    binary = "gobuster"

    def run(self, target, options=None):
        url = target if target.startswith("http") else f"http://{target}"
        wordlist = (options or {}).get("wordlist", "/usr/share/wordlists/dirb/common.txt")
        try:
            out = subprocess.run(
                ["gobuster", "dir", "-u", url, "-w", wordlist, "-q", "-t", "20", "--timeout", "5s"],
                capture_output=True, text=True, timeout=300)
            return {"stdout": out.stdout, "parsed": self.parse(out.stdout)}
        except FileNotFoundError:
            return {"error": "gobuster not installed", "parsed": {"paths": []}}
        except Exception as e:
            return {"error": str(e), "parsed": {"paths": []}}

    def parse(self, raw):
        paths = []
        for line in raw.splitlines():
            if line.startswith("/") or line.startswith("http"):
                parts = line.split()
                if len(parts) >= 2:
                    paths.append({"path": parts[0], "status": parts[1]})
        return {"paths": paths}
