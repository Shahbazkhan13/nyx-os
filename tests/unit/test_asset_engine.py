"""Unit tests for Asset Engine"""
import sys, os, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from core.assets.engine import AssetEngine

def test_add_and_list():
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    db = tmp.name
    tmp.close()
    with open(db, "w") as f:
        pass
    # Create tables first
    import sqlite3
    conn = sqlite3.connect(db)
    conn.executescript("""
        CREATE TABLE assets (
            id INTEGER PRIMARY KEY,
            case_id INTEGER,
            type TEXT,
            identifier TEXT,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()

    e = AssetEngine(db)
    e.add(1, "host", "192.168.1.1")
    assets = e.list(1)
    assert len(assets) == 1
    assert assets[0]["identifier"] == "192.168.1.1"
