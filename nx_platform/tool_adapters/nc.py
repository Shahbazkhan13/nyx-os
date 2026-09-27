"""netcat adapter — quick TCP port check."""
import subprocess
from nx_platform.tool_adapters.base import ToolAdapter


class NcAdapter(ToolAdapter):
    name = "nc"
    category = "network"
    binary = "nc"

    def run(self, target, options=None):
        port = (options or {}).get("port", 80)
        try:
            out = subprocess.run(
                ["nc", "-zv", "-w", "3", target, str(port)],
                capture_output=True, text=True, timeout=10,
            )
            return {
                "stdout": out.stdout + out.stderr,
                "parsed": {"open": out.returncode == 0},
            }
        except Exception as e:
            return {"error": str(e), "parsed": {"open": False}}

    def parse(self, raw):
        return {"open": "succeeded" in raw.lower() or "open" in raw.lower()}
