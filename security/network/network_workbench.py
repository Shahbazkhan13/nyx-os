"""Network Security Workbench."""
from nx_platform.workbench_sdk.workbench import Workbench, WorkbenchResult
from nx_platform.tool_adapters.nmap import NmapAdapter
from core.assets.asset_engine import AssetEngine
from core.findings.finding_engine import FindingEngine


class NetworkWorkbench(Workbench):
    name = "network"
    domain = "Network Security"
    description = "Port scanning, service detection, network mapping"

    def __init__(self, db, bus=None, ctx=None):
        super().__init__(ctx)
        self.db = db
        self.assets = AssetEngine(db, bus)
        self.findings = FindingEngine(db, bus)
        self.nmap = NmapAdapter()

    def discover(self, target, options=None):
        options = options or {}
        case_id = options["case_id"]
        aid = self.assets.add(case_id, "host", target)
        self._results.assets.append({"id": aid, "identifier": target})

        res = self.nmap.run(target, options.get("nmap_args"))
        for host in res.get("parsed", {}).get("hosts", []):
            for p in host["ports"]:
                self.assets.add(case_id, "service",
                                 f"{host['target']}:{p['port']}",
                                 {"service": p["service"], "state": p["state"]})
                self._results.assets.append(p)
                if p["state"] == "open":
                    sev = "info"
                    if p["service"] in ("telnet", "ftp"):
                        sev = "high"
                    elif p["service"] in ("http", "smtp"):
                        sev = "low"
                    self.findings.add(case_id,
                                      f"Open {p['service']} on {host['target']}:{p['port']}",
                                      sev)
        return self._results

    def analyze(self, asset):
        return self._results
