"""Web Security Workbench."""
import subprocess
from nx_platform.workbench_sdk.workbench import Workbench
from core.assets.asset_engine import AssetEngine
from core.findings.finding_engine import FindingEngine
from core.evidence.evidence_engine import EvidenceEngine


class WebWorkbench(Workbench):
    name = "web"
    domain = "Web Security"
    description = "HTTP analysis, header audit, directory discovery"

    def __init__(self, db, bus=None, ctx=None):
        super().__init__(ctx)
        self.db = db
        self.assets = AssetEngine(db, bus)
        self.findings = FindingEngine(db, bus)
        self.evidence = EvidenceEngine(db, bus)

    def discover(self, target, options=None):
        options = options or {}
        case_id = options["case_id"]
        url = target if target.startswith("http") else f"https://{target}"
        aid = self.assets.add(case_id, "endpoint", url)
        self._results.assets.append({"id": aid, "url": url})

        headers = self._fetch_headers(url)
        if headers:
            fid = self.findings.add(case_id, f"HTTP headers for {url}", "info")["id"]
            self.evidence.add(fid, "http_headers", headers)

            missing = self._missing_security_headers(headers)
            for h in missing:
                self.findings.add(case_id, f"Missing security header: {h}", "low")

        return self._results

    def analyze(self, asset):
        return self._results

    def _fetch_headers(self, url):
        try:
            out = subprocess.run(["curl", "-sI", "-m", "10", url],
                                 capture_output=True, text=True, timeout=15)
            return out.stdout
        except Exception:
            return ""

    def _missing_security_headers(self, headers):
        required = ["strict-transport-security", "content-security-policy",
                    "x-frame-options", "x-content-type-options"]
        lower = headers.lower()
        return [h for h in required if h not in lower]
