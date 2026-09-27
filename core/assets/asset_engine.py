"""NyxOS Asset Engine — manage assets + relationships."""
import json
from core.models.entities import Asset


class AssetEngine:
    def __init__(self, db, bus=None):
        self.db = db
        self.bus = bus

    def add(self, case_id, asset_type, identifier, metadata=None):
        cur = self.db.execute(
            "INSERT INTO assets(case_id, type, identifier, metadata) VALUES (?, ?, ?, ?)",
            (case_id, asset_type, identifier, json.dumps(metadata or {})),
        )
        aid = cur.lastrowid
        if self.bus:
            self.bus.publish("asset.created", {
                "id": aid, "case_id": case_id,
                "type": asset_type, "identifier": identifier,
            })
        return aid

    def get(self, asset_id):
        row = self.db.fetchone("SELECT * FROM assets WHERE id=?", (asset_id,))
        if not row:
            return None
        d = dict(row)
        d["metadata"] = json.loads(d.get("metadata") or "{}")
        return d

    def list(self, case_id):
        rows = self.db.fetchall(
            "SELECT * FROM assets WHERE case_id=? ORDER BY id DESC",
            (case_id,),
        )
        out = []
        for r in rows:
            d = dict(r)
            d["metadata"] = json.loads(d.get("metadata") or "{}")
            out.append(d)
        return out

    def find_by_identifier(self, case_id, identifier):
        row = self.db.fetchone(
            "SELECT * FROM assets WHERE case_id=? AND identifier=?",
            (case_id, identifier),
        )
        return dict(row) if row else None

    def delete(self, asset_id):
        self.db.execute("DELETE FROM assets WHERE id=?", (asset_id,))
        if self.bus:
            self.bus.publish("asset.deleted", {"id": asset_id})
