"""NyxOS Local AI Assistant.

Deterministic rule-based assistant + optional ollama integration.
"""
import json
import subprocess
import shutil


TOOL_DOCS = {
    "nmap": {"what": "Network mapper — port and service discovery.",
             "when": "First step of network assessment.",
             "cmd": "nmap -sV -T4 <target>",
             "notes": "Slow scans can be detected by IDS."},
    "dig": {"what": "DNS lookup utility.",
            "when": "When resolving domains / enumerating records.",
            "cmd": "dig +short <domain>",
            "notes": "Try different record types: A, MX, TXT, NS."},
    "whois": {"what": "Domain registration lookup.",
              "when": "Reconnaissance — owner, registrar, dates.",
              "cmd": "whois <domain>",
              "notes": "Privacy services may hide info."},
    "sqlmap": {"what": "SQL injection automation.",
               "when": "Found parameterized web input.",
               "cmd": "sqlmap -u '<url>?id=1' --batch --risk=1 --level=1",
               "notes": "Only on authorized targets."},
    "hashcat": {"what": "Password hash cracking.",
                "when": "Recovered hashes need analysis.",
                "cmd": "hashcat -m <mode> hash.txt wordlist.txt",
                "notes": "Use --identify to detect hash type."},
    "nuclei": {"what": "Template-based vulnerability scanner.",
               "when": "Automated web vuln checks.",
               "cmd": "nuclei -u <url> -severity medium,high,critical",
               "notes": "Fast, community templates."},
}

NEXT_STEPS = {
    "recon": ["Run network scan on discovered IPs.",
              "Fingerprint web technologies.",
              "Enumerate subdomains."],
    "network": ["Run vulnerability assessment on found services.",
                "Check for default credentials on exposed services.",
                "Verify firewall rules."],
    "vulnerability": ["Prioritize critical findings.",
                      "Capture evidence for report.",
                      "Recommend mitigations."],
    "web": ["Check authentication endpoints.",
            "Test input validation (authorized).",
            "Review security headers."],
}


class Assistant:
    def __init__(self, model=None, ollama_model=None):
        self.model = model
        self.ollama_model = ollama_model or "llama3.2"
        self.ollama_available = shutil.which("ollama") is not None

    # ---------- Tool explanation ----------
    def explain_tool(self, tool_name):
        info = TOOL_DOCS.get(tool_name.lower())
        if info:
            return {"tool": tool_name, **info}
        # optional LLM fallback
        if self.ollama_available:
            return {"tool": tool_name, "ai": self._ask_ollama(
                f"In 2 sentences explain the security tool: {tool_name}")}
        return {"tool": tool_name,
                "note": "No built-in doc. Install ollama for AI explanations."}

    # ---------- Output explanation ----------
    def explain_output(self, tool_name, output):
        tool = tool_name.lower()
        if tool == "nmap":
            return self._explain_nmap(output)
        if tool == "dig":
            return self._explain_dig(output)
        if "vulnerab" in tool or "cve" in output.lower():
            return {"summary": "Vulnerability data detected.",
                    "raw_len": len(output)}
        return {"tool": tool_name, "summary": output[:300] if output else ""}

    def _explain_nmap(self, out):
        open_count = out.count(" open ")
        services = [w for w in out.split() if w.islower() and w.isalpha()][:10]
        return {"open_ports_estimate": open_count,
                "services_mentioned": services,
                "advice": "Investigate each open service for CVEs and default creds."}

    def _explain_dig(self, out):
        return {"records": [l for l in out.splitlines() if l.strip()][:10],
                "advice": "Enumerate A, MX, TXT, NS records for full DNS picture."}

    # ---------- Next-step suggestions ----------
    def suggest_next(self, context):
        domain = (context or {}).get("domain", "").lower()
        return {"suggestions": NEXT_STEPS.get(domain,
                ["Run recon.", "Run network scan.", "Run vulnerability assessment."])}

    # ---------- Report assistant ----------
    def explain_finding(self, finding, evidence_list=None):
        sev = (finding.get("severity") or "info").lower()
        tips = {
            "critical": "Fix immediately — exploitation likely and high impact.",
            "high": "Fix soon — exploitable with real risk.",
            "medium": "Plan remediation — moderate risk.",
            "low": "Track — low risk but recommended.",
            "info": "Informational — no immediate action.",
        }
        return {"title": finding.get("title"),
                "severity": sev,
                "advice": tips.get(sev, ""),
                "evidence_count": len(evidence_list or [])}

    # ---------- Optional ollama ----------
    def _ask_ollama(self, prompt):
        try:
            out = subprocess.run(
                ["ollama", "run", self.ollama_model, prompt],
                capture_output=True, text=True, timeout=60)
            return out.stdout.strip()
        except Exception as e:
            return f"[ollama error: {e}]"
