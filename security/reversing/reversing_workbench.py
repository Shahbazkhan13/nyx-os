"""Binary analysis, disassembly"""
from nx_platform.workbench_sdk.workbench import Workbench
from core.assets.asset_engine import AssetEngine
from core.findings.finding_engine import FindingEngine
from core.evidence.evidence_engine import EvidenceEngine


class ReversingWorkbench(Workbench):
    name = "reversing"
    domain = "Reverse Engineering"
    description = "Binary analysis, disassembly"

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
        aid = self.assets.add(case_id, "reversing_target", str(target or ""),
                              {"domain": self.domain})
        self._results.assets.append({"id": aid, "identifier": str(target)})

        # Domain-specific analysis placeholder — replaced as tools are integrated
        self._results.raw = {
            "domain": self.domain,
            "available_tools": ['objdump', 'strings'],
            "note": "Workbench ready for tool integration.",
        }
        return self._results

    def analyze(self, asset):
        return self._results
