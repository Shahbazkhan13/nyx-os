"""Generate workbench stubs for remaining domains.
Real tools get real workbenches; others get structured stubs.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (folder, class, name, domain, description, tools)
DOMAINS = [
    ("database",       "DatabaseWorkbench",     "database",     "Database Security",
     "SQL injection detection, DB enumeration", ["sqlmap"]),
    ("active_directory","ADWorkbench",          "ad",           "Active Directory & Identity",
     "AD enumeration, Kerberos attacks",        ["ldapsearch", "kerberos"]),
    ("privesc",        "PrivEscWorkbench",      "privesc",      "Privilege Escalation",
     "Local privesc enumeration",               ["linpeas"]),
    ("postexploit",    "PostExploitWorkbench",  "postexploit",  "Post-Exploitation",
     "Persistence, pivoting, exfiltration",     []),
    ("reversing",      "ReversingWorkbench",    "reversing",    "Reverse Engineering",
     "Binary analysis, disassembly",            ["objdump", "strings"]),
    ("malware",        "MalwareWorkbench",      "malware",      "Malware Analysis",
     "Static/dynamic malware analysis",         ["file", "strings"]),
    ("mobile",         "MobileWorkbench",       "mobile",       "Mobile Security",
     "APK/IPA analysis",                        []),
    ("ai",             "AISecurityWorkbench",   "ai-security",  "AI Security",
     "ML model attacks, prompt injection",      []),
    ("cloud",          "CloudWorkbench",        "cloud",        "Cloud Security",
     "Cloud misconfiguration, IAM audit",       []),
    ("container",      "ContainerWorkbench",    "container",    "Container & Kubernetes Security",
     "Container escape, k8s audit",             []),
    ("api",            "APIWorkbench",          "api",          "API Security",
     "REST/GraphQL security testing",           ["curl"]),
    ("hardware",       "HardwareWorkbench",     "hardware",     "Hardware / IoT / Embedded",
     "Firmware analysis, IoT scanning",         []),
    ("ot",             "OTWorkbench",           "ot",           "OT / ICS Security",
     "Industrial control systems testing",      []),
    ("fuzzing",        "FuzzingWorkbench",      "fuzzing",      "Fuzzing & Research",
     "Fuzzing campaigns, crash triage",         []),
    ("crypto",         "CryptoWorkbench",       "crypto",       "Cryptography & Steganography",
     "Cert analysis, stego detection",          ["openssl"]),
    ("blueteam",       "BlueTeamWorkbench",     "blueteam",     "Blue Team / Defensive",
     "Detection, hardening, monitoring",        []),
    ("reporting",      "ReportingWorkbench",    "reporting",    "Reporting & Case Management",
     "Report generation, case tracking",        []),
]

TEMPLATE = '''"""{description}"""
from nx_platform.workbench_sdk.workbench import Workbench
from core.assets.asset_engine import AssetEngine
from core.findings.finding_engine import FindingEngine
from core.evidence.evidence_engine import EvidenceEngine


class {cls}(Workbench):
    name = "{name}"
    domain = "{domain}"
    description = "{description}"

    def __init__(self, db, bus=None, ctx=None):
        super().__init__(ctx)
        self.db = db
        self.assets = AssetEngine(db, bus)
        self.findings = FindingEngine(db, bus)
        self.evidence = EvidenceEngine(db, bus)

    def discover(self, target, options=None):
        options = options or {{}}
        case_id = options.get("case_id")
        if not case_id:
            raise ValueError("case_id required")

        # Register target as asset
        aid = self.assets.add(case_id, "{name}_target", str(target or ""),
                              {{"domain": self.domain}})
        self._results.assets.append({{"id": aid, "identifier": str(target)}})

        # Domain-specific analysis placeholder — replaced as tools are integrated
        self._results.raw = {{
            "domain": self.domain,
            "available_tools": {tools},
            "note": "Workbench ready for tool integration.",
        }}
        return self._results

    def analyze(self, asset):
        return self._results
'''

for folder, cls, name, domain, desc, tools in DOMAINS:
    path = os.path.join(ROOT, "security", folder)
    os.makedirs(path, exist_ok=True)
    init = os.path.join(path, "__init__.py")
    open(init, "a").close()

    fname = os.path.join(path, f"{folder}_workbench.py")
    with open(fname, "w") as f:
        f.write(TEMPLATE.format(cls=cls, name=name, domain=domain,
                                description=desc, tools=tools))
    print(f"  created {fname}")

print("done")
