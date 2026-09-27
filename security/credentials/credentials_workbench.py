"""Credentials Workbench — hash analysis, policy check."""
import re
import hashlib
from nx_platform.workbench_sdk.workbench import Workbench
from core.findings.finding_engine import FindingEngine


HASH_PATTERNS = [
    (r"^[a-f0-9]{32}$", "md5", "weak"),
    (r"^[a-f0-9]{40}$", "sha1", "weak"),
    (r"^[a-f0-9]{64}$", "sha256", "ok"),
    (r"^[a-f0-9]{128}$", "sha512", "ok"),
    (r"^\$2[aby]\$", "bcrypt", "ok"),
    (r"^\$argon2", "argon2", "ok"),
]


class CredentialsWorkbench(Workbench):
    name = "credentials"
    domain = "Password & Credential Security"
    description = "Hash identification, weak hash detection"

    def __init__(self, db, bus=None, ctx=None):
        super().__init__(ctx)
        self.db = db
        self.findings = FindingEngine(db, bus)

    def discover(self, target, options=None):
        """target = hash string to analyze."""
        options = options or {}
        case_id = options["case_id"]
        for pat, name, strength in HASH_PATTERNS:
            if re.match(pat, target):
                self._results.raw = {"hash_type": name, "strength": strength}
                if strength == "weak":
                    self.findings.add(case_id,
                                      f"Weak hash algorithm: {name}", "high",
                                      details={"hash_prefix": target[:8]})
                    self._results.findings.append({"type": name, "weak": True})
                return self._results
        self._results.raw = {"hash_type": "unknown"}
        return self._results

    def analyze(self, asset):
        return self._results
