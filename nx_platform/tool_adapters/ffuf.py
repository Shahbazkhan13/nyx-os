"""ffuf — fast web fuzzer."""
import subprocess
from nx_platform.tool_adapters.base import ToolAdapter

class FFUFAdapter(ToolAdapter):
    name = "ffuf"
    category = "web"
    binary = "ffuf"
    def run(self, target, options=None):
        url = target if target.startswith("http") else f"http://{target}"
        wordlist = (options or {}).get("wordlist",
                    "/usr/share/wordlists/dirb/common.txt")
        try:
            out = subprocess.run(
                ["ffuf", "-u", f"{url}/FUZZ", "-w", wordlist,
                 "-mc", "200,301,302,403", "-t", "50",
                 "-timeout", "5", "-s"],
                capture_output=True, text=True, timeout=300)
            return {"stdout": out.stdout, "parsed": self.parse(out.stdout)}
        except FileNotFoundError:
            return {"error": "ffuf not installed", "parsed": {"paths": []}}
        except Exception as e:
            return {"error": str(e), "parsed": {"paths": []}}
    def parse(self, raw):
        paths = [{"path": l.strip()} for l in raw.splitlines() if l.strip()]
        return {"paths": paths}
