"""NyxOS Recon Workbench - First Domain"""
import subprocess, json, re
from nx_nx_platform.workbench_sdk.workbench import Workbench

class ReconWorkbench(Workbench):
    name = "recon"
    domain = "Recon & OSINT"

    def discover(self, target):
        results = {}
        results["dns"] = self._dns_lookup(target)
        results["whois"] = self._whois(target)
        return results

    def _dns_lookup(self, target):
        try:
            out = subprocess.run(["dig", "+short", target], capture_output=True, text=True, timeout=15)
            return [l for l in out.stdout.strip().split("\n") if l]
        except Exception as e:
            return {"error": str(e)}

    def _whois(self, target):
        try:
            out = subprocess.run(["whois", target], capture_output=True, text=True, timeout=20)
            return out.stdout[:2000]
        except Exception as e:
            return {"error": str(e)}

    def analyze(self, asset):
        return {"asset": asset, "notes": "analysis placeholder"}
