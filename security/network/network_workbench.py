"""Network Workbench — nmap with version detection."""
from nx_platform.workbench_sdk.workbench import Workbench
from nx_platform.tool_adapters.nmap import NmapAdapter
from nx_platform.tool_adapters.nmap_udp import NmapUdpAdapter
from core.assets.asset_engine import AssetEngine
from core.findings.finding_engine import FindingEngine
from core.evidence.evidence_engine import EvidenceEngine


RISKY_SERVICES = {
    "telnet": ("critical", "Cleartext protocol — credentials exposed"),
    "ftp":    ("high",     "Cleartext FTP — check anonymous access"),
    "smb":    ("high",     "SMB exposed — check EternalBlue/MS17-010"),
    "rdp":    ("high",     "RDP exposed — check BlueKeep/NLA"),
    "vnc":    ("high",     "VNC exposed — check authentication"),
    "mysql":  ("medium",   "MySQL exposed — check auth"),
    "postgres": ("medium", "PostgreSQL exposed"),
    "mongodb": ("medium",  "MongoDB exposed — check auth (default no-auth in old versions)"),
}


class NetworkWorkbench(Workbench):
    name = "network"
    domain = "Network Security"
    description = "Port scan, service detection, risky service alerts"

    def __init__(self, db, bus=None, ctx=None):
        super().__init__(ctx)
        self.db = db
        self.assets = AssetEngine(db, bus)
        self.findings = FindingEngine(db, bus)
        self.evidence = EvidenceEngine(db, bus)
        self.nmap = NmapAdapter()
        self.nmap_udp = NmapUdpAdapter()

    def discover(self, target, options=None):
        options = options or {}
        case_id = options["case_id"]
        aid = self.assets.add(case_id, "host", target)
        self._results.assets.append({"id": aid, "identifier": target})

        tcp_args = options.get("nmap_args") or ["-sV", "-T4", "--top-ports", "200"]
        res = self.nmap.run(target, tcp_args)

        for host in res.get("parsed", {}).get("hosts", []):
            for p in host["ports"]:
                svc_id = self.assets.add(
                    case_id, "service",
                    f"{host['target']}:{p['port']}",
                    {"service": p["service"], "state": p["state"]})
                self._results.assets.append(p)

                if p["state"] != "open":
                    continue

                svc = p["service"].lower()
                if svc in RISKY_SERVICES:
                    sev, note = RISKY_SERVICES[svc]
                    fid = self.findings.add(
                        case_id,
                        f"{svc.upper()} exposed on {host['target']}:{p['port']}",
                        sev, asset_id=svc_id, details={"note": note})["id"]
                    self.evidence.add(fid, "nmap_line",
                                      f"{p['port']}/{svc} on {host['target']}")

        self._results.raw = {"hosts": res.get("parsed", {}).get("hosts", [])}
        return self._results

    def analyze(self, asset):
        return self._results
