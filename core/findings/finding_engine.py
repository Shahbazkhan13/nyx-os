"""NyxOS Finding Engine — create + track findings."""
import json
from core.risk.engine import compute_risk


class FindingEngine:
    def __init__(self, db, bus=None):
        self.db = db
        self.bus = bus

    def add(self, case_id, title, severity="info", asset_id=None, details=None):
        risk = compute_risk(severity)
        cur = self.db.execute(
            "INSERT INTO findings(case_id, asset_id, title, severity, risk_score, details) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (case_id, asset_id, title, severity, risk,
             json.dumps(details or {})),
        )
        fid = cur.lastrowid
        if self.bus:
            self.bus.publish("finding.created", {
                "id": fid, "case_id": case_id,
                "title": title, "severity": severity, "risk": risk,
            })
        return {"id": fid, "risk_score": risk}

    def list(self, case_id):
        rows = self.db.fetchall(
            "SELECT * FROM findings WHERE case_id=? ORDER BY risk_score DESC",
            (case_id,),
        )
        out = []
        for r in rows:
            d = dict(r)
            d["details"] = json.loads(d.get("details") or "{}")
            out.append(d)
        return out

    def update_risk(self, finding_id, new_score):
        self.db.execute("UPDATE findings SET risk_score=? WHERE id=?",
                        (new_score, finding_id))
        if self.bus:
            self.bus.publish("finding.risk_updated",
                             {"id": finding_id, "risk": new_score})
