"""NyxOS Finding Engine (skeleton)"""
import sqlite3, json

class FindingEngine:
    def __init__(self, db_path):
        self.db = sqlite3.connect(db_path)

    def add(self, case_id, asset_id, title, severity, details=None):
        cur = self.db.cursor()
        cur.execute(
            "INSERT INTO findings(case_id,asset_id,title,severity,details) VALUES(?,?,?,?,?)",
            (case_id, asset_id, title, severity, json.dumps(details or {}))
        )
        self.db.commit()
        return cur.lastrowid
