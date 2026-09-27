"""NyxOS Core API — high-level facade over database + engines."""
import json
from datetime import datetime


class CoreAPI:
    def __init__(self, db, bus=None):
        self.db = db
        self.bus = bus

    # ---- Cases ----
    def case_create(self, params):
        name = params["name"]
        desc = params.get("description", "")
        cur = self.db.execute(
            "INSERT INTO cases(name, description) VALUES (?, ?)",
            (name, desc),
        )
        case_id = cur.lastrowid
        if self.bus:
            self.bus.publish("case.created", {"id": case_id, "name": name})
        return {"id": case_id, "name": name, "description": desc}

    def case_list(self, params=None):
        rows = self.db.fetchall("SELECT * FROM cases ORDER BY id DESC")
        return {"cases": [dict(r) for r in rows]}

    def case_get(self, params):
        row = self.db.fetchone("SELECT * FROM cases WHERE id=?", (params["id"],))
        if not row:
            raise ValueError(f"Case {params['id']} not found")
        return dict(row)

    # ---- Assets ----
    def asset_add(self, params):
        cur = self.db.execute(
            "INSERT INTO assets(case_id, type, identifier, metadata) VALUES (?, ?, ?, ?)",
            (params["case_id"], params["type"], params["identifier"],
             json.dumps(params.get("metadata", {}))),
        )
        asset_id = cur.lastrowid
        if self.bus:
            self.bus.publish("asset.created", {
                "id": asset_id,
                "case_id": params["case_id"],
                "type": params["type"],
                "identifier": params["identifier"],
            })
        return {"id": asset_id}

    def asset_list(self, params):
        rows = self.db.fetchall(
            "SELECT * FROM assets WHERE case_id=? ORDER BY id DESC",
            (params["case_id"],),
        )
        return {"assets": [dict(r) for r in rows]}

    # ---- Findings ----
    def finding_add(self, params):
        cur = self.db.execute(
            "INSERT INTO findings(case_id, asset_id, title, severity, details) "
            "VALUES (?, ?, ?, ?, ?)",
            (params["case_id"], params.get("asset_id"),
             params["title"], params.get("severity", "info"),
             json.dumps(params.get("details", {}))),
        )
        fid = cur.lastrowid
        if self.bus:
            self.bus.publish("finding.created", {"id": fid, "title": params["title"]})
        return {"id": fid}

    def finding_list(self, params):
        rows = self.db.fetchall(
            "SELECT * FROM findings WHERE case_id=? ORDER BY id DESC",
            (params["case_id"],),
        )
        return {"findings": [dict(r) for r in rows]}

    # ---- Health ----
    def ping(self, params=None):
        return {"status": "ok", "service": "nyxos-core"}
