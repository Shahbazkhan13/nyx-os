"""Recon Workbench — dig, whois, subfinder, whatweb."""
from nx_platform.workbench_sdk.workbench import Workbench
from nx_platform.tool_adapters.dig import DigAdapter
from nx_platform.tool_adapters.whois import WhoisAdapter
from nx_platform.tool_adapters.subfinder import SubfinderAdapter
from nx_platform.tool_adapters.whatweb import WhatWebAdapter
from core.assets.asset_engine import AssetEngine
from core.findings.finding_engine import FindingEngine
from core.evidence.evidence_engine import EvidenceEngine


class ReconWorkbench(Workbench):
    name = "recon"
    domain = "Recon & OSINT"
    description = "DNS, WHOIS, subdomain, web-fingerprint discovery"

    def __init__(self, db, bus=None, ctx=None):
        super().__init__(ctx)
        self.db = db
        self.assets = AssetEngine(db, bus)
        self.findings = FindingEngine(db, bus)
        self.evidence = EvidenceEngine(db, bus)
        self.dig = DigAdapter()
        self.whois = WhoisAdapter()
        self.subfinder = SubfinderAdapter()
        self.whatweb = WhatWebAdapter()

    def discover(self, target, options=None):
        options = options or {}
        case_id = options["case_id"]

        aid = self.assets.add(case_id, "domain", target)
        self._results.assets.append({"id": aid, "identifier": target})

        # DNS
        dns = self.dig.run(target, {"type": "A"})
        ips = dns["parsed"]["records"][:5]
        for ip in ips:
            self.assets.add(case_id, "ip", ip, {"parent": target})
            self._results.assets.append({"identifier": ip, "type": "ip"})

        # WHOIS — evidence
        w = self.whois.run(target)
        if w.get("parsed"):
            fid = self.findings.add(case_id, f"WHOIS {target}", "info")["id"]
            self.evidence.add(fid, "whois", str(w["parsed"])[:4000])

        # Subdomains
        if options.get("subdomains", True):
            sf = self.subfinder.run(target)
            for sub in sf["parsed"].get("subdomains", [])[:50]:
                self.assets.add(case_id, "subdomain", sub, {"parent": target})
                self._results.assets.append({"identifier": sub, "type": "subdomain"})

        # Web tech
        if options.get("web_fingerprint", True):
            ww = self.whatweb.run(target)
            tech = ww["parsed"].get("tech", [])
            if tech:
                fid = self.findings.add(case_id,
                                        f"Technologies: {', '.join(tech[:8])}",
                                        "info", details={"tech": tech})["id"]
                self.evidence.add(fid, "whatweb", ", ".join(tech))

        self._results.raw = {"ips": ips, "tech": ww["parsed"].get("tech", [])}
        return self._results

    def analyze(self, asset):
        return self._results
