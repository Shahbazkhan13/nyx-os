"""Wireless Security Workbench."""
import subprocess
from nx_platform.workbench_sdk.workbench import Workbench
from core.assets.asset_engine import AssetEngine
from core.findings.finding_engine import FindingEngine


class WirelessWorkbench(Workbench):
    name = "wireless"
    domain = "Wireless Security"
    description = "WiFi interface info, MAC analysis"

    def __init__(self, db, bus=None, ctx=None):
        super().__init__(ctx)
        self.db = db
        self.assets = AssetEngine(db, bus)
        self.findings = FindingEngine(db, bus)

    def discover(self, target, options=None):
        options = options or {}
        case_id = options["case_id"]
        interfaces = self._list_interfaces()
        for iface in interfaces:
            self.assets.add(case_id, "wireless_interface", iface,
                            {"source": "iwconfig"})
            self._results.assets.append({"interface": iface})

        # Warning if running in WSL/VM (no wifi passthrough)
        if not interfaces:
            self.findings.add(case_id,
                              "No wireless interface detected (likely VM/WSL)",
                              "info")
        return self._results

    def analyze(self, asset):
        return self._results

    def _list_interfaces(self):
        try:
            out = subprocess.run(["iwconfig"], capture_output=True,
                                 text=True, timeout=5)
            ifaces = []
            for line in out.stdout.splitlines():
                if "IEEE 802.11" in line:
                    ifaces.append(line.split()[0])
            return ifaces
        except Exception:
            return []
