"""Red Team Workbench — authorized exploitation planning."""
from nx_platform.workbench_sdk.workbench import Workbench
from core.assets.asset_engine import AssetEngine
from core.findings.finding_engine import FindingEngine


ATTACK_SUGGESTIONS = {
    "ssh": ["Try default creds", "Check for weak keys", "Version-based CVE lookup"],
    "ftp": ["Anonymous login test", "Brute force risk"],
    "http": ["Directory bruteforce", "Check security headers", "Known CMS vulns"],
    "smb": ["Null session test", "SMB signing check", "EternalBlue check"],
    "rdp": ["NLA check", "BlueKeep vulnerability"],
    "mysql": ["Anonymous login", "Weak password check"],
    "telnet": ["Cleartext credentials capture", "Version-based CVE"],
}


class RedTeamWorkbench(Workbench):
    name = "redteam"
    domain = "Red Team / Exploitation"
    description = "Suggests exploitation paths from discovered services"

    def __init__(self, db, bus=None, ctx=None):
        super().__init__(ctx)
        self.db = db
        self.assets = AssetEngine(db, bus)
        self.findings = FindingEngine(db, bus)

    def discover(self, target, options=None):
        options = options or {}
        case_id = options["case_id"]

        # Authorized flag required (safety)
        if not options.get("authorized"):
            self.findings.add(case_id,
                              "Red Team requires authorized=True flag",
                              "info")
            return self._results

        for a in self.assets.list(case_id):
            if a["type"] != "service":
                continue
            svc = (a["metadata"].get("service") or "").lower()
            if svc in ATTACK_SUGGESTIONS:
                for suggestion in ATTACK_SUGGESTIONS[svc]:
                    self.findings.add(case_id,
                                      f"[RedTeam] {svc}: {suggestion}",
                                      "medium", asset_id=a["id"])
                    self._results.findings.append({"service": svc, "action": suggestion})
        return self._results

    def analyze(self, asset):
        return self._results
