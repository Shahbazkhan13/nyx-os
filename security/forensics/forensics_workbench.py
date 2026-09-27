"""Digital Forensics Workbench."""
import os, hashlib, subprocess
from nx_platform.workbench_sdk.workbench import Workbench
from core.assets.asset_engine import AssetEngine
from core.findings.finding_engine import FindingEngine
from core.evidence.evidence_engine import EvidenceEngine


class ForensicsWorkbench(Workbench):
    name = "forensics"
    domain = "Digital Forensics"
    description = "File hashing, metadata, integrity verification"

    def __init__(self, db, bus=None, ctx=None):
        super().__init__(ctx)
        self.db = db
        self.assets = AssetEngine(db, bus)
        self.findings = FindingEngine(db, bus)
        self.evidence = EvidenceEngine(db, bus)

    def discover(self, target, options=None):
        """target = file path"""
        options = options or {}
        case_id = options["case_id"]

        if not os.path.isfile(target):
            self.findings.add(case_id, f"File not found: {target}", "info")
            return self._results

        size = os.path.getsize(target)
        sha256 = self._hash_file(target, "sha256")
        md5 = self._hash_file(target, "md5")
        ftype = self._file_type(target)

        aid = self.assets.add(case_id, "file", target,
                              {"size": size, "sha256": sha256, "md5": md5})
        self._results.assets.append({"id": aid, "path": target, "size": size})

        fid = self.findings.add(case_id, f"File analyzed: {os.path.basename(target)}",
                                "info", asset_id=aid,
                                details={"sha256": sha256, "md5": md5, "type": ftype})["id"]
        self.evidence.add(fid, "hash", f"sha256={sha256}\nmd5={md5}\ntype={ftype}")

        self._results.raw = {"sha256": sha256, "md5": md5, "type": ftype, "size": size}
        return self._results

    def analyze(self, asset):
        return self._results

    def _hash_file(self, path, algo):
        h = hashlib.new(algo)
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    def _file_type(self, path):
        try:
            out = subprocess.run(["file", "-b", path], capture_output=True,
                                 text=True, timeout=5)
            return out.stdout.strip()
        except Exception:
            return "unknown"
