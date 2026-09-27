"""NyxOS Reporting — generate reports from case data."""
import json
import os
from datetime import datetime


class Reporter:
    def __init__(self, db):
        self.db = db

    def _case(self, case_id):
        r = self.db.fetchone("SELECT * FROM cases WHERE id=?", (case_id,))
        return dict(r) if r else None

    def _assets(self, case_id):
        return [dict(r) for r in self.db.fetchall(
            "SELECT * FROM assets WHERE case_id=?", (case_id,))]

    def _findings(self, case_id):
        return [dict(r) for r in self.db.fetchall(
            "SELECT * FROM findings WHERE case_id=? ORDER BY risk_score DESC",
            (case_id,))]

    def _evidence(self, finding_id):
        return [dict(r) for r in self.db.fetchall(
            "SELECT * FROM evidence WHERE finding_id=?", (finding_id,))]

    def to_json(self, case_id):
        return json.dumps({
            "case": self._case(case_id),
            "assets": self._assets(case_id),
            "findings": self._findings(case_id),
            "generated_at": datetime.utcnow().isoformat(),
        }, indent=2)

    def to_markdown(self, case_id):
        c = self._case(case_id) or {}
        lines = [f"# Report: {c.get('name','Untitled')}", ""]
        lines.append(f"**Generated:** {datetime.utcnow().isoformat()}")
        lines.append(f"**Status:** {c.get('status','?')}")
        lines.append("")
        lines.append("## Assets")
        for a in self._assets(case_id):
            lines.append(f"- [{a['type']}] {a['identifier']}")
        lines.append("")
        lines.append("## Findings")
        for f in self._findings(case_id):
            lines.append(f"### {f['title']}  (sev={f['severity']}, risk={f['risk_score']})")
            ev = self._evidence(f["id"])
            for e in ev:
                lines.append(f"- evidence[{e['type']}] hash={e['hash'][:12]}...")
            lines.append("")
        return "\n".join(lines)

    def save(self, case_id, path, fmt="markdown"):
        if fmt == "json":
            content = self.to_json(case_id)
        else:
            content = self.to_markdown(case_id)
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        return path
