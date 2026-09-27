"""NyxOS Recon Workbench — first real security domain."""
import subprocess
from nx_platform.workbench_sdk.workbench import Workbench, WorkbenchResult
from core.assets.asset_engine import AssetEngine
from core.findings.finding_engine import FindingEngine
from core.evidence.evidence_engine import EvidenceEngine


class ReconWorkbench(Workbench):
    name = "recon"
    domain = "Recon & OSINT"
    description = "DNS, WHOIS, subdomain, port discovery"

    def __init__(self, db, bus=None, ctx=None):
        super().__init__(ctx)
        self.db = db
        self.assets = AssetEngine(db, bus)
        self.findings = FindingEngine(db, bus)
        self.evidence = EvidenceEngine(db, bus)

    def discover(self, target, options=None):
        options = options or {}
        case_id = options.get("case_id")
        if not case_id:
            raise ValueError("case_id required")

        # Register target as asset
        aid = self.assets.add(case_id, "domain", target)
        self._results.assets.append({"id": aid, "identifier": target})

        # DNS
        dns = self._dns_lookup(target)
        if dns:
            self.assets.add(case_id, "ip", dns, {"parent": target})
            self._results.assets.append({"identifier": dns, "type": "ip"})

        # WHOIS
        whois = self._whois(target)
        if whois:
            ev = self.evidence.add(
                self.findings.add(case_id, f"WHOIS {target}", "info")["id"],
                "whois", whois,
            )
            self._results.evidence.append(ev)

        # Port scan (optional)
        if options.get("scan_ports") and dns:
            ports = self._port_scan(dns)
            for p in ports:
                self.assets.add(case_id, "service", f"{dns}:{p['port']}",
                                 {"port": p["port"], "service": p["service"]})
                self._results.assets.append(p)

        return self._results

    def analyze(self, asset):
        return self._results

    def _dns_lookup(self, target):
        try:
            out = subprocess.run(["dig", "+short", target],
                                 capture_output=True, text=True, timeout=15)
            lines = [l for l in out.stdout.strip().split("\n") if l]
            return lines[0] if lines else ""
        except Exception:
            return ""

    def _whois(self, target):
        try:
            out = subprocess.run(["whois", target],
                                 capture_output=True, text=True, timeout=20)
            return out.stdout[:4000]
        except Exception:
            return ""

    def _port_scan(self, ip):
        try:
            out = subprocess.run(["nmap", "-F", "-sV", ip],
                                 capture_output=True, text=True, timeout=180)
            results = []
            for line in out.stdout.splitlines():
                if "/tcp" in line and "open" in line:
                    parts = line.split()
                    results.append({
                        "port": parts[0].split("/")[0],
                        "state": parts[1],
                        "service": parts[2] if len(parts) > 2 else "unknown",
                    })
            return results
        except Exception:
            return []
