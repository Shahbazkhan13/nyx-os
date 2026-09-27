"""NyxOS Asset Engine (skeleton)"""
import sqlite3, json, time

class AssetEngine:
    def __init__(self, db_path):
        self.db = sqlite3.connect(db_path)
        self.db.row_factory = sqlite3.Row

    def add(self, case_id, atype, identifier, metadata=None):
        cur = self.db.cursor()
        cur.execute(
            "INSERT INTO assets(case_id,type,identifier,metadata) VALUES(?,?,?,?)",
            (case_id, atype, identifier, json.dumps(metadata or {}))
        )
        self.db.commit()
        return cur.lastrowid

    def list(self, case_id):
        cur = self.db.cursor()
        cur.execute("SELECT * FROM assets WHERE case_id=?", (case_id,))
        return [dict(r) for r in cur.fetchall()]
