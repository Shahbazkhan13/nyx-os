"""NyxOS Evidence Engine (skeleton)"""
import sqlite3, hashlib, time

class EvidenceEngine:
    def __init__(self, db_path):
        self.db = sqlite3.connect(db_path)

    def add(self, finding_id, etype, content):
        h = hashlib.sha256(content.encode()).hexdigest()
        cur = self.db.cursor()
        cur.execute(
            "INSERT INTO evidence(finding_id,type,content,hash) VALUES(?,?,?,?)",
            (finding_id, etype, content, h)
        )
        self.db.commit()
        return cur.lastrowid
