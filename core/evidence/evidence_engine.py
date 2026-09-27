"""NyxOS Evidence Engine — capture, hash, attach evidence to findings."""
import hashlib
from datetime import datetime


class EvidenceEngine:
    def __init__(self, db, bus=None):
        self.db = db
        self.bus = bus

    def add(self, finding_id, evidence_type, content):
        h = hashlib.sha256(content.encode("utf-8", errors="ignore")).hexdigest()
        cur = self.db.execute(
            "INSERT INTO evidence(finding_id, type, content, hash) VALUES (?, ?, ?, ?)",
            (finding_id, evidence_type, content, h),
        )
        eid = cur.lastrowid
        if self.bus:
            self.bus.publish("evidence.added", {
                "id": eid, "finding_id": finding_id,
                "type": evidence_type, "hash": h,
            })
        return {"id": eid, "hash": h}

    def list(self, finding_id):
        rows = self.db.fetchall(
            "SELECT * FROM evidence WHERE finding_id=? ORDER BY id DESC",
            (finding_id,),
        )
        return [dict(r) for r in rows]

    def verify(self, evidence_id):
        row = self.db.fetchone("SELECT * FROM evidence WHERE id=?", (evidence_id,))
        if not row:
            return {"valid": False, "reason": "not found"}
        expected = row["hash"]
        actual = hashlib.sha256(row["content"].encode("utf-8", errors="ignore")).hexdigest()
        return {"valid": expected == actual, "expected": expected, "actual": actual}
