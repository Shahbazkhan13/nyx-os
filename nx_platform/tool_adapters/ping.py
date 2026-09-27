"""ping adapter."""
import subprocess, re
from nx_platform.tool_adapters.base import ToolAdapter


class PingAdapter(ToolAdapter):
    name = "ping"
    category = "network"
    binary = "ping"

    def run(self, target, options=None):
        count = (options or {}).get("count", 3)
        try:
            out = subprocess.run([self.binary, "-c", str(count), target],
                                 capture_output=True, text=True, timeout=30)
            return {"stdout": out.stdout, "parsed": self.parse(out.stdout)}
        except Exception as e:
            return {"error": str(e), "parsed": {"alive": False}}

    def parse(self, raw):
        alive = "0% packet loss" in raw or "bytes from" in raw
        m = re.search(r"(\d+)% packet loss", raw)
        loss = int(m.group(1)) if m else 100
        return {"alive": alive, "packet_loss": loss}
